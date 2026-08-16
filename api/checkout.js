// Abre el cobro de un curso con Stripe y devuelve la URL de pago.
//
// POR QUE EXISTE
//
// Los botones "Inscribirme" del sitio apuntaban a celebios.online, o sea a
// Kajabi. Cada venta entraba a la plataforma de la que nos estamos yendo, el
// alumno quedaba dado de alta ALLA y alguien tenia que pasarlo a mano al aula.
// Ademas se pagan dos plataformas para vender una vez.
//
// La cuenta de Stripe ya existe y ya cobra: es la que Kajabi tiene conectada
// (se ve en su checkout, en vivo y en pesos). Aqui se usa la misma, sin dar de
// alta nada nuevo, y de paso se abre la puerta a MSI, SPEI y OXXO, que Stripe
// Mexico si maneja y PayPal cobraba al 4%.
//
// El precio NO se escribe aqui. Sale de cursos.precio_mxn, que es lo mismo que
// muestra la pagina. Un precio hardcodeado en el checkout es la forma mas facil
// de cobrar de menos por un curso que subio.

const SUPABASE = 'https://lwawpdjsfjvlyvqwqiqp.supabase.co'
const SITIO = 'https://celebios.vercel.app'
const SLUG = /^[a-z0-9-]{3,60}$/

export async function POST (request) {
  const clave = process.env.STRIPE_SECRET_KEY
  const servicio = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!clave || !servicio) return json({ error: 'cobro no configurado' }, 503)

  let cuerpo
  try { cuerpo = await request.json() } catch { return json({ error: 'cuerpo invalido' }, 400) }

  const slug = String(cuerpo?.curso || '')
  // Validar la forma antes de salir a la red, igual que en video.js: sin esto
  // cualquiera gasta una invocacion y una consulta con solo mandar basura.
  if (!SLUG.test(slug)) return json({ error: 'curso no valido' }, 400)

  // El correo se pide aqui y no en Stripe para que el alumno lo vea prellenado
  // y, sobre todo, para que el webhook sepa a quien inscribir aunque Stripe
  // devuelva el evento sin datos de cliente.
  const correo = String(cuerpo?.correo || '').trim().toLowerCase()
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(correo)) {
    return json({ error: 'hace falta un correo valido' }, 400)
  }

  const r = await fetch(
    `${SUPABASE}/rest/v1/cursos?slug=eq.${encodeURIComponent(slug)}&select=id,titulo,precio_mxn`,
    { headers: { apikey: servicio, Authorization: `Bearer ${servicio}` } }
  )
  if (!r.ok) return json({ error: 'no se pudo leer el curso' }, 502)
  const [curso] = await r.json()
  if (!curso) return json({ error: 'ese curso no existe' }, 404)
  if (!curso.precio_mxn || curso.precio_mxn <= 0) {
    return json({ error: 'ese curso no tiene precio para venta en linea' }, 409)
  }

  // Stripe cuenta en centavos. precio_mxn es un entero de pesos.
  const centavos = Math.round(curso.precio_mxn * 100)

  const params = new URLSearchParams({
    mode: 'payment',
    customer_email: correo,
    // Vuelve al aula: ahi el alumno pide su liga con el mismo correo que pago.
    success_url: `${SITIO}/aula?pago=ok`,
    cancel_url: `${SITIO}/${slug}?pago=cancelado`,
    'line_items[0][quantity]': '1',
    'line_items[0][price_data][currency]': 'mxn',
    'line_items[0][price_data][unit_amount]': String(centavos),
    'line_items[0][price_data][product_data][name]': curso.titulo,
    // El webhook necesita saber QUE se compro y PARA QUIEN. El correo del
    // formulario manda sobre el de Stripe: es el que el alumno escribio.
    'metadata[curso_id]': curso.id,
    'metadata[curso_slug]': slug,
    'metadata[correo]': correo,
    'payment_intent_data[metadata][curso_id]': curso.id,
    'payment_intent_data[metadata][correo]': correo,
  })

  const s = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${clave}`,
      'Content-Type': 'application/x-www-form-urlencoded',
      // Sin esto, dos clics seguidos abren dos sesiones de pago y el alumno
      // puede terminar pagando dos veces el mismo curso.
      'Idempotency-Key': `${slug}:${correo}:${new Date().toISOString().slice(0, 13)}`,
    },
    body: params,
  })

  if (!s.ok) {
    const detalle = await s.text()
    console.error('stripe checkout falló:', s.status, detalle.slice(0, 300))
    return json({ error: 'no se pudo abrir el cobro' }, 502)
  }

  const sesion = await s.json()
  return json({ url: sesion.url })
}

function json (cuerpo, status = 200) {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  })
}
