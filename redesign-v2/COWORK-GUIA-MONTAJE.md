# CELEBIOS · Guía de montaje en Kajabi (para cowork)

> Documento auditado. Todo lo de aquí está verificado contra el sitio real (sitemap, renders en vivo, status HTTP). Donde algo depende de Ángel, está marcado **[ÁNGEL]**.

---

## 0) PROMPT (pégalo al inicio de la sesión de cowork)

```
Eres mi operador para terminar de montar el sitio de CELEBIOS en Kajabi
(plan Basic). El diseño ya está hecho: son 28 archivos HTML autocontenidos
en C:/Users/coche/Desktop/CELEBIOS-web/redesign-v2/kajabi/ (terminan en
.kajabi.html). Cada archivo se pega TAL CUAL en un bloque "Custom Code" de
una Landing Page de Kajabi. No edites el diseño ni el código del theme.

Tu trabajo, en orden:
  1. Re-pegar las 5 páginas del núcleo con su versión final (enlaces ya
     corregidos a slugs planos).
  2. Montar las 22 páginas que faltan (6 áreas + índice de blog + 16 artículos).
  3. Poner la Home (/home) como página de inicio del sitio.
  4. Despublicar/retirar las páginas viejas que siguen vivas.
  5. Verificar página por página con el checklist.

Sigue al pie de la letra la "Guía de montaje" (este documento). Usa SIEMPRE
el slug EXACTO de la tabla maestra. Si algo no coincide con lo descrito
(un botón distinto, Kajabi rechaza un slug, el bloque no se ve de borde a
borde), PARA y repórtalo en vez de improvisar. No inventes datos del negocio.
```

---

## 1) Contexto

- **CELEBIOS** = academia latinoamericana de **fauna silvestre** (cursos cortos online para MV y biólogos, avalada por CONCERVET). Pivote a "el Platzi de la fauna".
- **Plataforma:** Kajabi (plan Basic). El sitio vive en **celebios.online** (dominio final será **celebios.com [ÁNGEL]**).
- **Diseño:** sistema "Lámina Viva" (navy + cian + salvia, logo real embebido). Cada página es **un solo archivo autocontenido** (HTML+CSS+SVG+logo en base64) que se pega en **un bloque Custom Code**.
- **Archivos a pegar:** `C:/Users/coche/Desktop/CELEBIOS-web/redesign-v2/kajabi/*.kajabi.html` (28).

---

## 2) Estado actual (auditado)

| Cosa | Estado |
|---|---|
| Núcleo (Home, Catálogo, Curso gatos, Diplomado, Nosotros) | ✅ montado, **pero** con enlaces viejos → **re-pegar versión final** |
| 6 áreas + índice /recursos + 16 artículos | ❌ **404, faltan por montar** |
| Página de inicio `/` | ⚠️ muestra el **home VIEJO** (la Home nueva quedó en `/home`) |
| Páginas viejas (`/about`, `/nutricion2025`, `/nutricion2024`, `/nutricionfauna`, `/test`, `/store`, `/lenguaje-y-comunicacion-de-los-gatos`) | ⚠️ **siguen publicadas**, hay que retirarlas |
| Parche global (contraste + placeholders) | ✅ ya está en Settings → Site details → Header Page Scripts |

---

## 3) Reglas de oro (gotchas auditados — NO saltarse)

1. **Landing Pages**, no Website Pages. Cada página es una Landing nueva.
2. **Una Landing = un bloque Custom Code** con el archivo entero. Nada más.
3. **Plantilla "Blank"** (en blanco) al crear la Landing.
4. El archivo ya trae su propia **barra de navegación y footer** y un truco **full-bleed** para ocupar de borde a borde. NO añadas secciones extra arriba/abajo. Si Kajabi te muestra un header/footer del theme que duplica la nav → en *Page settings* de esa Landing **oculta header y footer**.
5. **Logo:** va embebido (base64). **No subas ninguna imagen.**
6. **Slug:** usa el EXACTO de la tabla (sección 6). Son **planos** (un segmento, sin "/"). Si Kajabi te obliga a algo distinto, **párate y reporta**.
7. **No toques el código del theme** (eso es Pro y rompe todo).
8. **CTAs:** hoy los botones "Inscribirme / Lista de espera" apuntan a slugs internos. Cuando existan los **Offers de pago [ÁNGEL]**, hay que re-apuntarlos al checkout del Offer (ver sección 11).
9. **No inventes datos.** Si ves "por confirmar" en una página, es a propósito (dato que Ángel aún no da). Déjalo.

---

## 4) Receta paso a paso (una página)

