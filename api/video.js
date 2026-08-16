// Firma una URL temporal para el video de una leccion.
//
// La autorizacion NO se reimplementa aqui. Esta funcion le pide la leccion a
// Supabase usando el token del propio alumno, asi que quien decide es el RLS:
// si no esta inscrito, o su inscripcion vencio a los 5 meses, Supabase no
// devuelve la fila y aqui no se firma nada. Una sola fuente de verdad.
//
// El video NO pasa por esta funcion: se devuelve una URL firmada y el navegador
// la descarga directo del CDN de Blob. Proxear el video por una serverless
// function costaria caro y no cachearia.

import { issueSignedToken, presignUrl } from '@vercel/blob'

const SUPABASE = 'https://lwawpdjsfjvlyvqwqiqp.supabase.co'
const ANON = 'sb_publishable_ERuFbuD18eSA27_ggnnIVQ_49iNxV89'
// 90 min: la leccion mas larga dura 69. Las 2 h de antes regalaban 50 minutos de
// ventana que no compraban nada, y la URL firmada es una credencial al portador
// -- quien la reciba baja el video mientras viva. Si caduca a media clase, el
// listener de 'error' del reproductor pide una firma nueva.
const VIGENCIA_MS = 90 * 60 * 1000
// El firmador solo debe firmar videos de curso, no cualquier objeto del store.
const PREFIJO_PERMITIDO = 'curso-'
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export async function GET (request) {
  const url = new URL(request.url)
  const leccion = url.searchParams.get('leccion')
  const auth = request.headers.get('authorization') || ''

  if (!leccion) return json({ error: 'falta el parametro leccion' }, 400)
  // Validar la forma ANTES de salir a la red: sin esto, cualquiera sin cuenta
  // gastaba una invocacion de funcion mas una peticion a Supabase por cada
  // request con solo mandar 'Bearer loquesea'. Ahora el trafico de basura muere
  // aqui, sin tocar la base.
  if (!UUID.test(leccion)) return json({ error: 'leccion no valida' }, 400)
  if (!auth.startsWith('Bearer ')) return json({ error: 'falta la sesion' }, 401)

  // RLS decide. Con el token del alumno, esta consulta devuelve la leccion solo
  // si esta inscrito y vigente.
  const r = await fetch(
    `${SUPABASE}/rest/v1/lecciones?id=eq.${encodeURIComponent(leccion)}&select=video_url`,
    { headers: { apikey: ANON, Authorization: auth } }
  )
  // Un token vencido o invalido es culpa del cliente, no del servidor: PostgREST
  // contesta 401 y devolverlo como 502 mandaba al alumno el mensaje generico de
  // "no pudimos cargar el video" cuando lo que tenia que hacer era volver a
  // entrar.
  //
  // SOLO el 401. El 403 de PostgREST es su respuesta a insufficient_privilege,
  // o sea a un grant faltante: taparlo como "tu sesion expiro" haria que el dia
  // que alguien toque un permiso, los 21 alumnos salgan y vuelvan a entrar en
  // vano y no quede en los logs un solo 502 apuntando a la base.
  if (r.status === 401) {
    return json({ error: 'tu sesion expiro, vuelve a entrar' }, 401)
  }
  if (!r.ok) return json({ error: 'no se pudo verificar el acceso' }, 502)

  const filas = await r.json()
  if (!filas.length) return json({ error: 'sin acceso a esta leccion' }, 403)

  const ruta = filas[0].video_url
  if (!ruta) return json({ error: 'esta leccion todavia no tiene video' }, 404)
  // Si algun dia una leccion apunta a un video externo, se deja pasar tal cual.
  if (/^https?:\/\//.test(ruta)) return json({ url: ruta })
  // video_url la escribe un admin desde el navegador. Sin este cerco, poner ahi
  // la ruta de cualquier otro objeto del store convertia a esta funcion en un
  // firmador de proposito general en lugar de un firmador de videos de leccion.
  if (!ruta.startsWith(PREFIJO_PERMITIDO)) {
    return json({ error: 'ruta de video no valida' }, 500)
  }

  const validUntil = Date.now() + VIGENCIA_MS
  const token = await issueSignedToken({
    pathname: ruta, operations: ['get'], validUntil
  })
  const { presignedUrl } = await presignUrl(token, {
    operation: 'get', pathname: ruta, access: 'private', validUntil
  })

  return json({ url: presignedUrl, expira: new Date(validUntil).toISOString() })
}

function json (cuerpo, status = 200) {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: {
      'content-type': 'application/json',
      // La URL firmada es de un solo alumno y caduca: que no la guarde nadie.
      'cache-control': 'private, no-store'
    }
  })
}
