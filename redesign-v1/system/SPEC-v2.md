# CELEBIOS — Spec de construcción v2 (contrato para builders)

Consolidación de las 3 investigaciones (CRO/Neil Patel · Design Language · Motion). Todo portable a **Kajabi Basic** (CSS/JS por página, sin theme global, sin backend; checkout/login en celebios.online).

## Sistema compartido (NO editar; solo enlazar)
Cada página enlaza, en este orden:
```html
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="tokens-v2.css">   <!-- desde /system: href="tokens-v2.css" -->
<link rel="stylesheet" href="motion.css">
```
(Si la página vive en la raíz del proyecto: `href="system/tokens-v2.css"` etc.)

`tokens-v2.css` ya aplica: ámbar=acento (de-ambar de convocatoria/cta-final a verde), escala tipográfica con contraste, surface cálido en cards, grade de marca (`.img-grade`,`.veil`,`.grain`), estados a11y, placeholders `.phbox`.
`motion.css` ya aplica (por clase, casi automático): reveal de carga hero, Ken Burns, **scroll-reveal nativo `view()`**, cascada de cards, clip-path en imágenes, parallax sutil, sheen en CTA, pulso de convocatoria, FAQ height, **sticky-cta móvil**, micro-interacciones.

## Reglas de oro
- **Ámbar ≤10% de superficie**: solo CTA primario, subrayado nav activo, `●` convocatoria, números stats, comilla. NADA de fondos ámbar plenos. (Quitar cualquier `background:var(--amber-500)` inline de convocatoria/cta-final.)
- **Un CTA primario dominante por pantalla.** WhatsApp y "Aula Virtual" = links subordinados (no botón sólido), no compiten con "Ver diplomados/Inscríbete".
- **Itálicas Spectral** solo en hero + misión (firma). Testimonios → roman.
- **Fotos**: aplicar `.img-grade` + velo verde; en hero/misión ir como `background-image` (para velo/grano). Cada `.curso__img` con `object-position` propio.
- **Accesibilidad**: `:focus-visible` (ya en sistema), `prefers-reduced-motion` (ya), contraste AA (nunca texto ámbar sobre fondo claro; ámbar solo sobre verde oscuro).
- **Placeholders se MANTIENEN** (`.phbox` "+N", "[fecha]", "[institución a confirmar]") — los datos duros van en otra fase. Que se vean intencionales, no rotos.
- **Mapeo Kajabi**: cada `<section data-kajabi="...">` con su tipo (Hero/Cards/Accordion/CTA/Footer). HTML troceado por sección autocontenida.

## Páginas a construir
### A) Home v2 (`inicio-v2.html`, base: inicio-max.html)
Estructura B+heroA + upgrades: hero full-bleed (guacamaya) con grade+grano y CTA único + WhatsApp como link · **strip de logos de aliados bajo hero** (usar `.allies`/`.ally` ya en tokens.css) · convocatoria (verde, no ámbar) · oferta (cards foto+grade, cascada) · por qué (números grandes Spectral rompiendo margen, oldstyle) · **franja fotográfica full-bleed** entre egresados y FAQ · egresados (stats + testimonios roman con atribución placeholder) · FAQ · misión full-bleed con grano · CTA final (verde) + footer · **sticky-cta móvil** (`.sticky-cta` con "Ver diplomados") · **menú móvil** (hamburguesa simple, hoy `.nav` se oculta sin alternativa).

### B) Landing de curso (`curso-template.html`, plantilla reutilizable)
Orden CRO: hero de curso (nombre + outcome 1 línea + meta horas/módulos/modalidad + CTA + microcopy de fecha) · ¿para quién es?/requisitos · qué incluye (grabadas+material+sesiones vivo+diploma) · **temario por módulos (accordion `<details>`)** · profesores con credencial (foto+nombre+título+"autor de") · modalidad + precio (`$[precio]` MXN, placeholder) · fechas/urgencia honesta · FAQ del curso · prueba social (1 testimonio cerca del CTA) · **CTA "Inscríbete" → celebios.online con microcopy de continuidad** ("Te llevamos al pago seguro · apartas tu cupo al registrarte") · sticky-cta móvil. Mismo sistema/tokens/motion.

## Close-gates (cada checkpoint debe pasar)
1. Enlaza los 3 CSS compartidos; sin estilos que dupliquen/peleen con el sistema.
2. Ámbar solo como acento (cero fondos ámbar plenos).
3. Un CTA primario por pantalla; WhatsApp/Aula Virtual subordinados.
4. Render sin secciones en blanco (animaciones degradan a contenido visible).
5. `prefers-reduced-motion` y `:focus-visible` operativos.
6. Cada sección con `data-kajabi`; HTML válido; imágenes con `alt`.
7. Mobile: sticky-cta visible <760px, nav accesible, sin overflow horizontal.
8. Placeholders presentes pero con estilo `.phbox` (no texto roto).
