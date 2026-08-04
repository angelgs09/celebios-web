# BRIEF · CELEBIOS para Claude Design — 4 de agosto de 2026

Paquete de contexto para rediseñar el sistema visual de celebios.com.
Repo: `angelgs09/celebios-web`, rama **`codex/celebios-redesign-total`**.
Sitio de revisión (no es el dominio público todavía): **https://celebios.vercel.app**

---

## 1. Qué es CELEBIOS

Centro Latinoamericano de Estudios en Ciencias Biológicas y de la Salud Animal, S.C.
Academia de educación continua en **fauna silvestre** para médicos veterinarios y
biólogos de toda Latinoamérica. Fundada en 2010. Avalada por **CONCERVET** (Consejo
Nacional de Certificación en Medicina Veterinaria). Comunidad en +10 países.

**Quién lee este sitio:** un MVZ o biólogo de 25 a 45 años, en México, Colombia,
Ecuador, Perú o Venezuela, que ya trabaja o quiere trabajar con fauna silvestre.
Compra formación, no inspiración. Detecta el rigor y detecta la falta de rigor —
un dibujo mal hecho de un tapir le dice más de la academia que tres párrafos de copy.

**Qué vende hoy: exactamente un producto.** El curso corto pregrabado de Lenguaje
y Comunicación de los Gatos (12 h, Dra. Camila Hernández, $1,400 MXN de pago
único). **Nada más tiene precio ni convocatoria abierta**, incluido el diplomado
ancla de 170 h en Rescate y Rehabilitación de Fauna, cuya tercera edición cerró
el 30 de junio de 2025. Los otros 18 programas del catálogo están en dos estados
y ninguno se puede comprar:

| Estado | Cuántos | Qué significa |
|---|---|---|
| **Disponible** | 1 | se vende hoy, con precio |
| **Sin convocatoria** | 9 | se impartió antes; no hay edición abierta ni precio |
| **En producción** | 8 | área del atlas todavía sin construir |

Esa asimetría —un producto vendible contra dieciocho que no lo son— es la
tensión central del diseño, no un detalle de contenido.

**El sitio es la única superficie de venta.** SEO es el canal #1: la página vieja de
Wix `celebios.com/rehabilitacion-fauna-2024` rankea #3 nacional.

---

## 2. Qué hay hoy (33 páginas, en producción de revisión)

| Ruta | Archivo fuente | Papel |
|---|---|---|
| `/` | `redesign-v2/lamina-viva.html` | Home |
| `/cursos` | `redesign-v2/catalogo.html` | Catálogo de 19 programas |
| `/curso-lenguaje-felino` | `redesign-v2/curso-gatos.html` | Ficha de curso (plantilla) |
| `/diplomado-rescate-rehabilitacion-fauna` | `redesign-v2/diplomado-rehab.html` | Ancla premium |
| `/recursos/*` | `redesign-v2/recurso-*.html` | 14 artículos SEO |
| resto | `nosotros`, `contacto`, `admisiones`, `egresados`, `galeria`, `recursos`, `aviso-de-privacidad` | soporte |

**Las 4 primeras son el encargo.** El resto hereda el sistema que salga de ellas.

**Capturas del estado actual, tomadas del sitio en vivo** (no del código, no de un
kit viejo): `docs/design/capturas/` — 01 a 05 a 1440 px, 06 a 08 a 390 px.

La novena no es la ficha completa del diplomado en móvil sino solo su sección de
modalidades (`09-diplomado-movil-modalidades.png`), y la razón es en sí misma un
dato: **esa página mide 18,108 px de alto a 390 px**, más de lo que Chrome puede
capturar de una vez. Son unas 21 pantallas de scroll para una ficha de un
programa que hoy ni siquiera se puede comprar.

> ⚠️ Si no puedes ver esas imágenes, **dilo antes de diseñar**. No supongas su
> contenido. Descríbeme qué ves en `01-home-desktop.png` antes de proponer nada.

---

## 3. Dirección visual actual: "Lámina Viva"

