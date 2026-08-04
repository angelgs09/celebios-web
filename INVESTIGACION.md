# INVESTIGACION.md — Registro de investigación de contenido

Registro de qué afirmaciones sobre CELEBIOS están respaldadas por evidencia y cuáles no.
Cuatro estados: **confirmada** (fuente verificable, se puede publicar), **histórica**
(cierta en el pasado, no implica oferta vigente), **pendiente** (no hay evidencia
suficiente; no se publica hasta confirmar), **rechazada** (afirmación sin respaldo que estaba
en uso en `redesign-v2/*.html`; las cuatro se retiraron el 2026-08-02 y `build.py` impide que
vuelvan).

Fecha de acceso de esta revisión: **2026-08-01**, con correcciones verificadas el
**2026-08-02** (esquema de bulk redirects y estado de Search Console; cada una está fechada
en su bloque). Todas las fuentes citadas son archivos del repo, ya comiteados, salvo donde se
indique URL externa.

---

## Confirmadas

| Claim | Fuente | Fecha de acceso |
|---|---|---|
| Curso de Gatos: $1,400 MXN, pago único, 12 h, 11 temas, acceso 5 meses | `redesign-v1/CONTENIDO-REAL.md`, `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Curso de Gatos es la única convocatoria abierta hoy | `redesign-v1/CONTENIDO-REAL.md` ("única convocatoria abierta"), `migracion/redirects.csv` (único curso con `category=curso_disponible`: son 2 filas, `/lenguaje-y-comunicacion-de-los-gatos` y `/curso-lenguaje-felino`, ambas → `/curso-lenguaje-felino`) | 2026-08-01 |
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
| ~~Diplomado de Nutrición y Alimentación de Fauna Silvestre estaría en 4ª generación ACTIVA~~ **RESUELTO el 2026-08-02: confirmado con fuente pública.** Ver "Actualización 2026-08-02 — barrido de evidencia" al final de este documento. Lo que queda abierto ya no es la existencia del programa (probada), sino la decisión de negocio de si se publica, y las credenciales exactas de Maribel Anaya. | — | 2026-08-02 |
| Próxima edición (fecha/precio) del Diplomado de Rescate y Rehabilitación | La 3ª edición cerró 30-jun-2025; no hay fecha ni precio de una 4ª edición en ninguna fuente. | `PENDIENTES-CONTENIDO.md` | 2026-08-01 |
| Verbo exacto de las alianzas UNAM/UAEH/IFAW (¿convenio formal? ¿"docentes provienen de"?) | Ninguna fuente especifica el tipo de relación institucional; framing seguro actual es "docentes con trayectoria en". | `redesign-v2/DATOS-REALES-harvest.md`, `PENDIENTES-CONTENIDO.md` | 2026-08-01 |
| Contenido, duración, docentes y fechas de "Primeros Auxilios para Fauna Silvestre" y "Manejo de Reptiles" | Ninguna de las fuentes de evidencia (`CONTENIDO-REAL.md`, `DATOS-REALES-harvest.md`, `PENDIENTES-CONTENIDO.md`) menciona estos dos programas más allá de que existen como página en `redesign-v2`. | `redesign-v2/curso-primeros-auxilios.html`, `redesign-v2/curso-reptiles.html` | 2026-08-01 |
| RFC y domicilio fiscal exacto; número exacto de egresados; teléfono fijo; autores del blog | Flags explícitos sin dato público. | `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |
| Precio base vigente del diplomado (¿sigue en $19,500 o subió?) | La convocatoria histórica mostraba $20,384 (=$19,500 + 4% PayPal); no hay confirmación de precio actual. | `redesign-v2/DATOS-REALES-harvest.md` | 2026-08-01 |

## Rechazadas (RETIRADAS del HTML el 2026-08-02; la columna "Dónde aparecía" es histórica)

