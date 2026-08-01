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
const VIGENCIA_MS = 2 * 60 * 60 * 1000 // 2 h: mas que cualquier leccion (la mas larga dura 1:09)

export async function GET (request) {
  const url = new URL(request.url)
  const leccion = url.searchParams.get('leccion')
  const auth = request.headers.get('authorization') || ''

  if (!leccion) return json({ error: 'falta el parametro leccion' }, 400)
  if (!auth.startsWith('Bearer ')) return json({ error: 'falta la sesion' }, 401)

  // RLS decide. Con el token del alumno, esta consulta devuelve la leccion solo
  // si esta inscrito y vigente.
  const r = await fetch(
    `${SUPABASE}/rest/v1/lecciones?id=eq.${encodeURIComponent(leccion)}&select=video_url`,
    { headers: { apikey: ANON, Authorization: auth } }
  )
  if (!r.ok) return json({ error: 'no se pudo verificar el acceso' }, 502)

  const filas = await r.json()
  if (!filas.length) return json({ error: 'sin acceso a esta leccion' }, 403)

  const ruta = filas[0].video_url
  if (!ruta) return json({ error: 'esta leccion todavia no tiene video' }, 404)
  // Si algun dia una leccion apunta a un video externo, se deja pasar tal cual.
  if (/^https?:\/\//.test(ruta)) return json({ url: ruta })

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
