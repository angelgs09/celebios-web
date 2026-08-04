# PROMPT para Claude Design — CELEBIOS, 4 de agosto de 2026

Pega el bloque de abajo en claude.ai/design, con el repo `angelgs09/celebios-web`
conectado al proyecto.

**Antes de pegar:** conecta el repo y adjunta a mano las 9 capturas de
`docs/design/capturas/` como respaldo. No está verificado que Claude Design lea
imágenes desde el repo, y el prompt está escrito para detectarlo en el primer turno.

---

## ▼ COPIAR DESDE AQUÍ ▼

Vas a rediseñar el sistema visual de CELEBIOS, una academia latinoamericana de
educación continua en fauna silvestre para médicos veterinarios y biólogos.

El contexto completo está en el repo conectado:
**`docs/design/BRIEF-claude-design-2026-08-04.md`** (rama `codex/celebios-redesign-total`).
Léelo entero antes de proponer nada. El sitio en vivo, para revisión, está en
https://celebios.vercel.app

**Primer turno, antes de diseñar — tres cosas:**

1. Describe qué ves en `docs/design/capturas/01-home-desktop.png` y en
   `07-catalogo-movil.png`. **Si no puedes ver esas imágenes, dímelo explícitamente**
   en vez de suponer su contenido; te las adjunto a mano.
2. Dime tu lectura del encargo en una línea ("leo esto como…").
3. Dime qué te parece más débil del diseño actual, con tus palabras, antes de leer
   mi diagnóstico de la sección 4 del brief.

**El encargo:** el sistema visual se rediseña trabajando sobre cuatro páginas —
home (`/`), catálogo (`/cursos`), ficha de curso (`/curso-lenguaje-felino`) y
diplomado (`/diplomado-rescate-rehabilitacion-fauna`). Lo que salga de ahí se
propaga después a las 33 páginas del sitio.

La dirección actual se llama **"Lámina Viva"**: el sitio como atlas naturalista
latinoamericano, cada programa como una lámina numerada de un atlas de campo. La
tesis me sigue gustando; la ejecución se quedó a medias. Puedes profundizarla o
proponer romperla, pero si la rompes, defiéndelo.

**Los cinco problemas que tienes que resolver:**

- **Solo un programa de diecinueve se puede comprar hoy**: un curso pregrabado de
  12 horas y $1,400 MXN. Los otros dieciocho no tienen convocatoria ni precio,
  incluido el diplomado de 170 horas que ancla la marca. El catálogo son 19 cajas
  casi idénticas en cuatro columnas, y la única diferencia entre la que se vende y
  las que no es una píldora de color. Lo comprable tiene que ganar sin esconder al
  resto, que es el argumento de que esto es una academia con recorrido.
- El sitio casi no tiene imágenes: la home tiene una sola foto y el catálogo
  ninguna. Diecinueve tarjetas de puro texto.
- La home alterna fondo marino y fondo papel siete veces. Lee como acordeón, no
  como jerarquía.
- El hero tiene siete elementos de texto compitiendo por el momento de mayor
  atención del sitio.
- Las nueve fichas de programas sin convocatoria son fichas de venta con el botón
  apagado. La del diplomado mide 18,000 px de alto en móvil: veintiuna pantallas
  de scroll para algo que no está a la venta. Necesitan ser otra cosa —algo que
  convenza y capte lista de espera sin fingir disponibilidad.

**Reglas duras. Ganan sobre cualquier preferencia estética:**

- **HTML de un archivo con CSS vanilla.** Nada de React, Tailwind, JSX ni build. Lo
  que entregues se porta a mano a un `<style>` inline. Tailwind hace el trabajo
  inportable.
- **No generes imágenes de ningún tipo** — ni fotos de fauna, ni de alumnos, ni de
  instalaciones, ni placeholders tipo picsum o unsplash. En el sitio de una academia
  con aval profesional, una foto generada se lee como evidencia de algo que ocurrió.
  Si una sección necesita una imagen que no existe, deja el hueco marcado y dímelo.
  Las únicas imágenes disponibles son las 13 de `redesign-v2/media/`.
- **No inventes ningún dato.** Ni cifras de egresados, ni fechas, ni nombres de
  docentes, ni testimonios, ni porcentajes. El sitio tiene ~110 marcadores "por
  confirmar" justamente porque esos datos todavía no existen. Si necesitas un número
  para que la composición funcione, escribe `[por confirmar]`.
