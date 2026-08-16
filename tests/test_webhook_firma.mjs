// La firma del webhook de Stripe es lo unico que impide que cualquiera se
// inscriba gratis mandando un POST. Se prueba sin cuenta de Stripe: la firma es
// un HMAC-SHA256 sobre "<timestamp>.<cuerpo>" y se puede fabricar aqui.
//
//   node tests/test_webhook_firma.mjs

import { createHmac } from 'node:crypto'
import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'

const SECRETO = 'whsec_prueba_no_es_real'
const fuente = readFileSync(new URL('../api/stripe-webhook.js', import.meta.url), 'utf8')

// Se extrae la funcion del archivo real para probar LO QUE SE DESPLIEGA, no una
// copia que puede quedarse atras.
const ini = fuente.indexOf('function verificarFirma')
const fin = fuente.indexOf('async function buscarUsuario')
assert.ok(ini > 0 && fin > ini, 'no encontre verificarFirma en api/stripe-webhook.js')
const { verificarFirma } = await import(
  'data:text/javascript,' + encodeURIComponent(
    "import { createHmac, timingSafeEqual } from 'node:crypto'\n" +
    'const TOLERANCIA_S = 300\n' +
    'export ' + fuente.slice(ini, fin)
  )
)

const cuerpo = JSON.stringify({ type: 'checkout.session.completed', data: { object: { id: 'cs_1' } } })
const ahora = Math.floor(Date.now() / 1000)
const firmar = (t, c, s = SECRETO) => createHmac('sha256', s).update(`${t}.${c}`).digest('hex')

let pasadas = 0
const caso = (nombre, esperado, cabecera, cuerpoUsado = cuerpo) => {
  const r = verificarFirma(cuerpoUsado, cabecera, SECRETO)
  assert.equal(r.ok, esperado, `${nombre}: esperaba ok=${esperado}, dio ${r.ok} (${r.razon || ''})`)
  console.log(`  ok  ${nombre}`)
  pasadas++
}

caso('firma buena pasa', true, `t=${ahora},v1=${firmar(ahora, cuerpo)}`)

// Lo que tiene que rebotar
caso('sin cabecera', false, '')
caso('sin v1', false, `t=${ahora}`)
caso('firma inventada', false, `t=${ahora},v1=${'a'.repeat(64)}`)
caso('firmada con otro secreto', false, `t=${ahora},v1=${firmar(ahora, cuerpo, 'whsec_otro')}`)
caso('cuerpo alterado despues de firmar', false, `t=${ahora},v1=${firmar(ahora, cuerpo)}`,
     cuerpo.replace('cs_1', 'cs_HACKEADO'))
caso('evento viejo, reenviado 10 min despues', false,
     `t=${ahora - 600},v1=${firmar(ahora - 600, cuerpo)}`)
caso('timestamp del futuro lejano', false,
     `t=${ahora + 3600},v1=${firmar(ahora + 3600, cuerpo)}`)
caso('timestamp que no es numero', false, `t=maniana,v1=${firmar(ahora, cuerpo)}`)
caso('firma mas corta', false, `t=${ahora},v1=abc`)

// El borde de la ventana si tiene que pasar: un webhook tarda segundos.
caso('4 minutos de retraso todavia pasa', true,
     `t=${ahora - 240},v1=${firmar(ahora - 240, cuerpo)}`)

console.log(`\n${pasadas} casos, todos correctos`)