1. Kajabi → **Website** (menú izquierdo) → **Pages**.
2. **+ New Page → Landing Page → plantilla "Blank"**.
3. Ponle **nombre interno** (col. "Nombre" de la tabla) y abre el editor.
4. **Add Section → Custom Code** (o Add Block → Custom Code dentro de una sección en blanco).
5. Abre el `*.kajabi.html` correspondiente con Notepad → **Ctrl+A → Ctrl+C**.
6. Pega TODO dentro de la caja de Custom Code → **Apply/Save**.
7. **Page Settings → URL/slug** → escribe el slug EXACTO de la tabla (sin la diagonal inicial si Kajabi ya la pone).
8. *(Si aplica)* Page Settings → **oculta header/footer del theme** (regla 4).
9. **Publish**.
10. **Preview** → corre el checklist de la sección 10.

---

## 5) Orden de montaje recomendado

1. **Re-pegar el núcleo (5)** con la versión final (links ya planos): Home, Catálogo, Curso gatos, Diplomado, Nosotros.
2. **Áreas (6).**
3. **Índice de blog `/recursos`** + **16 artículos**.
4. **Set `/home` como homepage** (sección 8).
5. **Limpiar páginas viejas** (sección 9).

---

## 6) TABLA MAESTRA · archivo → slug → título → nombre interno

> El slug es la URL final (celebios.online/SLUG y luego celebios.com/SLUG).

### Núcleo (re-pegar con versión final)
| # | Archivo (`/kajabi/…`) | Slug | Título / Nombre interno |
|---|---|---|---|
| 1 | `lamina-viva.kajabi.html` | `home` *(→ marcar como homepage)* | Home — CELEBIOS |
| 2 | `catalogo.kajabi.html` | `cursos` | Catálogo de cursos |
| 3 | `curso-gatos.kajabi.html` | `curso-lenguaje-felino` | Curso · Lenguaje felino |
| 4 | `diplomado-rehab.kajabi.html` | `diplomado-rescate-rehabilitacion-fauna` | Diplomado · Rescate y rehabilitación |
| 5 | `nosotros.kajabi.html` | `nosotros` | Nosotros |

### Áreas / cursos cortos (6 nuevas)
| # | Archivo | Slug | Título |
|---|---|---|---|
| 6 | `curso-primeros-auxilios.kajabi.html` | `curso-primeros-auxilios` | Curso · Primeros auxilios de fauna |
| 7 | `curso-reptiles.kajabi.html` | `curso-reptiles` | Curso · Manejo de reptiles |
| 8 | `curso-ortopedia-aves.kajabi.html` | `curso-ortopedia-aves` | Curso · Ortopedia en aves |
| 9 | `curso-anestesia.kajabi.html` | `curso-anestesia` | Curso · Anestesia y contención |
| 10 | `curso-nutricion.kajabi.html` | `curso-nutricion` | Curso · Nutrición de fauna |
| 11 | `curso-manejo-conductual.kajabi.html` | `curso-manejo-conductual` | Curso · Manejo conductual |

### Blog (índice + 16 artículos)
| # | Archivo | Slug | Título |
|---|---|---|---|
| 12 | `recursos.kajabi.html` | `recursos` | Recursos (índice del blog) |
| 13 | `recurso-como-ser-rehabilitador.kajabi.html` | `recurso-como-ser-rehabilitador` | Cómo ser rehabilitador de fauna en México |
| 14 | `recurso-requisitos-rehabilitar.kajabi.html` | `recurso-requisitos-rehabilitar` | Requisitos para rehabilitar fauna en México |
| 15 | `recurso-liberar-fauna.kajabi.html` | `recurso-liberar-fauna` | Cómo liberar fauna correctamente (soft-release) |
| 16 | `recurso-animal-herido.kajabi.html` | `recurso-animal-herido` | Qué hacer si encuentras un animal herido |
| 17 | `recurso-triaje-fauna.kajabi.html` | `recurso-triaje-fauna` | Triaje de fauna: priorizar en una emergencia |
| 18 | `recurso-contencion.kajabi.html` | `recurso-contencion` | Contención física vs química |
| 19 | `recurso-dosis-anestesicas.kajabi.html` | `recurso-dosis-anestesicas` | Anestesia en fauna: principios de seguridad |
| 20 | `recurso-fractura-ala-ave.kajabi.html` | `recurso-fractura-ala-ave` | Fractura de ala en un ave: primeros pasos |
| 21 | `recurso-enfermedades-reptiles.kajabi.html` | `recurso-enfermedades-reptiles` | Enfermedades comunes en reptiles de cautiverio |
| 22 | `recurso-alimentacion-errores.kajabi.html` | `recurso-alimentacion-errores` | Errores al alimentar fauna en cautiverio |
| 23 | `recurso-enriquecimiento.kajabi.html` | `recurso-enriquecimiento` | Enriquecimiento ambiental para fauna |
| 24 | `recurso-que-es-concervet.kajabi.html` | `recurso-que-es-concervet` | Qué es CONCERVET y por qué importa |
| 25 | `recurso-cuanto-gana-veterinario.kajabi.html` | `recurso-cuanto-gana-veterinario` | Cuánto gana un veterinario de fauna |
| 26 | `recurso-lenguaje-corporal-gato.kajabi.html` | `recurso-lenguaje-corporal-gato` | Lenguaje corporal del gato |
| 27 | `recurso-por-que-maulla-gato.kajabi.html` | `recurso-por-que-maulla-gato` | Por qué mi gato maúlla tanto |
| 28 | `recurso-gato-estresado.kajabi.html` | `recurso-gato-estresado` | Cómo saber si mi gato está estresado |

