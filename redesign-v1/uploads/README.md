# CELEBIOS — Assets para Claude Design

Sube **toda esta carpeta** a Claude Design junto con `PROMPT-claude-design.md`.

## Estructura

### `/` raíz
- **PROMPT-claude-design.md** — prompt auditado a pegar en Claude Design.
- **README.md** — este archivo.

### `/logo` (1)
- `celebios-logo.png` (297×365). ⚠️ Resolución modesta: sirve para derivar paleta, pero idealmente consigue el logo en **SVG o PNG grande** para hero/print.

### `/fotos` (8) — banco fotográfico REAL (lo que va en el sitio)
**Fauna limpia (sin texto) — candidatas a hero/fondos:**
- `fauna-01-guacamaya-plumas.jpg` (2832×4256) — la más impactante.
- `fauna-03-collage-fauna.jpg` (2800×2800) — mosaico de especies.
- `fauna-05-serpiente-verde.jpg` (2560×1600) — alta res (posible stock).
- `fauna-02-leopardo-campo.jpg` (1920×1080) — limpia, pero felino africano (off-brand geográfico).
- `fauna-04-instalaciones-campus.jpg` (674×450) — instalaciones, baja res (apoyo).

**Personas / prueba social REAL (auténticas, baja-media res):**
- `generacion-visita-terrario.jpg` (960×720) — grupo de alumnos en visita.
- `practica-tecnicas-quirurgicas.jpg` (720×540) — alumnos en práctica quirúrgica.
- `practica-alumna-erizo.jpg` (720×540) — alumna en manejo de fauna.

### `/posters-marca` (9) — pósters reales de CELEBIOS
NO son fotos: son flyers de diplomados con texto. **Úsalos como referencia de la identidad actual** (tipografías, colores, tono, cómo presentan convocatorias), no como banco fotográfico. Incluyen: contención/anestesia, ortopedia de aves 2018, manejo conductual 2022, rescate y rehabilitación, diagnóstico/terapéutica, gatos, etc.

### `/screenshots-sitio-actual` (4) — punto de partida (qué NO repetir)
`actual-inicio / -nosotros / -cursos / -curso-rehabilitacion` (Wix actual).

### `/screenshots-referencias` (6) — inspiración de diseño
- Ed-tech español: `ref-platzi-home`, `ref-platzi-catalogo` (⚠️ solo viewport), `ref-platzi-landing-curso` (landing con temario+CTA+precios), `ref-domestika-cursos` (catálogo+tarjetas).
- Conservación/naturaleza: `ref-rewild`, `ref-wwf` (fotografía emocional).

## Notas de honestidad
- Fotos sacadas del sitio real (static.wixstatic.com) en full-res, **NO de Facebook** (FB bloquea scraping). Mismo banco visual, descargable de verdad.
- La recolección inicial trajo varios pósters mal etiquetados como "fauna/generaciones"; se re-verificaron **visualmente uno por uno** y se reclasificaron con nombres honestos.
- **Recomendación:** la prueba social fotográfica es limitada (3 fotos reales de personas). Para reforzar la sección "Egresados/Comunidad", agrega manualmente 3–5 fotos grupales de generaciones desde el **Facebook /celebi0s** (ahí hay más, pero no son scrapeables).

## Close gates (resultado)
| Gate | Estado |
|---|---|
| Logo presente y válido | ✅ (mejorable a SVG) |
| ≥8 fotos reales válidas | ✅ 8 |
| Fotos = fotos reales (no pósters mal etiquetados) | ✅ corregido |
| Screenshots del sitio actual | ✅ 4 |
| Referencias ed-tech (catálogo + landing) + conservación | ✅ 6 |
| Sin duplicados / sin basura / todas válidas | ✅ (run check: 28 img, 0 inválidas) |
| Prompt incluido | ✅ |
| Carpeta lista para subir | ✅ 30 MB |
