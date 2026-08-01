This is the critical, current fact I needed: **Google deprecated the FAQ rich result** — it's now only shown for well-known authoritative government and health websites. That materially changes my FAQ recommendation (still mark up FAQPage, but don't expect rich results; target PAA/featured-snippets via content structure instead). I now have everything authoritative. Let me write the plan.

I have enough authoritative grounding (Google Course spec scraped, FAQ deprecation confirmed, existing on-page JSON-LD reviewed). Delivering the plan.

---

# CELEBIOS — Plan de Schema.org + SEO técnico + E-E-A-T

Estado actual verificado: ya existe JSON-LD parcial y bien encaminado en `nosotros.html` (EducationalOrganization) y `diplomado-rehab.html` (Course + CourseInstance + Offer). El catálogo, home y curso-gatos **no** tienen JSON-LD aún. El plan estandariza lo existente y completa los huecos.

Archivos de referencia (rutas absolutas):
- `C:\Users\coche\Desktop\CELEBIOS-web\redesign-v2\nosotros.html` (líneas 28-77: EducationalOrganization ya presente — extender)
- `C:\Users\coche\Desktop\CELEBIOS-web\redesign-v2\diplomado-rehab.html` (líneas 28-67: Course ya presente — completar offers/instructor)
- `C:\Users\coche\Desktop\CELEBIOS-web\redesign-v2\curso-gatos.html` (head con meta/OG ya OK — falta JSON-LD)
- `C:\Users\coche\Desktop\CELEBIOS-web\redesign-v2\catalogo.html` (falta ItemList)
- `C:\Users\coche\Desktop\CELEBIOS-web\redesign-v2\lamina-viva.html` (home — falta WebSite/Org)

---

## 1. Mapa de schema por tipo de página

| Página | Tipo(s) JSON-LD | Rich result objetivo |
|---|---|---|
| Home (`lamina-viva.html`) | `EducationalOrganization` (referenciada por `@id`) + `WebSite` (con `SearchAction`) | Knowledge panel / sitelinks searchbox |
| Nosotros | `EducationalOrganization` completa (nodo canónico) | Knowledge panel, E-E-A-T |
| Catálogo | `CollectionPage` + `ItemList` de `Course` + `BreadcrumbList` | **Course list (carousel)** |
| Curso corto (gatos, plantilla) | `Course` + `hasCourseInstance` + `Offer` + `BreadcrumbList` + (`FAQPage` opcional) | **Course info** rich result |
| Diplomado | `Course` + múltiples `CourseInstance` + `Offer` (varios) + `BreadcrumbList` + `FAQPage` | Course info |

**Arquitectura de grafo recomendada:** definir la organización **una sola vez** con `"@id": "https://www.celebios.online/#org"` y en todas las demás páginas referenciar `"provider": {"@id": "https://www.celebios.online/#org"}` en vez de re-declarar el bloque completo. Evita divergencia de datos (mismo pitfall anti-divergencia de tu guía base) y mantiene un solo nodo de entidad para Google.

---

## 2. Campos por tipo (con required vs. recommended de Google)

### A. `EducationalOrganization` (Home + Nosotros) — nodo `#org`
Schema.org no es rich-result por sí mismo, pero alimenta el knowledge graph / E-E-A-T. Campos clave:
- `@id`, `name`, `legalName`, `url`, `logo` (URL absoluta, ≥112×112px), `image`
- `foundingDate: "2010"`, `description`, `slogan`
- `areaServed` (usar objeto `{"@type":"AdministrativeArea","name":"América Latina"}` o lista de países `["MX","CO","AR",...]`)
- `knowsAbout` (lista de temas — ya presente, buena señal de topicalidad)
- `sameAs` ← **falta y es crítico para E-E-A-T**: array con Instagram, Facebook, LinkedIn, YouTube de CELEBIOS
- `hasCredential` → `EducationalOccupationalCredential` con `recognizedBy` = CONCERVET (ya presente)
- `affiliation` → UNAM, UAEH, IFAW (ya presente — mantener)
- `contactPoint` → `{"@type":"ContactPoint","contactType":"admisiones","availableLanguage":"es","email/telephone"}`
- `address` → `PostalAddress` con `addressCountry: "MX"` (aunque sea solo país)