La tesis: el sitio es un **atlas naturalista latinoamericano**. Cada programa es una
lámina numerada (`LÁM. 07`) de un atlas de campo. La eligió Angel en junio de 2026
sobre dos alternativas ("Estación de Campo" y "Visor de Especie", ambas en el repo).

**La tesis sigue siendo buena. La ejecución se quedó a medias.** Eso es el encargo.

### Tokens reales hoy (`:root` en cada archivo)

```css
--charca:    #14294F;  /* marino canvas — color del logo */
--charca-2:  #1E3768;  /* panel marino */
--ceibo:     #2FA8C9;  /* cian del logo = disponible + acción */
--coral:     #2FA8C9;  /* señal: marcos, CTAs, foco (mismo cian) */
--cobalto:   #7A5797;  /* morado del logo = próxima edición */
--sage:      #6FB07A;  /* verde salvia del logo = acento de vida */
--hueso:     #EEF2EC;  /* papel */
--lodo:      #4D5F7C;  /* texto secundario sobre claro */
--ink:       #16294C;  /* tinta */
--r-plate: 6px;  --frame: 2px;  --maxw: 1240px;
--ease: cubic-bezier(.2,.7,.2,1);
/* escala de espaciado base 4: --s1 .25rem … --s10 8rem */
```

Los colores **salen del logo real** (descargado en `redesign-v2/brand/`). No son una
paleta elegida por gusto: son la marca. El mapeo semántico (cian = disponible,
morado = próxima edición, salvia = vida) es un sistema, no decoración.

### Tipografía (self-hosted en `redesign-v2/fonts/`, woff2)

- **Bricolage Grotesque** — display
- **Instrument Sans** — texto
- **Space Grotesk** — mono / rótulos
- Cero serif. Fue decisión explícita.

---

## 4. Diagnóstico honesto de lo que está mal HOY

Verificado mirando las capturas, no leyendo el código.

1. **El sitio casi no tiene imágenes.** La home tiene **una** foto (el hero: una
   veterinaria sosteniendo una lechuza). El catálogo tiene **cero**. Diecinueve
   tarjetas de puro texto. Una academia de fauna silvestre sin fauna a la vista.

2. **Monotonía de tarjeta.** Las 19 tarjetas del catálogo son la misma caja, en un
   grid de 4 columnas, y lo único que cambia es una palabra en cursiva dentro de un
   marco. Escanear ese muro no produce jerarquía: produce fatiga.

   Y ahora el problema es peor de lo que se ve, porque **18 de esas 19 tarjetas no
   llevan a ninguna parte**: no se pueden comprar. El catálogo tiene que hacer que
   la única tarjeta comprable gane sin esconder a las otras dieciocho, que siguen
   siendo el argumento de que esto es una academia con recorrido y no un curso
   suelto. Hoy la única diferencia entre la que se vende y las que no es una
   píldora de color y un precio en letra pequeña.

3. **Cebra de superficies.** La home alterna marino / papel / marino / papel siete
   veces. Cada banda cambia de tema completo. Lee como acordeón, no como jerarquía —
   el lector no sabe qué es importante porque todo grita lo mismo por turnos.

4. **Hero sobrecargado.** Siete elementos de texto (eyebrow `ATLAS LAT · LÁM. 00`,
   H1 de 3 líneas, párrafo, línea de aval, dos CTAs, micro-línea de credenciales,
   tagline) más una foto pequeña arrinconada a la derecha. El momento de mayor
   atención de todo el sitio está repartido entre siete cosas.

5. **"Por qué CELEBIOS" son cuatro columnas iguales con un número grande.** Es el
   patrón más genérico que existe en la web. 2010 / IFAW / 170 h / 100%.