**Estado: cerradas.** Las cuatro afirmaciones de esta tabla se retiraron de `redesign-v2/*.html`
el 2026-08-02 y ya no se publican. No se dejaron a la buena voluntad de la siguiente
reescritura: `build.py` (`FRASES_RECHAZADAS` + `buscar_frases_rechazadas`) revienta el build
antes de escribir en disco si alguna reaparece, y `tests/test_content_contract.py`
(`TestFrasesRechazadas`) lo defiende. Los reemplazos aplicados son los que esta misma tabla
prescribía: "única academia…" → "Academia latinoamericana…"; "diploma con validez oficial,
emitido por una institución universitaria y respaldado por CONCERVET" → "diploma con valor
curricular, avalado por CONCERVET"; "Claustro internacional · 12 especialistas de México,
España, Costa Rica y Estados Unidos" → "Claustro internacional de especialistas" con la lista
nominal marcada por confirmar.

**Nota de alcance honesta:** el registro asignaba esta corrección a Task 3, pero la restricción
global del plan ("no publicar afirmaciones no verificadas") está vigente hoy y el build las
estaba publicando hoy. Se prioriza la restricción sobre la nota de calendario. Task 3 reescribe
estas plantillas, así que el texto puede cambiar; la guarda de `build.py` no.


| Claim en uso | Dónde aparece hoy | Por qué se rechaza |
|---|---|---|
| "La única academia latinoamericana de fauna silvestre con cursos avalados por CONCERVET" | `redesign-v2/lamina-viva.html:846` | Ninguna fuente de evidencia verifica exclusividad de mercado ("única"). Es una afirmación competitiva no verificable con los datos disponibles; retirar o reformular sin la palabra "única". |
| "Diploma con validez oficial" / "validez oficial, emitido por una institución universitaria" | `redesign-v2/diplomado-rehab.html:215,1115,1382(nota),1405,1408,1594`; `redesign-v2/lamina-viva.html:103,1319`; `redesign-v2/nosotros.html:1054` | "Validez oficial" es un término legal (equivalente a RVOE/SEP en México) que ninguna fuente confirma. La evidencia real es "constancia/diploma con valor curricular, avalado por CONCERVET y una institución universitaria (nombre sin confirmar)" — afirmación distinta y más débil. No usar "oficial" sin evidencia de RVOE o convenio universitario nombrado. |
| Afiliaciones institucionales genéricas ("institución universitaria") sin nombrar la universidad ni el tipo de vínculo | mismas líneas que arriba | El harvest de Instagram dice que la universidad "es probablemente UAEH... pero el post dice genérico; no nombrarla sin [CONFIRMAR]". Mientras no se confirme, no se debe implicar un convenio formal no verificado. |
| "Claustro internacional — 12 especialistas de México, España, Costa Rica y Estados Unidos" | `redesign-v2/diplomado-rehab.html:1382` (ya marcado `<span class="ph">por confirmar</span>` en el propio HTML) | La cifra "12" no aparece en ninguna fuente verificada (ni scrape del sitio ni harvest de Facebook/Instagram). Página de un producto de $19,500: no publicar el número hasta tener fuente, o sustituir por una lista nominal de docentes sin conteo. |
| "Esa URL rankea #3 nacional" (sobre `celebios.com/rehabilitacion-fauna-2024`) | `build.py` (comentario, no visible al usuario) y tesis de `redesign-v2/SEO-COPY-STRATEGY.md:18` | Afirmación de ranking sin captura de Google Search Console adjunta en el repo; es una inferencia de la estrategia SEO, no un dato medido. Se rechaza como hecho hasta que exista evidencia fresca de GSC (fecha, keyword, posición) en el repo. No bloquea el 301 en sí (que se conserva por prudencia SEO), solo la afirmación de la posición exacta. |

## Evidencia externa citada

