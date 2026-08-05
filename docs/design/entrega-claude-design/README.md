# La entrega de Claude Design — 5 de agosto de 2026

Proyecto: `dd273dcc-4219-48ac-8901-109281194077` · "CELEBIOS project status".
Se lee y se escribe con la herramienta `DesignSync` (MCP `claude_design`, añadido
al config de usuario el 4-ago). Todo lo que hay allá sigue accesible; aquí solo
está copiado el entregable, que es lo que no conviene depender de una conexión.

## Cómo verlo

El `.dc.html` no se abre solo: necesita `support.js` a su lado y servirse por
HTTP, más los assets en rutas relativas. Para levantarlo:

```
# desde una carpeta temporal con el .dc.html, support.js,
# brand/logo-celebios{,-blanco}.png y redesign-v2/{fonts,media}/
python -m http.server 8902
```

Mide **29,049 px de alto**. No es una página: es el lienzo con todos los
artboards apilados, en el orden en que se fueron entregando.

## Qué contiene, por altura

| y aprox. | Qué |
|---|---|
| 0 – 1,650 | Login: "nadie tiene contraseña", entrar con correo, revisar correo |
| 1,650 – 3,000 | El correo de migración: "tu aula se mudó, tu acceso no cambia" |
| 3,000 – 4,400 | Primer paso para los siete que nunca entraron |
| 4,400 – 5,650 | La constancia, para los veintidós que llegaron al 100% |
| 5,650 – 7,150 | Hoja de movimiento: las cuatro animaciones, en vivo |
| 7,150 – 9,500 | La Introducción (sección 00 de 12) y el resultado del examen |
| 9,500 – 11,100 | Hoja de estados interactivos |
| **11,100 – 13,800** | **Home** |
| **13,800 – 15,780** | **Catálogo** |
| **15,780 – 17,480** | **Ficha de curso — el que sí se vende** |
| **17,480 – 19,880** | **Ficha del diplomado — la que no vende** |
| 19,880 – 23,600 | Las cuatro anteriores a 390 px |
| 23,600 – 29,000 | Aula: entrada, módulo y cierre, en ambos anchos |

## Los documentos que lo acompañan

Viven en el proyecto de Claude Design, no aquí (se leen con `DesignSync`
`get_file`):

- **`TOKENS-Y-COMPONENTES.md`** — el que manda para portar. Tokens de color,
  tipografía, espaciado, radios, estados y movimiento, más la tabla de qué
  componente cambia y cuál se queda. Incluye dos confesiones útiles: los ratios
  de contraste están **calculados, no verificados en navegador**, y hay valores
  de espaciado fuera de la base 4 (18, 22, 26, 30, 34) que hay que redondear al
  portar.
- **`ATLAS-PROGRAMAS.md`** — dieciséis ediciones fechadas entre 2010 y 2019,
  sacadas de `celebios.com/galeria-1`. Corrige el inventario de imágenes: el
  diplomado de contención química **sí se impartió** (1ª generación, ago–dic
  2017, 38 alumnos), aunque su cartel diga "próximamente".
- **`HALLAZGO-NUTRICION.md`** — `celebios.online/nutricion2025` sigue viva,
  indexable y con formulario de inscripción abierto, vendiendo un diplomado
  cerrado con tres precios. Fuera del repo, pero hay que apagarla antes del 30
  de agosto.
- **`AUDITORIA-REFERENCIAS.md`** — sin leer todavía.
- **`Archivo - Home tres direcciones.dc.html`** — las tres direcciones que
  compitieron para la home, archivadas.

## Estado

**Entregado y aprobado por Angel. Sin portar.** El HTML de Claude Design es
maqueta: se porta a mano a CSS vanilla en `redesign-v2/`, se pasa por las 324
pruebas y se verifica en navegador antes de publicar.