- **Un solo precio en todo el sitio ($1,400 MXN, el curso de gatos) y ninguna fecha
  de apertura**, ni siquiera marcada "por confirmar". No es una preferencia
  estética: en agosto de 2026 se retiraron siete precios publicados —dos de ellos
  inventados en una ronda de diseño anterior— y dos fechas de apertura de programas
  cuya edición ya había cerrado. Si tu composición necesita una tabla de precios o
  una cuenta regresiva, no la tiene.
- **La paleta sale del logo real, no de tu gusto:** marino `#14294F`, cian `#2FA8C9`,
  morado `#7A5797`, salvia `#6FB07A`, papel `#EEF2EC`, tinta `#16294C`. El cian marca
  disponible y acción; el morado, próxima edición; la salvia es acento de vida. Puedes
  reasignar el sistema si lo justificas, pero no traigas colores de fuera de la marca.
- **Las fuentes son Bricolage Grotesque (display), Instrument Sans (texto) y Space
  Grotesk (mono).** Están self-hosted. Cero serif — fue una decisión explícita. Cero
  `<link>` a Google Fonts: la política de seguridad del aula lo bloquea.
- **Accesibilidad AA verificada, no declarada.** Contraste real en las dos
  superficies, anillo de foco visible en ambas, cero scroll horizontal a 390 px
  (`minmax(0,1fr)`, no `1fr`), enlace de saltar al contenido. Hay 315 pruebas
  automáticas que rechazan el commit si esto se rompe.
- **Sin logos de terceros** (UNAM, UAEH, IFAW): el vínculo institucional no está
  confirmado por escrito.
- **Animación discreta y motivada.** Nada de scroll-hijack, secciones fijadas,
  marquesinas ni bucles infinitos. Si una animación no comunica jerarquía, estado o
  respuesta a una acción, va fuera.

**Qué sí puedes tocar libremente:** escala tipográfica y jerarquía, ritmo y densidad
de secciones, el sistema de superficies, la anatomía de la tarjeta de curso, la
composición del hero, el tratamiento de los estados de disponibilidad, tablas, FAQ,
footer, estados interactivos, el uso de la retícula y la barra de escala como
lenguaje gráfico, el espaciado.

**Qué espero, en este orden:**

1. Tus tres respuestas del primer turno (arriba). Para ahí y espera mi comentario.
2. **Dos o tres direcciones** para la home, cada una con su razón en dos líneas.
   No una sola propuesta.
3. Ya elegida una: las cuatro páginas en alta fidelidad, a 1440 px y a 390 px.
4. **Los tokens explícitos** — color, escala tipográfica, espaciado, radios, sombras —
   en una lista portable a CSS custom properties.
5. **Qué componente cambia y qué componente se queda**, para saber qué propagar a
   las otras 29 páginas.

Trabaja sección por sección y enséñame cada una antes de seguir. Prefiero cuatro
páginas resueltas de verdad que treinta y tres a medias.

## ▲ COPIAR HASTA AQUÍ ▲

---

## Auditoría de este prompt

Pasado por un round de revisión antes de entregarlo, según la regla firme del
28-jun-2026. Lo que se corrigió respecto del primer borrador:

| Hallazgo | Corrección |
|---|---|
| El borrador daba por hecho que el modelo ve las imágenes del repo. No está verificado. | Primer turno arranca pidiendo que describa dos capturas y que **diga si no las ve**. |
| Pedía las cuatro páginas de golpe. | Se partió en cuatro pasos con parada explícita después del primer turno. |
| No bloqueaba la generación de imágenes, que es el reflejo por defecto de todo skill de diseño premium (picsum, unsplash, image-gen). | Prohibición explícita **con la razón** — en una academia, una foto generada se lee como evidencia. |
| No bloqueaba Tailwind/React, que es el stack por defecto de esos mismos skills. | Prohibido, con la razón (el resultado se porta a mano a CSS vanilla). |
| Pedía "mejora el diseño" sin nombrar los defectos. | Los cuatro problemas concretos, verificados mirando las capturas de hoy. |
| No prevenía la invención de datos, y el sitio tiene ~110 huecos abiertos. | Regla explícita + instrucción de escribir `[por confirmar]`. |
| Dejaba abierta la puerta a motion pesado (scroll-hijack, sticky-stack, marquesinas), que es lo que proponen los skills de taste instalados. | Prohibido, con el criterio de qué justifica una animación. |
| Preguntaba el diagnóstico después de dar el mío, contaminando la respuesta. | Se le pide su lectura **antes** de leer mi sección 4. |
