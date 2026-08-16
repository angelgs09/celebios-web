// Genera aula/vendor/supabase-js-<version>.js desde node_modules.
//
// POR QUE NO SE BAJA DE UN CDN
//
// El primer intento fue traer el bundle ya hecho de esm.sh. Parecia
// autocontenido, pero sus dos primeras lineas eran:
//
//   import __Process$ from "/node/process.mjs";
//   import { Buffer as __Buffer$ } from "/node/buffer.mjs";
//
// Rutas ABSOLUTAS que solo existen en esm.sh. Servido desde nuestro dominio dan
// 404, el modulo no evalua, y el alumno ve una pagina en blanco: exactamente el
// fallo que quisimos quitar al dejar el CDN. (jsDelivr tampoco sirve: su "+esm"
// reparte el paquete en cinco modulos que tambien apuntan a su host.)
//
// Empaquetar aqui con platform=browser resuelve las dos cosas: nada de globals
// de Node, y ninguna ruta que dependa de un servidor ajeno.
//
//   node scripts/empaquetar-supabase.mjs
//
// Al terminar hay que actualizar el import en aula/index.html y aula/admin.html
// si cambio la version. El test test_supabase_js_se_sirve_local_y_con_version_fija
// no deja que se olvide.

import { build } from 'esbuild'
import { readFileSync, writeFileSync, readdirSync, unlinkSync } from 'fs'
import { join } from 'path'

const RAIZ = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')
const VERSION = JSON.parse(readFileSync(join(RAIZ, 'node_modules/@supabase/supabase-js/package.json'))).version
const SALIDA = join(RAIZ, 'aula/vendor', `supabase-js-${VERSION}.js`)

for (const f of readdirSync(join(RAIZ, 'aula/vendor'))) {
  if (f.startsWith('supabase-js-') && f !== `supabase-js-${VERSION}.js`) {
    unlinkSync(join(RAIZ, 'aula/vendor', f))
    console.log('quitado el anterior:', f)
  }
}

await build({
  stdin: {
    contents: "export { createClient } from '@supabase/supabase-js'",
    resolveDir: RAIZ,
    sourcefile: 'entrada-aula.js',
  },
  bundle: true,
  format: 'esm',
  platform: 'browser',   // sin globals de Node: nada de process ni Buffer
  target: 'es2022',
  minify: true,
  legalComments: 'none',
  outfile: SALIDA,
})

const js = readFileSync(SALIDA, 'utf8')

// El chequeo que fallo la primera vez: buscar `from"x"` sin contemplar el
// espacio dejo pasar `from "/node/process.mjs"` y con el la pagina en blanco.
const fuera = [...js.matchAll(/\bfrom\s*["']([^"']+)["']|\bimport\s*\(\s*["']([^"']+)["']/g)]
  .map(m => m[1] || m[2])
if (fuera.length) {
  console.error('SIGUE DEPENDIENDO DE ALGO DE FUERA:', fuera)
  process.exit(1)
}
if (!/\bcreateClient\b/.test(js)) {
  console.error('el bundle no exporta createClient')
  process.exit(1)
}

console.log(`${SALIDA}  ${(js.length / 1024).toFixed(0)} KB  sin dependencias externas`)