| Claim | Fuente | Fecha de acceso |
|---|---|---|
| `bulkRedirectsPath` es una propiedad válida de `vercel.json` para importar redirects en bloque desde un archivo CSV/JSON/JSONL, procesados en el momento del deploy | https://vercel.com/docs/routing/redirects/bulk-redirects/getting-started | 2026-08-01 |
| El esquema `source,destination,statusCode` que emite `build.py` es válido. La tabla normativa "Bulk redirect field definition" define: `source` (string, **requerido**), `destination` (string, **requerido**), `permanent` (boolean, opcional, default `false`; alterna 308/307), `statusCode` (integer, opcional; 301, 302, 303, 307 o 308; *"Overrides permanent when set"*), `caseSensitive` y `preserveQueryParams` (boolean, opcionales, default `false`). Nota textual, transcrita tal cual, erratas de la fuente incluidas: *"CSV headers must match the field names below, can be specific \[sic\] in any order, and optional fields can be ommitted \[sic\]"* | https://vercel.com/docs/project-configuration/vercel-json#bulkredirectspath | 2026-08-02 |
| Los errores de bulk redirects solo se ven al desplegar: *"Any errors processing the bulk redirects will appear in the build logs for the deployment"*, y *"Bulk redirects do not work locally while using `vercel dev`"* | https://vercel.com/docs/routing/redirects/bulk-redirects/getting-started, https://vercel.com/docs/routing/redirects/bulk-redirects | 2026-08-02 |

**Corregido el 2026-08-02 — el esquema NO es un riesgo.** Una versión anterior de este bloque
daba por riesgoso el encabezado `source,destination,statusCode` que emite `build.py`, tomando
el `source,destination,permanent` de la página de *getting started* como si fuera el esquema.
No lo es: ahí es un EJEMPLO. La tabla normativa de campos (`vercel.json#bulkredirectspath`,
verificada el 2026-08-02) documenta `statusCode` como campo opcional que acepta `301` y que
**prevalece sobre `permanent`** cuando se define, y solo exige que los encabezados del CSV
coincidan con los nombres de los campos, en cualquier orden, pudiendo omitir los opcionales.
`source,destination,statusCode` con `301` es válido por contrato documentado —y es lo que
queremos, porque `permanent` solo alterna 308/307 y nunca produce un 301.

**Lo que sí sigue abierto: la verificación de ejecución.** Ningún preview deploy ha confirmado
que Vercel procese realmente este CSV. No se puede comprobar en local (`vercel dev` no ejecuta
bulk redirects) y los errores de procesamiento aparecen únicamente en los logs de build del
deployment. Es decir: la puerta de verificación es externa y esta tarea no la ejecutó (no se
hizo ningún `vercel deploy`). Antes de Task 5 o de cualquier cutover real hay que correr un
preview deploy y leer esos logs. Que los tests locales pasen no es evidencia de que las reglas
estén vivas en producción.

> **CERRADO el 2026-08-03, y el veredicto invalida el enfoque completo.** Se corrió el preview
> deploy. Todo lo de arriba sobre el esquema del CSV es correcto y sigue siendo cierto, pero
> resultó irrelevante: los logs de build respondieron
> **«Bulk redirects are not available for teams on the Hobby plan. Please upgrade to Pro or
> Enterprise to use this feature.»** El equipo `konecta-estudio` está en Hobby, así que
> `bulkRedirectsPath` no publicaba **ni una sola** de las 367 reglas. El contrato de redirects
> entero se apoyaba en una función de pago cuya disponibilidad nadie había verificado — que es
> exactamente lo que esta puerta existía para atrapar, y por qué "los tests locales pasan" no
> era evidencia.
>
> **Sustituido por `redirects` inline en `vercel.json`**, que sí funciona en Hobby. Contra el
> esquema normativo (`openapi.vercel.sh/vercel.json`): `redirects` admite `maxItems: 2048`
> (emitimos 367) y acepta `statusCode` entero, así que se sigue emitiendo **301** exacto y no
> el 308 de `permanent: true`. `build.py` revienta si las reglas superan ese tope.
>
> **Verificado en ejecución, no por contrato:** deploy `dpl_9qxuGHfSa2T9aFLJV4mToFuG5uiY`
> (READY). Se probaron **las 367 reglas** contra la URL de preview: **367/367 devuelven el
> código y el destino exactos, fragmento incluido, 0 fallas**. Las páginas publicadas responden
> 200 y una ruta inexistente responde 404.

