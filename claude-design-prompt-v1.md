# Prompt para Claude Design — Sitio web CELEBIOS (v1, pre-audit)

> Pegar este prompt en Claude Design (claude.ai/design). Antes de enviarlo, sube como contexto: (1) el logo de CELEBIOS en vectorial/PNG alta, (2) 8–12 fotos del Facebook /celebi0s (fauna, prácticas de campo, generaciones de alumnos), (3) un screenshot del sitio actual celebios.com para que vea de dónde partimos.

---

## Rol y objetivo

Eres un diseñador de producto senior especializado en sitios para instituciones educativas. Diseña el **sitio web público de CELEBIOS**, una academia latinoamericana de educación continua en ciencias biológicas y salud animal. El sitio reemplaza un sitio viejo de Wix y se va a **construir en Kajabi** (lee la sección "Restricción de implementación" — es obligatoria). Quiero un diseño moderno, con autoridad académica y a la vez calidez por la fauna, que convierta visitas en inscripciones a diplomados.

Empieza simple (layout y contenido core), hazme preguntas si algo no queda claro, y muéstrame **2–3 variaciones de la página de inicio** antes de profundizar.

## Qué es CELEBIOS (usa estos datos reales, no inventes)

- **Nombre completo:** Centro Latinoamericano de Estudios en Ciencias Biológicas y de la Salud Animal (CELEBIOS S.C.).
- **Tagline:** "Eliminando fronteras, acercando al mundo."
- **Misión:** Formar individuos con conocimientos y habilidades específicas en las áreas biológicas y de la salud animal, que les permitan resolver problemas reales en el manejo y conservación de fauna.
- **Qué ofrece:** Diplomados y cursos (modalidad híbrida: clases grabadas donde los autores explican a profundidad + material de apoyo + sesiones en vivo). Diploma con validez oficial. Ejemplos reales de diplomados: Rehabilitación de Fauna Silvestre · Nutrición y Alimentación de Fauna Silvestre en Cautiverio · Contención Química y Anestesia de Fauna Silvestre · Medicina Preventiva y Manejo en Cautiverio · Manejo Conductual de Fauna · Ortopedia de Aves · Medicina Interna de Pequeñas Especies · Imagenología · Bioética · Félidos · SIG y manejo de datos de percepción remota.
- **Aliados institucionales (logos, prueba social):** Universidad Autónoma del Estado de Hidalgo (UAEH), UNAM, COMVEPEH, Bio Animal Wild.
- **Plataforma de cursos:** celebios.online (Kajabi) — ahí viven el login, el catálogo de cursos y el checkout. El sitio público debe **enviar tráfico hacia allá** para inscripciones, y al "Aula Virtual" (login) para alumnos.
- **Contacto:** contacto@celebios.com · WhatsApp +52 958 103 3574 · Instagram @celebios_edu · Facebook /celebi0s.

> Datos a NO inventar: número de egresados, países, años de operación, testimonios. Donde quieras usar cifras de prueba social, déjalas como **placeholders editables** (ej. "+[N] egresados de [N] países") para que el cliente las complete.

## Audiencia

Profesionales y estudiantes de habla hispana en toda Latinoamérica (México, Colombia, Perú, Ecuador y más): médicos veterinarios, biólogos, ecólogos, ingenieros ambientales/forestales, personal de zoológicos/santuarios y estudiantes de últimos semestres de estas carreras. Buscan especializarse en fauna silvestre con respaldo académico serio. Muchos llegan desde el celular y desde redes sociales.

## Objetivo de conversión (en orden)

1. **Inscripción a un diplomado/curso** → CTA hacia la landing del curso en celebios.online.
2. **Lead por WhatsApp** (dudas previas a inscribirse).
3. **Acceso de alumnos** al Aula Virtual (login en celebios.online).

## Restricción de implementación (OBLIGATORIA — Kajabi)

El diseño debe poder **construirse en Kajabi con un theme gratis + page builder por secciones + CSS personalizado por página**. NO habrá edición del código global del theme. Por lo tanto:

- Arma el diseño como **secciones apilables** estándar: hero, texto+imagen, grid de imágenes/galería, fila de tarjetas (cursos), tira de logos (aliados), acordeón/FAQ, testimonios, banner CTA, formulario de contacto, footer.
- Evita interacciones que dependan de JS complejo o de tocar el theme (carruseles exóticos, animaciones de scroll avanzadas, layouts imposibles de reproducir con secciones). Mejoras ligeras vía CSS por página están bien.
- Entrega cada página clave en **desktop y mobile** (mobile-first; gran parte del tráfico es móvil).
- Mantén tipografías y colores como un sistema simple y consistente que se pueda configurar en los ajustes del theme.

