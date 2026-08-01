I have enough authoritative, current material. Compiling the deliverable now.

---

# Frameworks SEO on-page/técnico para páginas de curso — CELEBIOS

Destilado de Backlinko (Brian Dean), Ahrefs, Moz/Google Search Central y la documentación oficial de Kajabi. Fuentes citadas al final. Todo accionable para Kajabi Basic + checkout en celebios.online.

---

## 1) CHECKLIST de SEO on-page para una página de curso

Aplicar a `curso-gatos.html`, `diplomado-rehab.html` y a cada curso nuevo. Cada curso = una página optimizada para **un keyword principal** (intención clara).

**Title tag**
- ≤ 60 caracteres (Kajabi recomienda < 70; Google trunca ~600px ≈ 60 chars). Keyword principal **al inicio**.
- Patrón de curso: `Curso de [Tema] [modificador] | CELEBIOS` → ej. `Curso de Lenguaje y Comunicación de los Gatos | CELEBIOS`. Para el ancla: `Diplomado en Rescate y Rehabilitación de Fauna Silvestre — 170h`.
- Único por página. Añade modificadores que la gente busca: "online", "certificado", "para MVZ", "México". Backlinko: title tags con modificadores capturan más long-tail.
- En Kajabi: campo **Page Title** en la sección "SEO and Sharing" de cada página.

**Meta description**
- 1–2 frases, ~150–160 caracteres, con el keyword + un CTA y un beneficio diferenciador (aval CONCERVET, 16 años, horas, certificado). No rankea directo pero sube el CTR.
- Única por página. Campo **Description** en "SEO and Sharing".

**H1 / H2 / H3**
- **Un solo H1** = nombre del curso con el keyword (en Kajabi: formato "Heading 1" en el editor de texto, no texto grande estilizado a mano).
- H2 para cada bloque que también es una pregunta de búsqueda: "¿Qué aprenderás?", "¿Para quién es este curso?", "Temario / Módulos", "Requisitos", "Certificación y aval", "Precio e inscripción", "Preguntas frecuentes".
- H3 para sub-temas (cada módulo del temario). Jerarquía limpia H1>H2>H3 = lo que Kajabi y Google esperan.

**Densidad / semántica (cobertura de tema, NO keyword stuffing)**
- Ahrefs y Backlinko coinciden: olvida el % de densidad; cubre el **tema completo** (términos que co-ocurren). Para "lenguaje felino": etología, comunicación, comportamiento, vocalizaciones, lenguaje corporal, gato, tutor, estrés. Para el diplomado: rescate, rehabilitación, fauna silvestre, manejo, contención, liberación, NOM-059, vida libre.
- Usa el keyword principal en: title, H1, primeros 100 palabras, una H2, URL, alt de la imagen principal, y meta description.
- Incluye **sinónimos y variantes regionales LATAM** (MVZ / médico veterinario zootecnista; "fauna silvestre" / "vida silvestre"; "diplomado" / "curso de especialización").

**Internal linking** (ver §3 a detalle)
- Cada página de curso enlaza al catálogo, a 2–4 cursos relacionados y al diplomado ancla, con **anchor text descriptivo** (no "clic aquí").

**Alt text en imágenes**
- Describe la imagen + keyword cuando sea natural: `alt="Veterinaria evaluando un ave rapaz durante rehabilitación de fauna silvestre"`. Sirve a accesibilidad, a Google Imágenes y a la cobertura semántica.
- Nombra los archivos descriptivamente antes de subir: `rehabilitacion-fauna-silvestre.jpg`, no `IMG_2381.jpg`.

**URL / slug**
- Corto, con keyword, minúsculas, guiones (no guion bajo), sin stop-words de relleno ni IDs. Kajabi lo confirma explícitamente.
- `/cursos/lenguaje-gatos`, `/diplomado-rescate-rehabilitacion-fauna`. Mantén una **carpeta consistente** `/cursos/` para señalar agrupación temática.