**Nota sobre `/aula`:** una fila del inventario de migración redirige `/aula-virtual` (host
`celebios.com`) a `/aula`. `/aula` no tiene `<link rel="canonical">` y `robots.txt` lo excluye
(`Disallow: /aula`) porque es una zona autenticada, no una página pública indexable — así lo
exige el plan de este redesign, que preserva `/aula` byte a byte y noindex. Esa regla de
redirect se conserva como excepción explícita en `convertir_redirects_bulk` (no se difiere aun
cuando `/aula` no aparece en las rutas canónicas publicadas), porque es el alias público
heredado del área que sí existe como salida real del build, a diferencia de destinos que Task 3
todavía no ha creado.

---

## Alcance de esta revisión

Fuentes cubiertas: `redesign-v2/DATOS-REALES-harvest.md`, `redesign-v1/CONTENIDO-REAL.md`,
`PENDIENTES-CONTENIDO.md`, `redesign-v2/SEO-COPY-STRATEGY.md`, `migracion/redirects.csv`,
y grep directo sobre `redesign-v2/*.html` para verificar el estado actual de las frases
rechazadas. No se consultaron redes sociales en vivo (Instagram, WhatsApp) — donde el
harvest ya citaba una fuente externa, se preserva esa cita tal cual.

**Google Search Console SÍ se consultó, y no aportó ningún dato.** La propiedad
`sc-domain:celebios.com` se verificó el 2026-08-01 con un registro TXT en el DNS de Wix. Al
2026-08-02, revisada en vivo, la propiedad existe pero sigue en llenado: Rendimiento,
Indexación, Enlaces y Mejoras muestran "Se están procesando los datos", sus tablas dicen "Sin
datos", y EXPORTAR aparece deshabilitado en Rendimiento y en Enlaces (última actualización del
panel de Rendimiento: hace ~4,5 h). Lo único que ya trae cifras es el informe HTTPS, con 28
URLs — estado de certificado, no señal de búsqueda, y ni siquiera cubre el inventario (371
URLs en el sitemap de Wix). Por eso ninguna afirmación de este archivo se apoya todavía en
GSC, y la fila rechazada "rankea #3 nacional" sigue rechazada.

> **Superado en parte el 2026-08-02 21:30** — ver "Rendimiento liberado, y NO hay histórico"
> más abajo. Rendimiento ya trae datos (de un solo día); Indexación y Enlaces siguen
> procesando. La fila "rankea #3 nacional" **sigue rechazada**: 2 clics y 23 impresiones en
> un día no sostienen ninguna afirmación de ranking.

## Actualización 2026-08-01 — evidencia autenticada de Wix Analytics (parcial)

Se importó el primer export autenticado de analítica externa:
`migracion/evidencia/wix-page-visits-2025-08-02_2026-08-02.csv` (reporte
`Page Visits` del sitio Wix `celebios`, 152 filas, SHA-256 documentado en
`migracion/wix-analytics-manifest.json`), normalizado en
`migracion/wix-page-visits-normalized.csv` con columnas
`source_url,page_views,site_sessions,unique_visitors,period_start,period_end,inventory_match`.

Esto **no** cierra el pendiente externo de la sección anterior. Sigue sin
existir: (1) una conexión de este sitio Wix a Google Search Console (el
reporte `Top Search Queries on Google` de Wix no está disponible), y (2) un
export de datos de búsqueda de Google que se pueda importar.