---

## 7) Poner `/home` como página de inicio

1. Kajabi → **Website → Pages** → ubica la página **Home** (slug `home`).
2. Menú "⋯" de esa página → **"Set as homepage"** *(o Settings → Site details → campo "Homepage" → selecciónala)*.
3. Verifica: abre **celebios.online/** (raíz) → debe verse la Home nueva (hero "CELEBIOS: la academia de fauna silvestre…", no el home viejo).

---

## 8) Limpiar páginas viejas (retirar)

Estas siguen publicadas y confunden / compiten. **Despublica o borra** cada una *(no borres si tienes duda; despublicar basta)*:

- `/about` — plantilla default vieja (Kim)
- `/nutricionfauna`, `/nutricion2025`, `/nutricion2024` — convocatorias viejas
- `/test`, `/store` — pruebas/placeholder
- `/lenguaje-y-comunicacion-de-los-gatos` — **OJO:** es la del curso de gatos vieja y **rankea #3 en Google**. NO la borres sin más → déjala para que **[ÁNGEL]** haga un **301 → /curso-lenguaje-felino** (no perder ese posicionamiento).

*(Cómo: Website → Pages → cada una → "⋯" → Unpublish.)*

---

## 9) Checklist de verificación (por página)

Por cada página, en Preview:
- [ ] El bloque se ve **de borde a borde** (no encajonado con márgenes blancos).
- [ ] El **logo** se ve arriba a la izquierda.
- [ ] La **nav** funciona (Cursos, Diplomado, Recursos, Nosotros) y lleva a las páginas correctas.
- [ ] **No** aparece texto "[CONFIRMAR…]" en morado (debe decir "por confirmar" sutil o nada).
- [ ] Los **botones cian** tienen **texto navy legible** (no blanco invisible).
- [ ] Los enlaces internos llevan al **slug correcto** (ver tabla).

Global, al terminar:
- [ ] `celebios.online/` muestra la Home nueva.
- [ ] Desde la Home, clic en una tarjeta de curso → abre el área correcta.
- [ ] En `/cursos`, las tarjetas de área abren (ya no dan 404).
- [ ] En `/recursos`, las 16 tarjetas abren su artículo.
- [ ] Las páginas viejas ya no salen (o redirigen).

---

## 10) Pendientes que cowork NO resuelve (reportar a [ÁNGEL])

1. **Datos "por confirmar"**: RFC / razón social, fecha de la edición 2026, autores del blog, URL oficial CONCERVET, precios de las áreas. Cuando Ángel los dé → se actualizan los archivos fuente y se re-pega esa página.
2. **Dominio:** apuntar **celebios.com** a Kajabi (Settings → Domain) y hacer **301** de la vieja `/lenguaje-y-comunicacion-de-los-gatos`.
3. **Offers de pago:** crear los Offers en Kajabi y re-apuntar los CTAs "Inscribirme" al checkout (el checkout vive en celebios.online/offers/…).
4. **Search Console:** enviar el sitemap y verificar el dominio (el código de verificación se pega en el mismo Header Page Scripts).

---

## 11) Dónde está todo (rutas)

- **Archivos a pegar:** `C:/Users/coche/Desktop/CELEBIOS-web/redesign-v2/kajabi/` → los `*.kajabi.html` (28). Ignora `PROOF-…` (es copia de prueba).
- **Parche global (ya pegado):** `…/kajabi/GLOBAL-fix-pegar-una-vez.html` → Settings → Site details → Header Page Scripts.
- **Fuente editable** (por si hay que regenerar): los `*.html` en `…/redesign-v2/` + el script `celebios_pack_flat.py`.
- **Datos reales del negocio:** `…/redesign-v2/DATOS-REALES-harvest.md`.
- **Estrategia SEO/copy:** `…/redesign-v2/SEO-COPY-STRATEGY.md`.

---

*Auditado el 2026-06-20. Verificado: receta de montaje (núcleo ya vive así), slugs planos sin colisiones, 28 archivos con logo embebido + full-bleed + sin comillas tipográficas + 0 enlaces rotos.*
