# Prompt para Claude Design — Sitio web CELEBIOS (v2, post-audit)

> **Antes de enviar el prompt, sube como contexto en Claude Design:**
> 1. Logo de CELEBIOS (vectorial o PNG en alta).
> 2. 8–12 fotos del Facebook /celebi0s (fauna, prácticas de campo, generaciones de alumnos).
> 3. Screenshot del sitio actual celebios.com (para ver el punto de partida).
> 4. Screenshots de las referencias que menciono abajo (Domestika, Platzi, un sitio de conservación). **Claude Design no navega URLs en vivo: si no subes el screenshot de una referencia, no la uses de memoria — pídemela.**

---

## 0. Dominio y plataformas (léelo primero)

- **Sitio público (lo que vas a diseñar):** vive en **celebios.com**, apuntado a Kajabi.
- **Plataforma de cursos / login / checkout:** **celebios.online** (Kajabi, ya existe).
- Por lo tanto, los CTA de **"Inscríbete"** y **"Aula Virtual"** son **enlaces externos** del sitio público hacia celebios.online. Diseña esa transición para que NO se sienta como salir del sitio (mismo branding + microcopy "continúas tu inscripción en la plataforma").

## 1. Rol y objetivo

Eres un diseñador de producto senior especializado en sitios para instituciones educativas. Diseña el **sitio web público de CELEBIOS**, academia latinoamericana de educación continua en ciencias biológicas y salud animal. Reemplaza un sitio viejo de Wix y se **construye en Kajabi** (la sección 5 es obligatoria). Busco un diseño moderno con **autoridad académica + calidez por la fauna**, que convierta visitas en inscripciones.

**Arranque:** confírmame que entendiste la restricción de Kajabi (sección 5), el dominio (sección 0) y la audiencia; hazme las preguntas que necesites; y entrega como **primer paso 2–3 variaciones del Hero + estructura de secciones del Inicio en DESKTOP** (contenido en baja fidelidad pero dirección visual clara). Cuando elija una, la llevas a alta fidelidad y **después** derivas mobile. No generes las 3 variaciones full en desktop+mobile de golpe.

## 2. Qué es CELEBIOS (datos reales; no inventes)

- **Nombre completo:** Centro Latinoamericano de Estudios en Ciencias Biológicas y de la Salud Animal (CELEBIOS S.C.).
- **Tagline:** "Eliminando fronteras, acercando al mundo."
- **Misión:** Formar individuos con conocimientos y habilidades en las áreas biológicas y de la salud animal, capaces de resolver problemas reales en manejo y conservación de fauna.
- **Qué ofrece:** Diplomados y cursos en modalidad **híbrida** (clases grabadas donde los autores explican a profundidad + material de apoyo + sesiones en vivo). Diplomados reales: Rehabilitación de Fauna Silvestre · Nutrición y Alimentación de Fauna Silvestre en Cautiverio · Contención Química y Anestesia de Fauna Silvestre · Medicina Preventiva y Manejo en Cautiverio · Manejo Conductual de Fauna · Ortopedia de Aves · Medicina Interna de Pequeñas Especies · Imagenología · Bioética · Félidos · SIG y manejo de datos de percepción remota.
- **Aliados (logos):** UAEH, UNAM, COMVEPEH, Bio Animal Wild.
- **Plataforma de cursos:** celebios.online (Kajabi) — login, catálogo, checkout.
- **Contacto:** contacto@celebios.com · WhatsApp +52 958 103 3574 · IG @celebios_edu · FB /celebi0s.

### Guardrails de credibilidad (datos a CONFIRMAR, no afirmar a ciegas)
- **"Validez oficial":** NO la afirmes de forma genérica. Usa el aval concreto que el cliente confirme (p. ej. "aval académico de [institución]") o déjalo como **placeholder editable**.
- **Logos de aliados (UNAM/UAEH, etc.):** mostrarlos implica relación institucional. Trátalos como **placeholders a confirmar**; si el uso de marca no está autorizado, referir como "colaboraciones" en texto.
- **Credenciales de personas** (p. ej. presidente Miguel A. Galindo Bustos): marca grado/cargo como **dato a confirmar**.
- **Cifras** (egresados, países, años): siempre **placeholders editables** del tipo "+[N] egresados de [N] países".

## 3. Audiencia

Profesionales y estudiantes hispanohablantes de toda LATAM (México, Colombia, Perú, Ecuador y más): médicos veterinarios, biólogos, ecólogos, ingenieros ambientales/forestales, personal de zoológicos/santuarios y estudiantes de últimos semestres. Buscan especializarse en fauna silvestre con respaldo académico serio. **Gran parte llega desde el celular y desde redes sociales.** Promesa de conversión clave: **"estudia desde cualquier país de LATAM, a tu ritmo, con sesiones en vivo".**

## 4. Conversión