**Corrección del 2026-08-02 sobre el punto (2).** La propiedad de CELEBIOS en
Search Console SÍ existe: `sc-domain:celebios.com`, verificada el 2026-08-01
con un TXT en el DNS de Wix. Cambia la razón, no el veredicto — Search Console
sigue procesando (Rendimiento, Indexación, Enlaces y Mejoras muestran "Se están
procesando los datos", las tablas dicen "Sin datos" y EXPORTAR está
deshabilitado en Rendimiento y en Enlaces), así que **no hay export disponible
y el gate SEO sigue BLOQUEADO, con `cutover_allowed: false`**. Propiedad
verificada no es gate desbloqueado.

Por lo tanto `clicks`, `impressions`, `position` y `backlinks` en
`migracion/urls-wix.csv`/`redirects.csv` **siguen vacíos** — no se rellenan con
page views de Wix, que es una métrica distinta (tráfico de página, no señal de
búsqueda orgánica de Google), ni con el informe HTTPS de GSC (28 URLs), que es
estado de certificado. El corte real y el diseño final siguen esperando el
primer export CON DATOS de `sc-domain:celebios.com` y su aprobación.

## Actualización 2026-08-03 — el archivo histórico estaba en `/galeria-1`

`/galeria-1` es la **8ª página más visitada** del sitio viejo (131 visitas en 12 meses) y
estaba clasificada `sin_equivalente`, es decir **404** en el sitio nuevo. Era la única de las
seis rutas sin destino con contenido real; las otras cinco son basura del editor (`/blank`,
`copia-de-copia-de-…`, `/test`, `/keeper`).

Su contenido resultó ser el registro escrito de la escuela, y **confirma hechos que hasta hoy
estaban marcados sin fuente**. Todo lo que sigue es transcripción del sitio vivo de CELEBIOS
(consultado 2026-08-03), no redacción:

| Hecho | Detalle |
|---|---|
| **Fundación en 2010** | "Ene-Mar, 2010, 1ª generación" del diplomado de medicina y manejo de fauna silvestre en cautiverio. Sostiene el `foundingDate: 2010` del JSON-LD, que antes no tenía fuente citada. |
| Serie de 8 generaciones | 1ª (ene-mar 2010), 2ª (jun-sep 2010), 3ª (ene-mar 2012), 4ª (jun-sep 2012), 5ª (sep-nov 2013), 6ª (feb-jun 2014), 7ª (abr-jul 2017), 8ª (oct 2018-ene 2019) |
| Tamaño de dos generaciones | 38 alumnos (contención química y anestesia, 2017); 32 alumnos (diagnóstico y terapéutica) |
| Formato semipresencial | 80 h teóricas en línea + 40 h prácticas presenciales; el de rehabilitación 2019 fue de 130 h + 40 h |
| Prácticas en 7 países | Ecuador, Costa Rica, Perú, Argentina, México, Colombia y España (rehabilitación, 2019) |
| Sedes de prácticas | Parque Ecológico Zacango, Reino Animal, laboratorios de la UAEH, Africam Safari, Laboratorio de Herpetología FES Iztacala/UNAM, Aviario El Nido, CIVS Los Reyes (SEMARNAT), Rancho Mágico |
| Ponentes con adscripción | Dr. Randall Arguedas (Costa Rica), Dra. Valeria Aguilar Sánchez (FMVZ/UNAM), Dr. Emilio Rendón Franco (UAM), Dra. Claudia Rivera Cerecedo (IFC/UNAM), Dr. Jorge Luna del Villar (FMVZ/UNAM), Dr. Juan Carlos Morales Luna (Hospital de Aves FMVZ/UNAM), Biól. Jorge Mendoza Marroquín (Inst. Biología UNAM), MVZ Juliana Peña Stadlin (Zoológico de Cali), entre otros |

Se publica en `/galeria`, y `/galeria-1` ahora redirige ahí en vez de morir en 404.

