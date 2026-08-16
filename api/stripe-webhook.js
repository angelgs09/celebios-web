// Cuando Stripe confirma un pago, inscribe al alumno en el aula y le manda su
// liga de acceso. Es el paso que hoy hace una persona a mano.
//
// LA FIRMA SE VERIFICA SIEMPRE
//
// Esta URL es publica: cualquiera puede mandarle un POST diciendo "fulano pago"
// y quedaria inscrito gratis. Lo unico que separa un pago real de uno inventado
// es la firma HMAC que Stripe pone en la cabecera stripe-signature, calculada
// con un secreto que solo tienen Stripe y nosotros. Sin STRIPE_WEBHOOK_SECRET
// configurado, esta funcion NO acepta nada: prefiere rechazar pagos buenos a
// regalar cursos.
//
// La comparacion va en tiempo constante y con ventana de tiempo, que es lo que
// evita que alguien reenvie un evento viejo o adivine la firma byte por byte.

import { createHmac, timingSafeEqual } from 'node:crypto'

const SUPABASE = 'https://lwawpdjsfjvlyvqwqiqp.supabase.co'
const TOLERANCIA_S = 300   // 5 min, el mismo margen que usa Stripe

export async function POST (request) {
  const secreto = process.env.STRIPE_WEBHOOK_SECRET
  const servicio = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!secreto || !servicio) return texto('webhook no configurado', 503)

  const firma = request.headers.get('stripe-signature') || ''
  const crudo = await request.text()

  const v = verificarFirma(crudo, firma, secreto)
  if (!v.ok) {
    console.error('firma de stripe rechazada:', v.razon)
    return texto('firma invalida', 400)
  }

  let evento
  try { evento = JSON.parse(crudo) } catch { return texto('json invalido', 400) }

  // Solo importa el pago completado. Los demas eventos se contestan 200 para
  // que Stripe no los reintente en bucle.
  if (evento.type !== 'checkout.session.completed') return texto('ignorado', 200)

  const s = evento.data?.object || {}
  if (s.payment_status !== 'paid') return texto('sesion sin pago', 200)

  const correo = (s.metadata?.correo || s.customer_details?.email || '').trim().toLowerCase()
  const cursoId = s.metadata?.curso_id
  const intent = typeof s.payment_intent === 'string' ? s.payment_intent : s.payment_intent?.id
  if (!correo || !cursoId) return texto('faltan datos en el evento', 200)

  const H = {
    apikey: servicio,
    Authorization: `Bearer ${servicio}`,
    'Content-Type': 'application/json',
  }

  try {
    // 1. El usuario. Si ya existe (recompra, o compro otro curso antes), se
    //    reutiliza en vez de tronar.
    let alumnoId = await buscarUsuario(correo, H)
    if (!alumnoId) alumnoId = await crearUsuario(correo, H)
    if (!alumnoId) return texto('no se pudo crear el usuario', 500)

    // 2. La inscripcion. stripe_payment_intent es UNIQUE en la tabla, asi que
    //    si Stripe reintenta el mismo evento -- y lo hace -- la segunda vez
    //    choca con la restriccion y no se duplica nada.
    const ins = await fetch(`${SUPABASE}/rest/v1/inscripciones`, {
      method: 'POST',
      headers: { ...H, Prefer: 'return=representation' },
      body: JSON.stringify({
        alumno_id: alumnoId,
        curso_id: cursoId,
        estado: 'activa',
        origen: 'stripe',
        monto_mxn: Math.round((s.amount_total || 0) / 100),
        stripe_payment_intent: intent || null,
      }),
    })

    if (!ins.ok) {
      const d = await ins.text()
      // 23505 = clave duplicada. O ya estaba inscrito, o es un reintento de
      // Stripe. En los dos casos el trabajo ya esta hecho.
      if (d.includes('23505')) return texto('ya estaba inscrito', 200)
      console.error('no se pudo inscribir:', ins.status, d.slice(0, 300))
      return texto('no se pudo inscribir', 500)
    }

    // 3. Su liga de acceso, por el mismo camino que usa el aula.
    await fetch(`${SUPABASE}/auth/v1/otp`, {
      method: 'POST',
      headers: { apikey: servicio, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: correo,
        create_user: false,
        options: { email_redirect_to: 'https://celebios.vercel.app/aula' },
      }),
    })

    return texto('inscrito', 200)
  } catch (e) {
    console.error('webhook reventó:', e?.message)
    // 500 para que Stripe reintente: el dinero ya entro y el alumno TIENE que
    // quedar inscrito.
    return texto('error interno', 500)
  }
}

// --------------------------------------------------------------------------

function verificarFirma (cuerpo, cabecera, secreto) {
  const partes = Object.fromEntries(
    cabecera.split(',').map(p => p.split('=')).filter(p => p.length === 2)
  )
  const t = partes.t
  const recibida = partes.v1
  if (!t || !recibida) return { ok: false, razon: 'cabecera incompleta' }

  const edad = Math.abs(Math.floor(Date.now() / 1000) - Number(t))
  if (!Number.isFinite(edad) || edad > TOLERANCIA_S) {
    return { ok: false, razon: `fuera de ventana (${edad}s)` }
  }

  const esperada = createHmac('sha256', secreto).update(`${t}.${cuerpo}`).digest('hex')
  const a = Buffer.from(esperada, 'utf8')
  const b = Buffer.from(recibida, 'utf8')
  // timingSafeEqual truena si difieren en longitud; se compara antes para no
  // filtrar por la excepcion cuanto se parecia la firma.
  if (a.length !== b.length) return { ok: false, razon: 'longitud distinta' }
  if (!timingSafeEqual(a, b)) return { ok: false, razon: 'no coincide' }
  return { ok: true }
}

async function buscarUsuario (correo, H) {
  const r = await fetch(
    `${SUPABASE}/rest/v1/perfiles?correo=eq.${encodeURIComponent(correo)}&select=id`,
    { headers: H }
  )
  if (!r.ok) return null
  const filas = await r.json()
  return filas[0]?.id || null
}

async function crearUsuario (correo, H) {
  const r = await fetch(`${SUPABASE}/auth/v1/admin/users`, {
    method: 'POST',
    headers: H,
    body: JSON.stringify({ email: correo, email_confirm: true }),
  })
  if (!r.ok) {
    console.error('no se pudo crear el usuario:', r.status, (await r.text()).slice(0, 200))
    return null
  }
  return (await r.json())?.id || null
}

function texto (mensaje, status) {
  return new Response(mensaje, { status, headers: { 'cache-control': 'no-store' } })
}