### B. `Course` + `CourseInstance` + `Offer` (cursos y diplomado)
Según Google ([course spec](https://developers.google.com/search/docs/appearance/structured-data/course), actualizado 2025-12-10):

**Course list / carousel — requeridos mínimos:** `name`, `description`, `provider`. Esto es lo mínimo para elegibilidad de la lista de cursos.

**Course info (rich result completo) — además incluir:**
- `offers` → `Offer` con `price`, `priceCurrency` (ISO 4217 = `"MXN"`), `availability` (`https://schema.org/InStock`), `category`, `url`
- `hasCourseInstance` → `CourseInstance` con:
  - `courseMode`: `"online"` (curso gatos / teórico) o `"blended"` (diplomado semipresencial)
  - `courseWorkload`: duración ISO-8601 (`"PT12H"` gatos, `"PT170H"` diplomado completo, `"PT130H"` teórico)
  - `courseSchedule` (opcional) → `Schedule` con `repeatFrequency`, `startDate`/`endDate` si hay cohortes con fecha; para "a tu ritmo" omitir fechas y dejar solo `courseMode: online`
  - `instructor` → `Person` (ver §3, E-E-A-T)
- `educationalCredentialAwarded`: `"Constancia con valor curricular"` (gatos) / `"Diploma con valor curricular avalado por CONCERVET"` (diplomado)
- `coursePrerequisites` (ya presente en diplomado — bueno)
- `inLanguage: "es"`, `provider: {"@id":"...#org"}`
- `aggregateRating` / `review` → **solo si tienes reseñas reales verificables**. No inventar (riesgo de acción manual). Si las hay, marcar con `Review` de personas reales.

**Regla de Google a respetar:** mínimo **3 cursos** con `Course` markup para ser elegible al feature. CELEBIOS ya tiene ≥4 disponibles → OK. No poner precios en el `name` del curso ("Curso - solo $30") — Google lo prohíbe explícitamente.

### C. `CollectionPage` + `ItemList` (Catálogo)
- `CollectionPage` con `name`, `description`, `url`
- `mainEntity` o `hasPart` → `ItemList`
- `ItemList.itemListElement` → array de `ListItem` con:
  - `position` (1,2,3…)
  - `url` (URL absoluta a cada página de curso) **— requerido para el carousel**
  - `item` → `Course` resumido (`name`, `description`, `provider`)
- Cada curso del catálogo debe tener su **página de detalle propia** con el `Course` completo (modelo summary-page + detail-page de Google). El catálogo es la summary page.

### D. `FAQPage` — ⚠️ cambio importante de Google
**Google deprecó el rich result de FAQ** (confirmado en su [doc de FAQPage](https://developers.google.com/search/docs/appearance/structured-data/faqpage)): ahora **solo se muestra para sitios gubernamentales y de salud reconocidos/autoritativos**. CELEBIOS no califica → no esperar el rich result visual.

Recomendación:
- **Sí** mantener `FAQPage` markup (semántica válida, ayuda a LLMs/AI Overviews y no penaliza).
- **No** depender de él para CTR. Para ganar PAA/featured snippets, la palanca real es la **estructura de contenido** (§5), no el schema.
- Estructura: `mainEntity` → array de `Question`, cada uno con `acceptedAnswer` → `Answer` con `text`.

### E. `BreadcrumbList` (todas las páginas internas)
- `itemListElement` → `ListItem` con `position`, `name`, `item` (URL).
- Ej. diplomado: Inicio › Catálogo › Diplomado de Rescate y Rehabilitación.
- Sí genera rich result de migas activo y mejora comprensión de jerarquía.

---

## 3. E-E-A-T para educación veterinaria (el diferenciador del nicho)

Google evalúa contenido **YMYL-adyacente** (salud animal, decisiones clínicas) con vara más alta. La señal nuclear de CELEBIOS es: **docentes reales con credenciales + avales institucionales verificables**. Ya tienes los nombres en el diplomado (MVZ Erika Flores Reynoso, MVZ PhD Valeria Ruoppolo, Dr. Carlos Gutiérrez Olvera/UNAM FMVZ, Dr. Albert Martínez Silvestre, Dr. Ernesto Domínguez Villegas, etc.) — hay que **estructurarlos**:

1. **Autor/docente como entidad `Person`** en el `instructor` de cada Course y en `member`/`employee` de la Organización:
   - `name`, `jobTitle` ("Médica Veterinaria Zootecnista, especialista en aves marinas"), `affiliation` (IFAW, UNAM FMVZ), `alumniOf`, `hasCredential` (`EducationalOccupationalCredential`), `sameAs` (perfil ResearchGate / LinkedIn / Google Scholar / ORCID si existe).
   - Esto convierte "MVZ PhD Valeria Ruoppolo" de texto plano en una **entidad reconocible** que Google puede cruzar con su conocimiento de IFAW.
2. **Páginas de bio de docentes** (Experience + Expertise): aunque sea un bloque por docente con foto, credenciales, publicaciones y rol. Es la evidencia "E" (Experience real de campo: rescate, rehabilitación) que un curso de fauna sí puede demostrar y un competidor genérico no.
3. **Avales como `EducationalOccupationalCredential` + página dedicada**: explicar qué es CONCERVET y qué significa "valor curricular" (link a CONCERVET). Authoritativeness verificable externamente.
4. **Citas y fuentes**: en contenidos clínicos (primeros auxilios, ortopedia de aves), citar literatura/guías (IFAW, manuales). Refuerza Trust en YMYL.
5. **Página "Acerca de" robusta** (ya existe `nosotros.html`): misión ("evitar iatrogenias", bienestar de fauna), 16 años de historia, equipo, aliados. Es lo primero que mira un quality rater.
6. **Trust operacional**: política de reembolso, datos de contacto reales, checkout en dominio coherente (`celebios.online`), HTTPS, términos. La inconsistencia de dominio (sitio Kajabi vs. checkout) debe resolverse con canonical y `sameAs` coherentes para no diluir la entidad.

Marca cada docente con `Person` y enlázalo desde el `Course.instructor` **y** desde `EducationalOrganization.employee` con el mismo `@id` por persona.

---

## 4. Featured snippets + People Also Ask (la jugada SEO real)

Dado que el FAQ rich result está deprecado, el camino a posición-0 es **estructura de contenido**, no markup:

- **Long-tail informacional** (tu canal #1 ya validado en las refs de StarterStory): crear contenido que responda preguntas exactas que tu audiencia teclea: *"¿cómo saber si un gato está estresado?"*, *"¿qué hacer si encuentro un ave caída?"*, *"¿cuánto dura un diplomado de rehabilitación de fauna?"*, *"¿qué se necesita para trabajar en rescate de fauna en México?"*
- **Formato anti-snippet**: pregunta como `<h2>`/`<h3>` exacta → respuesta directa de **40-55 palabras** en el primer párrafo inmediatamente debajo → luego expandir. Google levanta ese párrafo como snippet de párrafo.
- **Snippets de lista/tabla**: "13 módulos del diplomado" como `<ol>`, comparativas (online vs. semipresencial) como `<table>`. Listas y tablas ganan snippets estructurados.
- **PAA**: cada artículo/curso debe rematar con 4-6 preguntas-respuesta (marcadas como `FAQPage` para AI Overviews aunque no den rich result). Cubrir variantes "qué/cómo/cuánto/cuándo/para qué".
- **Clusters temáticos por área** (etología felina, rehabilitación, reptiles, aves): un pilar por área + sub-artículos enlazados internamente → autoridad topical, que es lo que mueve el long-tail edtech.

---

## 5. SEO técnico accionable en Kajabi Basic

Restricción real: Kajabi Basic permite **landing pages + bloques de Custom Code**, sin acceso a theme code global. Implicaciones:

| Ítem | Acción concreta en Kajabi Basic | Notas |
|---|---|---|
| **JSON-LD** | Pegar cada bloque en un **Custom Code block** por página (en el `<head>` si el bloque lo permite, o al final del body — Google lo lee igual). Un bloque por página, con el `@id` compartido. | Validar cada uno en **Rich Results Test** y **Schema Markup Validator** antes de publicar. |
| **Sitemap** | Kajabi **genera `sitemap.xml` automático**. Verificar que las landing publicadas aparezcan; enviar en Search Console. | El checkout en `celebios.online` debe tener su propio sitemap o quedar `noindex` si no es contenido SEO. |
| **Canonical** | Kajabi pone canonical auto por página; **forzar** el canonical correcto en SEO settings de cada landing (ya lo haces en los HTML: `https://www.celebios.online/...`). Cuidado con duplicados Kajabi-subdominio vs. dominio propio. | Resolver discrepancia dominio sitio (`celebios.online`) vs. enlaces internos. Un solo host canónico con/sin `www`. |
| **OG / Twitter** | Configurar en SEO settings de cada landing **y** ya están en el HTML. `og:image` debe ser absoluta y ≥1200×630 (hoy apunta al logo blanco — cambiar a imagen social dedicada por curso). | Logo blanco sobre fondo claro se ve mal al compartir; crear OG cards por curso. |
| **robots.txt** | Kajabi gestiona robots; asegurar que las páginas de cursos **no** estén bloqueadas y que áreas de miembros/checkout sí. | |
| **Meta robots / noindex** | Marcar `noindex` páginas thin o duplicadas (ej. variantes de prueba `lamina-viva-v1-coral`, `estacion-de-campo`, `visor-de-especie` si no son públicas). | Hoy hay varias variantes — no indexar las experimentales. |
| **Performance** | Kajabi es lento por defecto: minimizar custom JS, usar `font-display:swap` (ya tienes `&display=swap`), `preconnect` a fonts (ya presente), imágenes en WebP, `loading="lazy"` en below-the-fold, evitar fuentes pesadas extra. | Las 3 familias (Bricolage, Instrument, Space Grotesk) son muchas — considerar reducir a 2 para LCP. |
| **Mobile** | `viewport` ya correcto. Verificar tap targets ≥48px y que los bloques Custom Code sean responsive (no anchos fijos). | Audiencia LATAM mayoritariamente móvil. |
| **Hreflang** | Sitio único en español para todo LATAM → no necesitas hreflang multi-idioma, pero sí `<html lang="es">` (ya presente) y opcionalmente `lang="es-MX"` como mercado primario. | |
| **Idioma del schema** | Quitar/normalizar caracteres: hoy el JSON-LD mezcla con y sin acentos ("rehabilitacion"). Usar texto correcto y consistente con la página visible (Google exige que el markup refleje el contenido visible). | |

---

## 6. Orden de implementación sugerido

1. **Nodo `#org` canónico** en Nosotros + referenciarlo desde todas (añadir `sameAs`, `contactPoint`, `address`).
2. **Course completo** en diplomado (ya 80% — añadir `instructor` como `Person` con credenciales + `inLanguage`) y **replicar la plantilla** a curso-gatos.
3. **ItemList** en catálogo (summary page) apuntando a las páginas-detalle.
4. **BreadcrumbList** en las 4 internas.
5. **Person** por docente + bloques de bio (E-E-A-T) — la mayor palanca diferencial del nicho.
6. **FAQPage** + reestructura de contenido para PAA (sin esperar rich result).
7. Validar todo en Rich Results Test, enviar sitemap en Search Console, arreglar OG images y `noindex` de páginas experimentales.

---

## Fuentes citadas (reales, verificadas hoy)
- Google Search Central — **Course (Course list / carousel + ItemList) structured data**, actualizado 2025-12-10: `https://developers.google.com/search/docs/appearance/structured-data/course` (required: `name`, `description`, `provider`; mínimo 3 cursos; prohibido precio en el título; ItemList requiere `itemListElement`/`position`/`url`).
- Google Search Central — **FAQPage structured data**: `https://developers.google.com/search/docs/appearance/structured-data/faqpage` — **el rich result de FAQ está deprecado y solo se muestra para sitios gubernamentales y de salud autoritativos** (confirmado en el changelog de la doc). Implica usar FAQPage solo como señal semántica, no como fuente de CTR.
- schema.org — `EducationalOrganization`, `Course`, `CourseInstance`, `Offer`, `ItemList`, `CollectionPage`, `BreadcrumbList`, `Person`, `EducationalOccupationalCredential` (vocabulario base referenciado en los HTML existentes).
- Insight de canal ya validado en `redesign-v2/references/starterstory/cases/*.md`: **SEO long-tail = canal #1** para negocios de cursos → refuerza la apuesta por clusters temáticos + featured snippets sobre el schema decorativo.

**Nota de precisión que cambia la entrega vs. el brief:** el brief pedía "targetear featured snippets vía FAQ" — hay que aclarar a Angel que **FAQ schema ya no genera rich result** (deprecado por Google); el FAQ sigue valiendo para AI Overviews y comprensión, pero los featured snippets/PAA se ganan con **estructura de contenido** (pregunta-H2 + respuesta de 40-55 palabras + listas/tablas), no con el markup. Esa es la corrección de mayor impacto del análisis.