6. **La lámina tipográfica funciona una vez y se agota repetida.** El mejor momento
   visual del sitio es el bloque del diplomado: `Panthera onca` en cursiva grande
   sobre una retícula, con su barra de escala. Ese mismo recurso, repetido 19 veces
   en miniatura en el catálogo, deja de leerse como lámina y pasa a leerse como
   plantilla sin llenar. (Contexto: hasta ayer eran dibujos de línea; seis de ellos
   eran el mismo contorno de cuadrúpedo con distinta cabeza, rotulados con seis
   géneros distintos. Se retiraron por eso. El rótulo tipográfico fue el reemplazo
   honesto, no el destino.)

7. **Footer de granja de enlaces**, cuatro columnas.

**Lo que sí está bien y hay que conservar:** el sistema de estados con color
(cian/morado/gris), la numeración de láminas, la barra de escala, el bloque del
diplomado, la honestidad del catálogo (dice "sin convocatoria abierta" en vez de
fingir disponibilidad), y el rigor de accesibilidad (ver §6).

---

## 5. El encargo

Rediseñar el **sistema** trabajando sobre cuatro páginas: **home, catálogo, ficha de
curso y diplomado**. Lo que salga de ahí —tokens, escala tipográfica, componentes,
ritmo de superficies— se propaga después a las 33 páginas a mano.

Preguntas que el rediseño tiene que contestar:

- ¿Cómo se ve un **atlas de campo** que no puede apoyarse en ilustraciones a medida?
  (No hay presupuesto de ilustración validada por un MVZ, y ese era el gate original
  de esta dirección.)
- ¿Cómo se distingue un catálogo de **19 programas de los que solo uno se vende**
  sin convertirlo en 19 cajas iguales, y sin esconder los otros 18?
- ¿Cómo se ordena una home cuya única foto es el hero?
- ¿Cómo se sostiene la **jerarquía entre lo único que se vende hoy** (un curso de
  $1,400 que dura 12 horas) y **lo que ancla la marca** (un diplomado de 170 h que
  hoy no tiene convocatoria)? El barato es el que paga; el caro es el que da
  autoridad. Hoy el diplomado ocupa mucho más espacio y no se puede comprar.
- ¿Cómo se ve una ficha de un programa **sin convocatoria** para que siga
  convenciendo y captando lista de espera, sin fingir que está a la venta? Son
  nueve páginas del sitio y hoy son fichas de venta con el botón desactivado.

---

## 6. Reglas duras — no negociables

Estas ganan sobre cualquier preferencia estética. Varias vienen de fallos reales
que ya costaron trabajo en este proyecto.

### Stack

- **HTML de un solo archivo por página, CSS vanilla dentro de `<style>`.**
  Nada de React, Tailwind, JSX ni paso de build. `build.py` publica los archivos de
  `redesign-v2/` tal cual. Si propones Tailwind, el resultado no es portable.
- **Fuentes self-hosted.** Cero `<link>` a Google Fonts: la CSP del aula lo bloquea y
  filtraría la IP del alumno a un tercero. Los woff2 ya están en `redesign-v2/fonts/`.
- **Cero dependencias nuevas.** Sin GSAP, sin Motion, sin librerías de iconos.
- Los archivos `kajabi/*.kajabi.html`, `estacion-de-campo.html`, `visor-de-especie.html`
  y `lamina-viva-v1-coral.html` son **histórico**. No se tocan, no se rediseñan.

### Contenido y honestidad

- **No inventes ni un dato.** Ni cifras, ni fechas, ni nombres de docentes, ni
  testimonios, ni "+500 egresados". El sitio tiene ~110 marcadores "por confirmar"
  precisamente porque el dueño todavía no aporta esos datos. Un número inventado en
  una academia con aval profesional es un problema legal, no un detalle de copy.
- **Un solo precio en todo el sitio: $1,400 MXN**, y solo para el curso de lenguaje
  felino. Ningún otro programa lleva importe. Esto no es una preferencia: el 4 de
  agosto de 2026 se retiraron siete precios que se habían publicado un mes, dos de
  ellos ($1,200 y $1,600) sin ninguna fuente en el repositorio — eran placeholders
  de una ronda de diseño anterior que se colaron a producción.