Objetivos en orden: (1) **inscripción** a diplomado → landing del curso en celebios.online; (2) **lead por WhatsApp**; (3) **acceso de alumnos** al Aula Virtual (login en celebios.online).

Reglas:
- **CTA primario único y consistente** en todo el sitio ("Ver diplomados" / "Inscríbete"), siempre con el mayor peso visual (color acento). WhatsApp siempre **secundario**.
- **Botón flotante de WhatsApp** persistente en mobile en todas las páginas (ver nota de implementación en sección 5).
- Cuida la **continuidad visual** del hand-off a celebios.online (es el punto de fuga #1).

## 5. Restricción de implementación (OBLIGATORIA — Kajabi BASIC)

El diseño se construye en **Kajabi plan Basic**: theme gratis + page builder por secciones + **CSS personalizado por página**. **No hay edición del código global del theme.** Reglas:

- **Mapeo a secciones nativas.** Arma todo como secciones apilables estándar y, **para CADA sección, declara su tipo Kajabi**: Hero · Text · Image+Text · Gallery/Images · Cards/Columns · Accordion/FAQ · CTA Banner · Form · Footer. Indica nº de columnas y qué ajustes son nativos vs. cuáles necesitan CSS por página.
- **Navegación/header:** se configura en los ajustes del theme (logo + items + 1 botón). Diseña un **menú simple (5–7 ítems):** Inicio, Diplomados, Nosotros, Egresados, Galería, Contacto + botón **"Aula Virtual"** → celebios.online/login. **Sin** mega-menús ni búsqueda en el header.
- **Formulario de contacto:** se implementa con el **form nativo de Kajabi** (campos fijos: nombre, email, teléfono, mensaje). Diseña el bloque asumiendo esos campos y estilo aplicable por CSS. **No** inventes campos custom ni formularios multi-paso.
- **Tira de logos de aliados:** no existe componente nativo de "logos"; se arma con **sección de imágenes en columnas**. Logos sobre fondo neutro, mismo alto óptico, padding generoso; monocromo/hover vía CSS. **Sin** carrusel de logos.
- **Testimonios y galería:** **grid/tarjetas estáticas apiladas, NO carrusel.** Un slider sería "mejora opcional vía CSS/JS por página", no requisito.
- **WhatsApp flotante:** no es nativo; se inyecta vía CSS/JS por página en cada plantilla. El enlace base es `wa.me/529581033574`.
- **Mapa (Egresados/Contacto):** lista de países o **imagen/ilustración estática** de mapa — **no** mapa interactivo. Ubicación en Contacto: embed simple opcional.
- **CSS es POR PÁGINA (no global).** Por eso: (a) confía en los **tokens del theme** para colores/tipografías/botones globales; (b) reserva el CSS por página para retoques puntuales; (c) minimiza estilos que deban repetirse en todas las páginas (se duplican a mano).
- **Tipografías:** prioriza fuentes del **selector del theme de Kajabi** (mayormente Google Fonts) con **soporte de español (acentos, ñ)**. Si propones una fuera de lista, márcala como "requiere CSS por página".
- **Espaciado:** escala simple en **múltiplos de 8px**. Componentes reutilizables; el catálogo y la landing de curso comparten **la MISMA tarjeta de curso**.
- **HTML exportado = MAQUETA de referencia visual, NO código para pegar.** Cada sección debe mapear 1:1 a un tipo de sección de Kajabi para replicarla en el page builder.

## 6. Arquitectura del sitio (páginas a diseñar)

1. **Inicio** (la más importante).
2. **Nosotros** — misión/visión, breve historia, presidente (dato a confirmar), aliados.
3. **Diplomados y Cursos** — catálogo (grid de tarjetas → cada una enlaza a su landing en celebios.online).
4. **Landing de curso** — 1 plantilla reutilizable (ver sección 8).
5. **Egresados / Comunidad** — UNA página agregada de prueba social. **No** páginas por alumno.
6. **Galería** — fotos de campo y generaciones.
7. **Contacto** — form nativo + WhatsApp + email + redes.

*(El "Aula Virtual" NO es una página: es el botón del header al login de celebios.online.)*
*(Opcional fase 2: sección "Recursos/Blog" para tráfico orgánico SEO — no en este alcance.)*

### Estructura de la página de Inicio (orden recomendado)
1. **Hero** — identidad + tagline + foto potente de fauna + CTA primario "Ver diplomados" + secundario WhatsApp.
2. **Tira de aliados** — justo bajo el hero (autoridad arriba para público escéptico).
3. **Convocatoria abierta** — banda del diplomado activo con CTA fuerte (fácil de actualizar).
4. **Oferta educativa** — grid de **4–6 tarjetas representativas** (no las 14) + "Ver todas".
5. **Por qué CELEBIOS** — 3–4 diferenciadores (aval/validez [placeholder], autores expertos, modalidad híbrida desde cualquier país LATAM, comunidad).
6. **Prueba social** — números placeholder + 2–3 testimonios **con atribución (nombre, profesión, país)**.
7. **FAQ** — dudas comunes (cómo funciona lo híbrido, certificado, pagos, países).
8. **Misión** — toque emocional: foto a pantalla completa + tagline.
9. **CTA final + footer** (contacto, redes).

## 7. Dirección visual / marca

- **Sensación:** autoridad académica + naturaleza viva. Serio y confiable, cálido y no acartonado. Mucho aire, jerarquía clara, fotografía de fauna protagonista.
- **Ignora cualquier design system de organización heredado;** la marca es la de CELEBIOS definida aquí + el logo que subo.
- **Color:** base en verde naturaleza profundo (institucional) + acento cálido (ámbar/terracota) para CTAs + neutros limpios. **Ajusta la paleta al logo real** y muéstrala. **Contraste AA obligatorio**; usa overlays/scrims sobre las fotos cuando haya texto encima.
- **Tipografía:** propón las combinaciones **después** de elegir dirección de Inicio (no en el primer turno), respetando fuentes del theme (sección 5).
- **Fotografía:** banco de fauna y generaciones que subo; trato editorial, no stock genérico.

## 8. Plantilla de Landing de curso (reutilizable)

Para una convocatoria activa, con reductores de fricción para público profesional:
- **Hero del diploma** (nombre + foto + CTA "Inscríbete").
- **¿Para quién es? / requisitos.**
- **Qué incluye / cómo funciona el acceso** (grabaciones + material + sesiones en vivo + certificado).
- **Temario / módulos.**
- **Profesores / autores** con credencial y foto.
- **Modalidad + precio** (ej. $[precio] MXN por módulo — placeholder).
- **Fechas / convocatoria** con urgencia ligera (cupo/fecha de inicio).
- **FAQ del curso** (pago, certificado, sesiones en vivo, países).
- **CTA "Inscríbete"** → celebios.online (con microcopy de continuidad).

## 9. SEO (el diseño debe habilitarlo)

- **Un solo H1 por página** + jerarquía correcta de H2/H3.
- Deja espacio/indicación para **title y meta-description por página**.
- **Alt text** descriptivo en todas las fotos (que el diseño contemple el campo).
- **Contenido como texto indexable**, no texto incrustado en imágenes.
- **Breadcrumbs** en catálogo y landing de curso; **slugs limpios** (ej. `/diplomados/rehabilitacion-fauna-silvestre`).
- Copy en **español neutro**; considera términos de búsqueda por país ("diplomado fauna silvestre", "rehabilitación de fauna online").

## 10. Referencias (usa SOLO los screenshots que subo)

- **Domestika / Platzi:** claridad del catálogo, tarjetas, jerarquía de landing de curso y CTAs de inscripción.
- **Sitio de conservación/naturaleza:** uso emocional de fotografía a pantalla completa y narrativa de misión.
- **celebios.com actual:** solo para ver el contenido y qué **NO** repetir (viejo, recargado, poca jerarquía).
- Si menciono una referencia y no subí su screenshot, **pídemela** en vez de inventarla de memoria.

## 11. Entregables

1. **Fase 1:** 2–3 variaciones del Hero + estructura del Inicio (desktop, baja fidelidad de contenido).
2. **Fase 2 (tras elegir):** Inicio en alta fidelidad → luego su versión mobile.
3. Resto de páginas clave con esa identidad + la **plantilla de landing de curso**.
4. **Mini design system:** paleta + tipografías (post-elección).
5. **Nombra y reutiliza componentes** (`hero-fauna`, `card-curso`, `tira-aliados`, `banner-convocatoria`, `bloque-stat`) para iterar por nombre.
6. **HTML exportado por secciones autocontenidas (CSS scopeado por sección)** + el mapeo de cada sección a su tipo Kajabi.

## 12. Qué NO hacer

- No inventar cifras, testimonios, "validez oficial", relaciones institucionales ni credenciales (usa placeholders / datos a confirmar).
- No proponer funciones fuera de Kajabi Basic (theme global, carruseles JS, mega-menús, formularios custom, mapas interactivos).
- No recrear las cientos de páginas individuales de egresados.
- No clonar las referencias: inspiración, no copia.

---

## Anexo — Notas de migración (NO es tarea de Claude Design; para el armado)

- **Dominio:** apuntar celebios.com al sitio Kajabi y retirar Wix solo después de tener el sitio listo.
- **Redirects 301:** inventariar URLs indexadas del Wix viejo (cursos, /nosotros, /contacto, y las cientos de egresados) y mapear 301 → equivalentes nuevas (las de alumnos individuales → /egresados). Sin esto se pierde el SEO existente.
- **Catálogo:** cada tarjeta de curso enlaza por **URL externa manual** a su landing en celebios.online (en Basic no hay sync automático de catálogo).