## Arquitectura del sitio (páginas a diseñar)

1. **Inicio** — la más importante.
2. **Nosotros** — misión/visión, breve historia, presidente (MenMVZ Miguel A. Galindo Bustos), aliados.
3. **Diplomados y Cursos** — catálogo (grid de tarjetas). Cada tarjeta lleva a su landing/curso en celebios.online.
4. **Landing de curso** (diseña 1 plantilla reutilizable) — para una convocatoria activa: hero del diploma, para quién es, temario/módulos, modalidad, precio (ej. $[precio] MXN por módulo), profesores/autores, fechas, CTA "Inscríbete" → celebios.online.
5. **Egresados / Comunidad** — UNA página agregada de prueba social (números placeholder, fotos de generaciones, mapa o lista de países, testimonios). NO páginas individuales por alumno.
6. **Galería** — fotos de campo y generaciones (del Facebook).
7. **Contacto** — formulario + WhatsApp + email + redes + ubicación si aplica.
8. **Aula Virtual** — bloque/CTA que manda al login de celebios.online.

### Estructura sugerida de la página de Inicio (enfoque híbrido: autoridad + conversión)

- **Hero**: nombre/identidad + tagline + fotografía potente de fauna + CTA primario "Ver diplomados" y secundario "Hablar por WhatsApp".
- **Convocatoria abierta**: banda destacando el diplomado activo con CTA fuerte (debe poder actualizarse fácil).
- **Oferta educativa**: grid de tarjetas de diplomados con ícono/foto, nombre y "Ver más".
- **Por qué CELEBIOS**: 3–4 diferenciadores (validez oficial, autores expertos, modalidad híbrida, comunidad LATAM).
- **Aliados**: tira de logos (UAEH, UNAM, COMVEPEH, Bio Animal Wild).
- **Prueba social**: números placeholder + 2–3 testimonios.
- **Misión** (toque emocional, foto a pantalla completa, tagline).
- **CTA final** + footer con contacto y redes.

## Dirección visual / marca

- **Sensación:** autoridad académica + naturaleza viva. Serio y confiable, pero cálido y no acartonado. Mucho aire, jerarquía clara, foto de fauna como protagonista.
- **Color:** base en verde naturaleza profundo (institucional) + un acento cálido (ámbar/terracota) para CTAs + neutros limpios. Ajusta la paleta al logo real que subo; propón la paleta final y muéstrala.
- **Tipografía:** propón 2 combinaciones — una con serif de autoridad para títulos + sans limpia para cuerpo, y otra 100% sans moderna. Que se vean bien en español (acentos, ñ).
- **Fotografía:** usa el banco de fotos de fauna y generaciones que subo (Facebook). Trato editorial, no stock genérico.

## Referencias (te subo screenshots; toma de cada una lo indicado)

- **Domestika / Platzi** (ed-tech en español): claridad del catálogo de cursos, tarjetas, jerarquía de landing de curso y CTAs de inscripción.
- **Sitios de conservación/naturaleza** (ej. organizaciones de vida silvestre): uso emocional de fotografía a pantalla completa y narrativa de misión.
- **Sitio actual celebios.com** (te lo subo): solo para que veas el contenido y qué NO repetir (se ve viejo, recargado, poca jerarquía).

## Entregables

1. 2–3 variaciones de la **página de inicio** (desktop + mobile).
2. Una vez elegida la dirección: el resto de páginas clave con esa misma identidad.
3. La **plantilla reutilizable de landing de curso**.
4. La paleta + tipografías como mini design system.
5. Al final, exportable a **HTML** para usarlo como referencia exacta al armar en Kajabi.

## Qué NO hacer

- No inventar cifras, testimonios ni datos del cliente (usa placeholders).
- No proponer funciones que Kajabi (theme gratis + page builder + CSS por página) no pueda construir.
- No recrear las cientos de páginas individuales de egresados del sitio viejo.
- No copiar literal las referencias; inspiración, no clonación.

## Arranque

Confírmame que entendiste la restricción de Kajabi y la audiencia, hazme las preguntas que necesites, y arranca mostrándome **2–3 variaciones de la página de inicio** en desktop y mobile.
