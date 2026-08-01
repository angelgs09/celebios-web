# INVESTIGACION.md — Registro de investigación de contenido

Registro de qué afirmaciones sobre CELEBIOS están respaldadas por evidencia y cuáles no.
Cuatro estados: **confirmada** (fuente verificable, se puede publicar), **histórica**
(cierta en el pasado, no implica oferta vigente), **pendiente** (no hay evidencia
suficiente; no se publica hasta confirmar), **rechazada** (afirmación en uso hoy en
`redesign-v2/*.html` que NO tiene respaldo y debe quitarse o reescribirse en Task 3).

Fecha de acceso de esta revisión: **2026-08-01**. Todas las fuentes citadas son archivos
del repo, ya comiteados, salvo donde se indique URL externa.

---

## Confirmadas

| Claim | Fuente | Fecha de acceso |
|---|---|---|
| Curso de Gatos: $1,400 MXN, pago único, 12 h, 11 temas, acceso 5 meses | `redesign-v1/CONTENIDO-REAL.md`, `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Curso de Gatos es la única convocatoria abierta hoy | `redesign-v1/CONTENIDO-REAL.md` ("única convocatoria abierta"), `migracion/redirects.csv` (única fila con `category=curso_disponible`) | 2026-08-01 |
| Docente del curso de gatos: Dra. Camila Hernández, MV chilena, Máster en Etología Clínica (UAB), autora de "Miaulogía" | `redesign-v1/CONTENIDO-REAL.md`, `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Aval CONCERVET (Consejo Nacional de Certificación en Medicina Veterinaria y Zootecnia) | `redesign-v1/CONTENIDO-REAL.md` | 2026-08-01 |
| Fundación 2010; modalidad a distancia desde 2014 | `redesign-v1/CONTENIDO-REAL.md` | 2026-08-01 |
| Razón social: Celebios S.C. (Centro Latinoamericano de Estudios en Ciencias Biológicas y de la Salud Animal) | `redesign-v1/CONTENIDO-REAL.md`, `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Pago del diplomado: depósito/transferencia o tarjeta vía PayPal (4% comisión), sin MSI | `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Contacto: contacto@celebios.com, WhatsApp +52 958 103 3574, FB /celebi0s, IG @celebios_edu | `redesign-v1/CONTENIDO-REAL.md`, `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Comunidad de alumnos en +10 países (MX, CO, EC, PE, VE, HN, CR) | `redesign-v2/DATOS-REALES-harvest.md` (hallazgo Instagram) | 2026-08-01 |

## Históricas (ciertas en el pasado, no implican oferta vigente)

| Claim | Fuente | Fecha de acceso |
|---|---|---|
| Diplomado en Rescate y Rehabilitación de Fauna Silvestre, 3ª edición: 170 h (130 en línea + 40 presenciales), 13 módulos teóricos + 1 práctico, práctica en UMA Selva Teenek (SLP). Cerró el 30-jun-2025. | `redesign-v1/CONTENIDO-REAL.md`, `PENDIENTES-CONTENIDO.md` | 2026-08-01 |
| Docentes históricos del diplomado de rehabilitación (IFAW, UNAM FMVZ, UAM Xochimilco, YUMKA', CRARC, etc.) | `redesign-v1/CONTENIDO-REAL.md` | 2026-08-01 |
| Precio histórico del diplomado (3ª edición): $19,500 MXN teórico / $26,000 MXN semipresencial | `redesign-v1/CONTENIDO-REAL.md` | 2026-08-01 |
| CELEBIOS impartió ~14 temas a lo largo del tiempo, incluyendo Anestesia/Contención, Manejo Conductual, Nutrición de Fauna en Cautiverio, Ortopedia de Aves, Félidos, Medicina Interna, Medicina Preventiva, Bioética, Diagnóstico y Terapéutica, Imagenología (fauna y caballos), SIG, Impacto Ambiental, Manejo de Datos | `redesign-v1/CONTENIDO-REAL.md` | 2026-08-01 |
| Slugs históricos "anestesia", "conductual", "nutricion", "ortopedia-aves", "rehabilitacion" ya usados como ancla en `/cursos#historico-*` | `migracion/redirects.csv` | 2026-08-01 |

**Nota de alcance:** ninguno de los hechos históricos anteriores se traduce en `contenido/programas.json`
como `offer`, precio, docente o fecha — esos campos están reservados para `status: "disponible"`.
Un programa histórico solo lleva slug/título/categoría/tema/resumen/evidencia/interest_topic.

## Pendientes (evidencia insuficiente — no publicar hasta confirmar)

