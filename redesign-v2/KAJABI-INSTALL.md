# CELEBIOS — Instalación en Kajabi Basic

Sitio "Lámina Viva" (5 páginas), construido para **Kajabi Basic** con bloques de **Custom Code**.
Cada página se instala como una **Landing Page** con un bloque de Custom Code que trae su propio diseño (header, contenido, footer).

## Lo que tienes
| Página | Archivo paste-ready | Slug sugerido |
|---|---|---|
| Home | `kajabi/lamina-viva.kajabi.html` | `/` |
| Catálogo | `kajabi/catalogo.kajabi.html` | `/cursos` |
| Curso (Gatos, plantilla) | `kajabi/curso-gatos.kajabi.html` | `/curso-lenguaje-felino` |
| Diplomado (Rehab) | `kajabi/diplomado-rehab.kajabi.html` | `/diplomado-rehabilitacion` |
| Nosotros | `kajabi/nosotros.kajabi.html` | `/nosotros` |

> Los archivos `*.html` (sin `.kajabi`) son para previsualizar en el navegador. Los `kajabi/*.kajabi.html` son lo que se PEGA en Kajabi.

---

## Paso 0 — Subir el logo (1 vez)
1. En Kajabi sube el archivo **`brand/logo-white.png`** (logo blanco para fondo oscuro) a una imagen/recurso y **copia su URL** pública.
   - Truco: crea un bloque de Imagen en cualquier página, sube el PNG, y copia la URL del `<img>`.
2. Guarda esa URL. La usarás como **`{{LOGO_URL}}`** en cada página (aparece 2 veces por página: header y footer).

## Paso 1 — Theme (mínimo)
- Elige cualquier **theme gratis**. No dependemos de él: nuestras páginas traen su propio header/footer.
- En cada Landing Page, **oculta el header y footer del theme** (ajustes de la página) para que no se dupliquen con los nuestros. Si Basic no deja ocultarlos del todo, usa la plantilla de landing más limpia/en blanco.
- Sube el **favicon** (logo) en ajustes del sitio.

## Paso 2 — Crear cada página (×5)
Para cada fila de la tabla:
1. **New → Landing Page → en blanco**.
2. Ponle el **slug** sugerido.
3. En el editor, agrega un bloque **Custom Code** a todo el ancho.
4. Abre el archivo `kajabi/<pagina>.kajabi.html`, **copia TODO** y **pégalo** en el bloque.
5. En ese bloque, **reemplaza `{{LOGO_URL}}`** por la URL del logo del Paso 0 (2 ocurrencias).
6. **Guarda** y **previsualiza**.

> Las fuentes (Bricolage Grotesque / Instrument Sans / Space Grotesk) cargan solas desde Google Fonts (van en el bloque). La ilustración es SVG inline (no hay que subir nada).

## Paso 3 — Productos y checkout (cap 5 en Basic)
Da de alta como **productos/ofertas** SOLO los cursos **Disponibles** (los "Próxima/En producción" son tarjetas de marketing, no productos):
- **Lenguaje Felino** → ya tienes la oferta: `https://www.celebios.online/offers/pp4ZMos3`
- **Diplomado Rehab**, **Primeros Auxilios**, **Manejo de Reptiles** → crea oferta/checkout.
Luego, en cada bloque pegado, cambia los CTA **"Inscribirme"** (hoy van a `celebios.online` o a `mailto:`) por la **URL real de checkout** de cada curso.

## Paso 4 — Lista de espera (Próxima / En producción)
- Crea un **Form** en Kajabi (nombre + correo + "curso de interés").
- Los botones **"Avisarme" / "Lista de espera"** hoy abren un `mailto:contacto@celebios.com` con asunto prellenado. Si prefieres capturar en Kajabi, cámbialos por el enlace/popup de ese Form (así alimentas tus contactos y mides demanda = qué producir primero).

## Paso 5 — Dominio
- Apunta **celebios.com** a este sitio Kajabi (Settings → Domains). (celebios.online sigue para checkout/cursos.)

## Paso 6 — Revisar nav
- Los enlaces de la nav ya apuntan a los slugs sugeridos (`/cursos`, `/diplomado-rehabilitacion`, `/nosotros`, `/`). Si usas otros slugs, ajústalos en cada bloque (busca `href="/cursos"`, etc.).

---

## Pendientes antes del launch real
- **Ilustración:** hoy es placeholder (SVG line-art simple). Para verse pro necesitas el **set ilustrado a medida** (8-12 especies LATAM, validado por un MVZ). Se reemplazan los `<svg class="specimen">` por las ilustraciones reales.
- **Datos a confirmar (de tu propio sitio, scrape ~26-may):** docente de Gatos (Máster UAB / "Miaulogía"), avales y aliados, precios, fechas de "Próxima edición". Verifica que sigan vigentes.
- **Cap de 5 productos:** cuando tengas >5 cursos vendibles, sube a **Growth**.
- Quitar branding de Kajabi requiere **Growth+**.