**Fotografía de prácticas (2026-08-03, segunda pasada).** El Wix no tiene fotos de cursos en
vivo: solo carteles. Las fotos están en los álbumes de la página de Facebook de CELEBIOS
(`facebook.com/celebi0s`, 18 mil seguidores), que la galería vieja ya enlazaba. Con
autorización de Angel se descargaron de seis álbumes propios —Rehabilitación Fauna 2022 (95),
Imagenología en equinos (40), Rescate y Rehabilitación 2024 (35), Imagenología diagnóstica
(30), Manejo integral de aves (29) y Nutrición 2025 (8)— de los que la vista de álbum de
Facebook sirve unas 9 por álbum a ~640-890 px. De 35 obtenidas se publican **10**, elegidas
por mostrar trabajo clínico real y fechadas entre 2022 y 2025. Se descartaron los banners con
el logo, los letreros de sedes de terceros (Zoológico de Cali, Bioparque Yana-Cocha), los
selfies de grupo y los paisajes. Sustituyen a las fotos de 2010-2015 rescatadas del Wix, que
eran de menor resolución y encuadre amateur.

**Criterio de publicación de imágenes (2026-08-03).** Angel advirtió que "imágenes
polémicas nos pueden causar problemas". En un sitio de fauna silvestre el riesgo es concreto y
de dos tipos:

1. **Lectura fuera de contexto.** Una exploración clínica normal puede leerse como maltrato
   por quien no ve el contexto. Se retiraron dos: la guacamaya con las alas extendidas y
   estiradas por manos enguantadas sobre la mesa —que estaba en el **hero de la portada**, la
   primera imagen del sitio— y el perezoso boca arriba inmovilizado. El hero pasó a la
   auscultación de una lechuza, que comunica cuidado profesional en vez de sujeción.
2. **Rostros identificables.** De las 24 imágenes publicadas, **11 muestran caras
   reconocibles** de alumnos y docentes. Que estén públicas en la página de Facebook no
   equivale a republicarlas en el sitio comercial: en México la imagen es dato personal bajo la
   LFPDPPP, la misma ley que este proyecto acaba de citar en el aviso de privacidad. **No hay
   consentimiento documentado**, y obtenerlo es decisión de Angel. Las 11 están listadas en
   `tests/test_content_contract.py::TestImagenesPublicadas`.

También se excluyeron desde el principio los logos de terceros y la señalización de sedes
ajenas (Zoológico de Cali, Bioparque Yana-Cocha).

El conjunto publicado es una **lista cerrada** en los tests: añadir una imagen obliga a un
cambio explícito, para que no entre ninguna por descuido.

**Imágenes.** Se rescataron del Wix vivo y se guardaron en `redesign-v2/media/` (26 archivos,
2.4 MB en WebP) en vez de enlazarlas a `static.wixstatic.com`: si se cancela la cuenta de Wix,
ese CDN deja de servirlas y desaparece el único registro visual del archivo. De 59 imágenes
descargadas se descartaron 33 por dos motivos explícitos: **stock del banco de Wix** (jaguar,
flamenco, paisajes, gato, mujer con laptop — su licencia cubre el uso *dentro* de Wix, no
fuera) y **logos de terceros** (CONCERVET, UAEH, YanaCocha, Tamandúa), porque el verbo exacto
de las alianzas sigue sin fuente. Lo que se conserva es material propio: 15 carteles de
convocatorias con marca CELEBIOS y 11 fotos de prácticas docentes.

## Actualización 2026-08-02 21:30 — Rendimiento liberado, y NO hay histórico

Search Console soltó el informe de **Rendimiento**: el banner de procesamiento
desapareció, EXPORTAR quedó habilitado (`aria-disabled="false"`) y las tablas
traen cifras. Se capturaron en
`migracion/evidencia/gsc-rendimiento-2026-08-01.csv`.