| Claim | Por qué está pendiente | Fuente | Fecha de acceso |
|---|---|---|---|
| Diplomado de Nutrición y Alimentación de Fauna Silvestre estaría en 4ª generación ACTIVA (docente MVZ Maribel Anaya, práctica en Zoológico de Cali) | Un solo hallazgo de Instagram, marcado por la propia fuente como `[CONFIRMAR si quieres página propia]`; no aparece en el scrape de sitio ni en `redirects.csv` como convocatoria abierta. Contradice la instrucción vigente de que solo el curso de gatos está `disponible`. Se trata como histórico en `programas.json` hasta que Angel lo confirme. | `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Próxima edición (fecha/precio) del Diplomado de Rescate y Rehabilitación | La 3ª edición cerró 30-jun-2025; no hay fecha ni precio de una 4ª edición en ninguna fuente. | `PENDIENTES-CONTENIDO.md` | 2026-08-01 |
| Verbo exacto de las alianzas UNAM/UAEH/IFAW (¿convenio formal? ¿"docentes provienen de"?) | Ninguna fuente especifica el tipo de relación institucional; framing seguro actual es "docentes con trayectoria en". | `redesign-v2/DATOS-REALES-harvest.md`, `PENDIENTES-CONTENIDO.md` | 2026-08-01 |
| Contenido, duración, docentes y fechas de "Primeros Auxilios para Fauna Silvestre" y "Manejo de Reptiles" | Ninguna de las fuentes de evidencia (`CONTENIDO-REAL.md`, `DATOS-REALES-harvest.md`, `PENDIENTES-CONTENIDO.md`) menciona estos dos programas más allá de que existen como página en `redesign-v2`. | `redesign-v2/curso-primeros-auxilios.html`, `redesign-v2/curso-reptiles.html` | 2026-08-01 |
| RFC y domicilio fiscal exacto; número exacto de egresados; teléfono fijo; autores del blog | Flags explícitos sin dato público. | `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Precio base vigente del diplomado (¿sigue en $19,500 o subió?) | La convocatoria histórica mostraba $20,384 (=$19,500 + 4% PayPal); no hay confirmación de precio actual. | `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |

## Rechazadas (en uso hoy en `redesign-v2/*.html`, sin respaldo — corregir en Task 3)

| Claim en uso | Dónde aparece hoy | Por qué se rechaza |
|---|---|---|
| "La única academia latinoamericana de fauna silvestre con cursos avalados por CONCERVET" | `redesign-v2/lamina-viva.html:846` | Ninguna fuente de evidencia verifica exclusividad de mercado ("única"). Es una afirmación competitiva no verificable con los datos disponibles; retirar o reformular sin la palabra "única". |
| "Diploma con validez oficial" / "validez oficial, emitido por una institución universitaria" | `redesign-v2/diplomado-rehab.html:215,1115,1382(nota),1405,1408,1594`; `redesign-v2/lamina-viva.html:103,1319`; `redesign-v2/nosotros.html:1054` | "Validez oficial" es un término legal (equivalente a RVOE/SEP en México) que ninguna fuente confirma. La evidencia real es "constancia/diploma con valor curricular, avalado por CONCERVET y una institución universitaria (nombre sin confirmar)" — afirmación distinta y más débil. No usar "oficial" sin evidencia de RVOE o convenio universitario nombrado. |
| Afiliaciones institucionales genéricas ("institución universitaria") sin nombrar la universidad ni el tipo de vínculo | mismas líneas que arriba | El harvest de Instagram dice que la universidad "es probablemente UAEH... pero el post dice genérico; no nombrarla sin [CONFIRMAR]". Mientras no se confirme, no se debe implicar un convenio formal no verificado. |
| "Claustro internacional — 12 especialistas de México, España, Costa Rica y Estados Unidos" | `redesign-v2/diplomado-rehab.html:1382` (ya marcado `<span class="ph">por confirmar</span>` en el propio HTML) | La cifra "12" no aparece en ninguna fuente verificada (ni scrape del sitio ni harvest de Facebook/Instagram). Página de un producto de $19,500: no publicar el número hasta tener fuente, o sustituir por una lista nominal de docentes sin conteo. |
| "Esa URL rankea #3 nacional" (sobre `celebios.com/rehabilitacion-fauna-2024`) | `build.py` (comentario, no visible al usuario) y tesis de `redesign-v2/SEO-COPY-STRATEGY.md:18` | Afirmación de ranking sin captura de Google Search Console adjunta en el repo; es una inferencia de la estrategia SEO, no un dato medido. Se rechaza como hecho hasta que exista evidencia fresca de GSC (fecha, keyword, posición) en el repo. No bloquea el 301 en sí (que se conserva por prudencia SEO), solo la afirmación de la posición exacta. |

---

## Alcance de esta revisión

Fuentes cubiertas: `redesign-v2/DATOS-REALES-harvest.md`, `redesign-v1/CONTENIDO-REAL.md`,
`PENDIENTES-CONTENIDO.md`, `redesign-v2/SEO-COPY-STRATEGY.md`, `migracion/redirects.csv`,
y grep directo sobre `redesign-v2/*.html` para verificar el estado actual de las frases
rechazadas. No se consultaron fuentes externas (GSC, Instagram en vivo, WhatsApp) — donde el
harvest ya citaba una fuente externa, se preserva esa cita tal cual.
