// Sube los once videos del curso a Vercel Blob, en privado.
//
// Privado, no publico: `api/video.js` firma una URL temporal por alumno y por
// leccion, y quien decide si firma es el RLS de Supabase. Un blob publico haria
// inutil toda esa cadena -- bastaria con que alguien pasara la URL.
//
// Lo que se guarda en `lecciones.video_url` es el PATHNAME, no la URL: la
// funcion lo vuelve a firmar en cada reproduccion.
//
// Idempotente: `addRandomSuffix: false` mas un pathname estable significa que
// volver a correrlo sobreescribe el mismo objeto en vez de duplicar 1.2 GB.
//
//   node scripts/subir-videos.mjs [--dir <carpeta>] [--solo 3]
//
// Lee BLOB_READ_WRITE_TOKEN de .env.production.local (traido con `vercel env
// pull`). No lo imprime nunca.

import { put, list } from '@vercel/blob'
import { createReadStream, existsSync, readFileSync, statSync } from 'node:fs'
import { readdir } from 'node:fs/promises'
import path from 'node:path'

const RAIZ = path.resolve(import.meta.dirname, '..')
const CURSO = 'curso-lenguaje-felino'

function cargarToken () {
  const f = path.join(RAIZ, '.env.production.local')
  if (!existsSync(f)) {
    throw new Error('falta .env.production.local — corre: vercel env pull .env.production.local --environment production')
  }
  for (const linea of readFileSync(f, 'utf8').split('\n')) {
    const m = linea.match(/^BLOB_READ_WRITE_TOKEN="?([^"\r\n]+)"?/)
    if (m) return m[1]
  }
  throw new Error('el archivo no trae BLOB_READ_WRITE_TOKEN')
}

const args = process.argv.slice(2)
const valor = (bandera) => {
  const i = args.indexOf(bandera)
  return i === -1 ? null : args[i + 1]
}

// Este default APUNTA A DONDE ESCRIBE comprimir-videos.ps1, y tiene que seguir
// haciendolo. Antes apuntaba a CELEBIOS-web/videos, que es donde viven los
// cortes en CRUDO: correr el script sin --dir comparaba bytes contra esos,
// imprimia "ya esta arriba, se salta" en los once y no subia nada, sin un solo
// error en pantalla. Es el mismo accidente que obligo a cerrar el aula.
const dir = valor('--dir') || 'C:/Users/coche/Desktop/CELEBIOS-videos/web'
const solo = valor('--solo') ? Number(valor('--solo')) : null
const token = cargarToken()

const archivos = (await readdir(dir))
  .filter(n => /^modulo-\d+\.mp4$/i.test(n))
  .sort()
  .map(n => ({ nombre: n, numero: Number(n.match(/\d+/)[0]), ruta: path.join(dir, n) }))
  .filter(a => solo === null || a.numero === solo)

if (!archivos.length) throw new Error(`no hay modulo-NN.mp4 en ${dir}`)

const yaSubidos = new Map()
try {
  const { blobs } = await list({ token, prefix: `${CURSO}/` })
  for (const b of blobs) yaSubidos.set(b.pathname, b.size)
} catch { /* store vacio la primera vez */ }

const total = archivos.reduce((n, a) => n + statSync(a.ruta).size, 0)
console.log(`${archivos.length} archivos · ${(total / 1e9).toFixed(2)} GB · destino ${CURSO}/`)

const hechos = []
for (const a of archivos) {
  const bytes = statSync(a.ruta).size
  const pathname = `${CURSO}/modulo-${String(a.numero).padStart(2, '0')}.mp4`

  if (yaSubidos.get(pathname) === bytes) {
    console.log(`  = ${pathname} ya esta arriba con el mismo tamano, se salta`)
    hechos.push({ numero: a.numero, pathname, bytes, subido: false })
    continue
  }

  const t0 = Date.now()
  process.stdout.write(`  ↑ ${pathname} (${(bytes / 1e6).toFixed(0)} MB) `)
  const res = await put(pathname, createReadStream(a.ruta), {
    access: 'private',
    token,
    contentType: 'video/mp4',
    addRandomSuffix: false,
    allowOverwrite: true,
    multipart: true
  })
  const seg = (Date.now() - t0) / 1000
  console.log(`ok en ${seg.toFixed(0)}s (${(bytes / 1e6 / seg).toFixed(1)} MB/s)`)
  hechos.push({ numero: a.numero, pathname: res.pathname, bytes, subido: true })
}

console.log('\nSQL para dejar las lecciones apuntando a su video:\n')
for (const h of hechos) {
  console.log(
    `update lecciones set video_url = '${h.pathname}' ` +
    `where numero = ${h.numero} and curso_id = (select id from cursos where slug = '${CURSO}');`
  )
}