**E-E-A-T** (Experience, Expertise, Authoritativeness, Trust — crítico en YMYL/educación-salud animal)
- Muestra al **instructor con credenciales** (MVZ, posgrados, años de campo) en cada página de curso → señal de Expertise/Experience.
- Exhibe aval **CONCERVET** y alianzas **UNAM/UAEH/IFAW**, "16 años desde 2010" → Authoritativeness.
- Trust: testimonios reales de egresados, certificado verificable, política de devolución, datos de contacto, HTTPS. Backlinko (guía E-E-A-T): autoría visible + señales de confianza + reputación off-site.
- Enlaza la bio del instructor a su página de autor en "Nosotros".

**Schema (datos estructurados)**
- Marca cada curso con **`Course` schema** (JSON-LD) + `Provider` (Organization = CELEBIOS). Para el diplomado usa `Course` con `hasCourseInstance` (modalidad, fechas, duración). Añade **`FAQPage`** para el bloque de FAQ y `BreadcrumbList`.
- Esto habilita rich results de cursos en Google y alimenta la cobertura para AI Overviews / AEO.
- En Kajabi Basic se inserta vía bloque **Custom Code** (script JSON-LD) dentro de la página. (Ver §4.)

**Featured snippet / PAA targeting** (técnica Backlinko)
- Identifica las **People Also Ask** del tema y respóndelas literalmente en la página. Formato que Google extrae: **H2 con la pregunta exacta + respuesta de 40–55 palabras inmediatamente debajo**, en párrafo o lista.
  - "¿Cómo se comunican los gatos entre sí?", "¿Qué se necesita para trabajar en rehabilitación de fauna silvestre en México?", "¿Cuánto dura el diplomado de rescate de fauna?".
- Usa **listas numeradas** para procesos (pasos de un rescate) y **tablas** para comparativas (módulos/horas/precio) — son los formatos que más ganan snippets.
- Un bloque **FAQ** con 5–8 preguntas reales por curso cubre PAA y, con FAQ schema, da visibilidad extra.

---

## 2) Estructura y longitud ideal de una landing de curso para rankear

Una página de curso es **híbrida**: debe convertir (landing) y rankear (contenido suficiente para cubrir el tema). El error común es una landing "póster" con 150 palabras que nunca rankea.

**Longitud:** apunta a **1,200–2,000 palabras** de contenido real y útil. No por la cifra en sí — Ahrefs y Backlinko son claros en que el word count no es factor de ranking — sino porque cubrir bien el tema, responder PAA y describir 13 módulos naturalmente llega ahí. El diplomado ancla justifica el rango alto; un curso corto puede vivir bien en ~1,000–1,400.

**Estructura recomendada (orden + función SEO):**
1. **Hero**: H1 (nombre+keyword), subtítulo con propuesta de valor, badges de confianza (CONCERVET, horas, certificado), CTA de inscripción. Keyword en los primeros 100 palabras.
2. **Para quién es** (H2): MVZ, biólogos, estudiantes de últimos semestres, etc. Captura intención + variantes de audiencia.
3. **Qué aprenderás / Resultados** (H2): bullets con verbos de resultado → cobertura semántica.
4. **Temario / Módulos** (H2 + H3 por módulo): el cuerpo SEO más denso. Tabla módulo/horas para el diplomado (target de snippet).
5. **Instructor(es)** (H2): credenciales = E-E-A-T.
6. **Certificación y aval** (H2): CONCERVET + alianzas = Authoritativeness/Trust.
7. **Testimonios / casos de egresados** (H2): Trust + contenido único.
8. **Precio, modalidad y proceso de inscripción** (H2): claridad de conversión; CTA al checkout en celebios.online.
9. **FAQ** (H2 + preguntas como H3): target PAA/featured snippet + FAQ schema.
10. **CTA final + links internos** a cursos relacionados y catálogo.