- **Ninguna fecha de apertura, ni marcada "por confirmar".** El mismo día se
  retiraron "Abre Sep 2026" y "Abre Oct 2026" de dos programas cuya edición ya
  había cerrado. Una fecha por confirmar sigue siendo una promesa. El build
  rechaza el commit si aparece una.
- **No generes imágenes.** Ni fotos de fauna, ni de alumnos, ni de instalaciones, ni
  "placeholder photography" tipo picsum. Una foto generada en el sitio de una
  academia se lee como evidencia de algo que pasó. Las 13 imágenes reales del repo
  (`redesign-v2/media/`) son todo lo que hay, y varias están recortadas a propósito
  para que no aparezcan rostros identificables ni escudos de universidades ajenas.
  Si una sección necesita una imagen que no existe, **deja el hueco marcado y dilo**.
- **Los H1, H2 y el texto visible tienen mapa de palabras clave** (`SEO-COPY-STRATEGY.md`).
  Puedes reordenar y recortar; no reescribas los encabezados sin decir cuál cambias
  y por qué.
- **Sin logos de terceros.** UNAM, UAEH, IFAW: el vínculo institucional no está
  confirmado por escrito y el build rechaza el commit si aparece el verbo equivocado.

### Accesibilidad (hay 315 pruebas que lo blindan)

- Contraste **AA verificado en navegador real**, en las dos superficies (papel y
  marino). El sitio pasó de 20 fallos falsos a 0 reales; no lo regreses.
- **Anillo de foco visible** en ambas superficies (`--foco` claro sobre marino,
  oscuro sobre papel). `outline: none` está prohibido.
- **Cero scroll horizontal a 390 px.** Trece páginas lo tenían; ya no. La causa fue
  `1fr` en grid (que es `minmax(auto,1fr)` y no baja de min-content). Usa `minmax(0,1fr)`.
- Enlace "saltar al contenido", `aria-current` en la navegación, y todo interactivo
  alcanzable por teclado.
- Animación: discreta y motivada. Nada de scroll-hijack ni de bucles infinitos.

---

## 7. Lo que SÍ puedes tocar libremente

Escala tipográfica y jerarquía · ritmo y densidad de secciones · el sistema de
superficies (cuándo marino, cuándo papel, cuándo algo intermedio) · la anatomía de
la tarjeta de curso · la composición del hero · el tratamiento de los estados
(disponible / próxima edición / en producción) · tablas, FAQ y footer · estados
interactivos (hover, activo, foco) · el uso de la retícula y la barra de escala como
lenguaje gráfico · el espaciado.

---

## 8. Material en el repo

- `docs/design/capturas/` — 9 capturas del sitio en vivo, hoy
- `redesign-v2/brand/` — logo real, versión navy y knockout blanco
- `redesign-v2/fonts/` — las tres familias en woff2
- `redesign-v2/media/` — las 13 imágenes reales publicadas
- `redesign-v2/references/` — referencias cosechadas de Mobbin (edtech) y Starter Story
- `redesign-v2/SEO-COPY-STRATEGY.md` — mapa de palabras clave por página
- `redesign-v2/DATOS-REALES-harvest.md` — qué dato está verificado y con qué fuente
- `contenido/programas.json` — el contrato de contenido de los 19 programas
- `MIGRACION.md` — de dónde viene este sitio y por qué

---

## 9. Entregable que espero de Claude Design

1. **Una lectura del brief en una línea** antes de diseñar ("leo esto como…").
2. **Dos o tres direcciones** para la home, no una. Cada una con su razón.
3. Elegida una: **home, catálogo, ficha de curso y diplomado** en alta fidelidad,
   a 1440 px y a 390 px.
4. **Los tokens explícitos** — color, escala tipográfica, espaciado, radios, sombras —
   en una lista que se pueda portar a CSS custom properties.
5. **Qué componente cambia y qué componente se queda**, para saber qué propagar a
   las otras 29 páginas.

El HTML que salga de Claude Design es **maqueta, no código de producción**: se porta
a mano a CSS vanilla, se pasa por las 315 pruebas y se verifica en navegador antes
de publicar.