**El hallazgo que corrige la premisa del plan: no hubo backfill.** Con el rango
de **16 meses** seleccionado en la UI, el gráfico se rotula "del 1 de agosto de
2026 al 1 de agosto de 2026" — un solo día. Los 16 meses de Search Console son
el máximo de **retención hacia adelante**, no una recuperación de historia
hacia atrás: una propiedad empieza a acumular el día que se verifica. Como
`sc-domain:celebios.com` se verificó el 2026-08-01, el histórico de 2025 y
antes **no existe y no va a llegar**. Seguir esperando no cambia eso.

Lo que hay, del 1-ago-2026: 2 clics, 23 impresiones, CTR 8,7 %, posición media
9,8; 3 consultas (`celebios` 1/1, `paulina alejandra` 0/3, `rubén saavedra`
0/1) y 17 páginas con impresiones.

**Las 17 páginas están cubiertas 17/17 por `migracion/redirects.csv`**, sin una
sola ausente. Sus columnas `clicks`/`impressions` ya se rellenaron con estas
cifras — son señal de búsqueda de Google, que es justo lo que esas columnas
pedían. `position` y `backlinks` siguen vacías: la tabla de páginas no
desglosa posición y el informe de Enlaces sigue procesando.

Dos señales que tocan el diseño:

1. `imagenologia-caballos-2020` recibió impresiones y su regla apunta a
   `/cursos#historico-imagenologia-caballos`, **una de las 7 anclas huérfanas**
   (tema sin tarjeta en el catálogo). Deja de ser un hueco hipotético: hay
   tráfico real cayendo ahí.
2. Las consultas con más impresiones son **nombres de personas** (`paulina
   alejandra`, `rubén saavedra`), y sus páginas
   (`/paulinaachavezcontreras`, `/rubensaavedraperez`, `confidence=baja`)
   redirigen al genérico `/egresados`. Si la página de egresados no ofrece un
   ancla por persona o al menos por cohorte, ese tráfico aterriza sin match.

Siguen **procesando**, ambos con el mismo mensaje "vuelve a comprobar esta
sección mañana": **Indexación de páginas** y **Enlaces**. Ese segundo es el que
alimentaría la columna `backlinks`.

---

## Actualización 2026-08-02 — barrido de evidencia sobre tres programas

Barrido multi-modal (redes vía Apify, sitemaps vivos de ambos dominios, Wayback, buscadores y
el propio repo) con verificación independiente de cada hallazgo abriendo la fuente.
**Limitación honesta: 11 de 62 agentes murieron por errores de conexión de API, así que el
barrido NO es exhaustivo.** Lo que sigue es lo que sí quedó verificado con cita literal.

### Diplomado en Nutrición y Alimentación de Fauna Silvestre — CONFIRMADO, real y vigente

Deja de ser un "hallazgo de Instagram sin confirmar". Hay evidencia pública y de dominio propio:

| Hecho | Fuente | Cita literal |
|---|---|---|
| La 4ª generación ya corrió su semana práctica | https://www.celebios.online/nutricion2025 | "(4a generación)" y "Colombia, Zoológico de Cali: 11 al 15 de agosto, 2025 (cupo lleno)" |
| La semana práctica se impartió, no solo se anunció | Facebook `/celebi0s`, post del 2025-08-12 | "¡Inició la semana práctica del Diplomado en Nutrición y Alimentación de Fauna Silvestre Bajo Cuidado Humano! … Nuestros alumnos llegaron al Zoológico de Cali para iniciar sus 40 horas del módulo práctico … Contamos con participantes de Perú, Colombia, Venezuela y México" |
| Concluyó, con constancias entregadas | Facebook `/celebi0s`, post del 2025-08-16 | "Hoy concluimos una semana llena de aprendizaje y experiencias en el Zoológico de Cali. Nuestros alumnos recibieron sus constancias de participación" |
| Existe desde 2019 | https://www.celebios.com/nutricion-2021 (HTTP 200) | "DIPLOMADO EN NUTRICIÓN Y ALIMENTACIÓN DE FAUNA SILVESTRE EN CAUTIVERIO"; 1ª generación jun–nov 2019, 80 h teóricas en línea + 40 h prácticas |
| Tiene tráfico registrado | `migracion/wix-page-visits-normalized.csv` | `/nutricion2024` con 135 vistas, 117 sesiones, 93 visitantes únicos |