**Principios transversales:** intención de búsqueda primero (¿el que busca "curso de X" quiere inscribirse o aprender? — sirve ambas en la misma página), contenido escaneable (párrafos cortos, bullets, negritas), una imagen/diagrama relevante con alt, y CTAs repartidos sin romper el flujo de lectura.

---

## 3) Táctica de INTERNAL LINKING para un sitio de cursos

Basado en la guía de internal linking de Backlinko (Brian Dean) + Ahrefs. Para un catálogo de cursos, el internal linking es la palanca on-page de mayor ROI porque concentra autoridad y enseña a Google la jerarquía.

**Arquitectura hub-and-spoke (pillar/cluster):**
- **Hub/pillar** = `catalogo.html` (y, por área temática, una página pillar por vertical: "Fauna silvestre", "Etología", "Clínica de fauna"). El **Diplomado** es el pillar comercial ancla.
- **Spokes** = cada curso corto. Cada spoke enlaza **de vuelta al hub** y a **2–4 cursos hermanos** del mismo tema. El hub enlaza a todos los spokes.

**Reglas accionables:**
1. **Anchor text descriptivo y variado** (Backlinko): enlaza con texto como "curso de primeros auxilios en fauna silvestre", no "ver más". Mezcla variantes (exact + parcial) para no verse spam, pero mantén el keyword visible. Google recomienda anchors descriptivos.
2. **Enlaza HACIA y DESDE tus páginas importantes**: el diplomado ancla debe recibir links internos desde Home, catálogo, Nosotros y desde cada curso corto relacionado ("¿Quieres profundizar? Continúa con el Diplomado de Rescate y Rehabilitación"). Así le pasas autoridad a la página que más te interesa convertir.
3. **Links contextuales > links de menú**: los enlaces dentro del cuerpo del contenido pesan más que los de navegación. Inserta enlaces a cursos relacionados dentro del temario y del bloque "qué aprenderás".
4. **De páginas con autoridad → a páginas nuevas**: cuando lances "Ortopedia de Aves" o "Nutrición de Fauna en Cautiverio", enlázalas desde tus páginas más fuertes (Home, diplomado) para acelerar su indexación y ranking. Backlinko llama a esto la jugada de "middleman pages".
5. **Profundidad de clic ≤ 3**: todo curso accesible en ≤ 3 clics desde Home. El catálogo plano ayuda.
6. **Sin links rotos ni huérfanos**: cada curso "Próximo" o "En producción" debe tener al menos un link entrante (desde el catálogo) para que se indexe.
7. **Bloque "Cursos relacionados"** reutilizable al pie de cada plantilla de curso (3 tarjetas) — sistematiza el spoke-to-spoke.

---

## 4) Técnico para Kajabi (Basic) — lo que aplica

Kajabi maneja gran parte del técnico automáticamente, pero tiene **límites reales** que importan para CELEBIOS.

**Sitemap XML**
- Kajabi **genera y mantiene el sitemap automáticamente** en `tudominio/sitemap.xml`; no se edita manualmente. Acción: una vez publicado el sitio, **envíalo en Google Search Console** (Sitemaps → `sitemap.xml`). Verifica que solo incluya páginas públicas (200 OK), no páginas de checkout/login.

**robots.txt**
- Kajabi gestiona un robots.txt por defecto y **no permite editarlo libremente**; su documentación dice explícitamente *no usar robots.txt como mecanismo de bloqueo*. Para ocultar una página usa la opción de **no-index / "hide from search engines"** de la página y, si ya está indexada, la **Removals Tool** de Search Console.

**Canonical**
- Kajabi añade canonical automático por página. Riesgo a vigilar: el **checkout en celebios.online** vs. el contenido del sitio principal → asegúrate de que cada curso tenga **una sola URL pública canónica** y que las páginas de oferta/checkout no compitan por el mismo keyword (canonicaliza o no-indexa las de checkout). Evita publicar la misma landing en dos dominios sin canonical cruzado — eso fragmenta autoridad.