**Precisiones que NO se deben perder al publicar:**

- La práctica **en México** solo está **anunciada** ("se viene una extraordinaria práctica ahora
  en México"), no hay evidencia de que se haya impartido. Anuncio ≠ hecho.
- **Maribel Anaya**: el sitio propio de CELEBIOS la registra como "M. en C. Maribel Anaya Lira,
  COORDINADORA DEL DIPLOMADO"; los posts de Facebook la llaman "Dra." y "MVZ". Las tres
  credenciales no son intercambiables. **No publicar "MVZ" ni "Dra." hasta resolver cuál es.**
- El post dice que "dirigió esta semana práctica"; el sitio dice que "coordina el diplomado".
  Tampoco es lo mismo.

**Consecuencia abierta, de negocio y no de código:** hay un diplomado real, con cuatro
generaciones e inscripciones abiertas, que **no existe en el sitio nuevo**. Ya estaba anotado en
`LANZAMIENTO_25JUL.md:42-44` ("hay un diplomado vendiendo sin página"). Publicarlo como
disponible rompería la invariante de un solo programa disponible (`build.py`) y la regla de
negocio de `migracion/README.md`. Decisión de Angel, no del build.

### Primeros Auxilios para Fauna Silvestre y Manejo de Reptiles — CERO evidencia pública

El barrido no encontró **ninguna** traza de que estos dos programas existan fuera de las
maquetas del propio rediseño:

- Sitemaps vivos de `celebios.com` (371 URLs) y `celebios.online` (15 URLs): 0 coincidencias con
  "reptil" ni "auxilio". Los demás cursos históricos sí tienen URL.
- `migracion/redirects.csv` (386 filas): 0 coincidencias.
- Scrape del sitio viejo (`redesign-v1/CONTENIDO-REAL.md`) y harvest de Facebook/Instagram
  (`redesign-v2/DATOS-REALES-harvest.md`): no aparecen en la lista de ~14 temas históricos.
- Único rastro real de reptiles: es el **módulo 7 dentro del Diplomado de Rescate y
  Rehabilitación**, no un curso independiente.
- Las propias maquetas se contradicen con el `status: "historical"` del contrato:
  `redesign-v2/curso-primeros-auxilios.html` dice "**Próxima edición — en desarrollo.** Este
  curso aún no tiene fecha de apertura".

**Resuelto como "no hay evidencia", el 2026-08-02.** Angel atestiguó primero que ambos sí se
impartieron y poco después, al pedírsele la fuente, respondió que no tiene idea de ese dato y
que se siga sin él. No queda entonces ninguna fuente: ni documental ni testimonial firme.

Consecuencia aplicada: estos dos programas **no se presentan como impartidos**. Su `summary` en
`contenido/programas.json` se corrigió —afirmaba que el programa estaba "presente como página
propia en el sitio de CELEBIOS", cuando solo existe como maqueta en `redesign-v2/`— y su
`evidence` dejó de ser la maqueta citándose a sí misma para apuntar a esta sección, que es lo
único que sí está documentado: que se buscó y no se encontró nada.

**Sigue abierto y es decisión de negocio, no de código:** las dos páginas publican el aval
CONCERVET 13 y 10 veces respectivamente, y se presentan como "Próxima edición — en desarrollo".
Un aval nominal sobre un curso del que no hay constancia de que exista es una afirmación del
mismo tipo que las de la tabla de rechazadas. Retirarlo reestructura las dos páginas, así que
queda para que Angel decida: retirar el aval, retirar las dos páginas, o aportar la fuente.