**HTTPS**
- Provisto por Kajabi por defecto. Verifica que el dominio custom tenga SSL activo y que no haya contenido mixto.

**Core Web Vitals / velocidad**
- Punto débil de Kajabi: temas pesados + scripts. Acciones dentro de Basic:
  - **Comprime y dimensiona imágenes antes de subir** (WebP/JPG, < 200KB para imágenes de contenido). Es la mayor palanca de LCP.
  - Limita el **Custom Code**: cada script de terceros (chat, pixels, fuentes externas) golpea INP/LCP. Carga lo no crítico con `async`/`defer`.
  - Una sola familia tipográfica con pocos pesos; evita 4 fuentes distintas.
  - Mide con **PageSpeed Insights** móvil; prioriza LCP < 2.5s, INP < 200ms, CLS < 0.1.

**Mobile**
- Los temas de Kajabi son responsive por defecto, pero el **Custom Code/JSON-LD y los bloques HTML a mano pueden romper en móvil**. Verifica cada página de curso en móvil real. La indexación de Google es mobile-first: lo que no se ve en móvil, no cuenta.

**Schema vía Custom Code**
- Como Kajabi Basic no da acceso a theme code global, inserta el **JSON-LD (`Course`, `FAQPage`, `BreadcrumbList`, `Organization`) por página** usando un bloque **Custom Code** con `<script type="application/ld+json">`. Valida cada uno en el **Rich Results Test** de Google. Mantén un snippet maestro por tipo y solo cambia los datos por curso.

**SEO fields nativos por página (Kajabi)**
- Cada página y blog post tiene la sección **"SEO and Sharing"**: Page Title (<70 chars, único), Description (1–2 frases, keyword, única), URL slug (corto, guiones, minúsculas, keyword) e imagen social (Open Graph). Llénalos en TODAS las páginas — es el mínimo no negociable.

**Blog como motor de long-tail** (refuerza el insight ya validado de que SEO long-tail es el canal #1)
- Usa el **blog nativo de Kajabi** para artículos long-tail que alimentan los cursos: "Cómo interpretar el lenguaje corporal de tu gato", "Qué hacer si encuentras un ave herida en México". Cada artículo enlaza al curso correspondiente (spoke→hub comercial). Esto es lo que hacen los casos de Starterstory que ya cosechaste: el contenido informativo captura la búsqueda y el internal link la convierte.

---

## Fuentes
- Backlinko — *On-Page SEO* (Brian Dean): https://backlinko.com/on-page-seo
- Backlinko — *Internal Linking* (actualizado feb-2026): https://backlinko.com/hub/seo/internal-links
- Backlinko — *Google E-E-A-T*: https://backlinko.com/google-e-e-a-t ; *Schema Markup Guide*: https://backlinko.com/schema-markup-guide ; *Skyscraper Technique*: https://backlinko.com/skyscraper-technique
- Ahrefs Blog — *On-Page SEO: How to Optimize for Robots and Readers* (act. ago-2025, Ryan Law et al.): https://ahrefs.com/blog/on-page-seo/
- Google Search Central — *Link best practices / crawlable links* (citado por Backlinko): https://developers.google.com/search/docs/crawling-indexing/links-crawlable
- Kajabi Help Center — *Get started with SEO*: https://help.kajabi.com/articles/resources/business-guides/get-started-with-seo
- Kajabi Help Center — *Block AI & search engine bots* (robots.txt / Removals Tool): https://help.kajabi.com/articles/website/pages/block-ai-search-engine-bots-from-scraping-your-kajabi-site

Nota de aplicación inmediata: el mayor diferencial competitivo de CELEBIOS en SEO es **E-E-A-T** (CONCERVET + 16 años + UNAM/IFAW + instructores MVZ) y la **cobertura long-tail vía blog→curso**. Esos dos, más `Course`/`FAQPage` schema y un internal-linking hub-and-spoke con el Diplomado como ancla, son las palancas de mayor retorno dentro de las limitaciones de Kajabi Basic.