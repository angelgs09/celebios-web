# Inventario SEO de migración — Wix + Kajabi → sitio nuevo

Contrato de redirects para retirar `celebios.com` (Wix) y, más adelante,
`celebios.online` (Kajabi) sin perder el tráfico que ya tienen indexado.

## Cómo se generó

```
pip install requests
python scripts/sync_migration_inventory.py
```

El script descarga en vivo `https://www.celebios.com/sitemap.xml` (Wix, un
sitemap-index que apunta a `pages-sitemap.xml`) y
`https://www.celebios.online/sitemap.xml` (Kajabi), clasifica cada URL con
`classify_source()` y escribe tres CSV con las mismas columnas:

| Archivo | Contenido |
|---|---|
| `urls-wix.csv` | Snapshot completo del sitemap de Wix. |
| `urls-kajabi.csv` | Snapshot completo del sitemap de Kajabi. |
| `redirects.csv` | Unión de los dos anteriores: el contrato completo. |

Snapshot del 2026-08-01: **371 URLs en Wix, 15 en Kajabi.** Si el sitio vivo
cambia, correr el script otra vez regenera los tres archivos — no se edita
el CSV a mano.

## Columnas

`source_url,destination_path,status_code,category,topic_or_cohort,clicks,impressions,position,backlinks,priority,confidence,manual_review`

- **status_code**: `301` si hay `destination_path`, `404` si no.
- **destination_path**: ruta raíz-relativa del sitio nuevo. Nunca es `/`
  salvo la propia home; nunca es una URL arbitraria de relleno.
- **clicks, impressions, position, backlinks**: **vacíos a propósito.** No
  hay una sesión autenticada de Google Search Console ni de Wix Analytics
  todavía — importar ese export es un paso externo pendiente, y no se
  inventan métricas para llenar la tabla.
- **manual_review**: `true` en las filas donde no hay un destino seguro que
  ofrecer (hoy solo `/aviso-de-privacidad`: el sitio nuevo no tiene todavía
  página de privacidad, así que queda en 404 marcada para revisión en vez de
  redirigirse a algo que no corresponde).

## Categorías

| category | Significa | status_code típico |
|---|---|---|
| `home` | La raíz del sitio. | 301 → `/` |
| `curso_disponible` | Lenguaje y Comunicación de los Gatos — el único curso a la venta hoy. | 301 → `/curso-lenguaje-felino` |
| `curso_historico` | Cualquier otro curso, diplomado o cohorte (disponible como página informativa o no). | 301 → la página del curso si existe, si no al catálogo `/cursos` |
| `institucional` | Nosotros, contacto, aviso de privacidad, aula. | 301 a la página viva, o 404 + `manual_review` si no hay una todavía |
| `sin_equivalente` | Certificados de egresados individuales sin ningún curso reconocible en la URL (ej. `/lopez-hernandez`), y páginas de andamiaje del editor de Wix (`blank`, `copia-de-*`, `keeper`, `galeria-1`, …). Sin valor de negocio y sin nombres propios en `topic_or_cohort`. | 404 |

Una certificación individual cuya URL sí trae un curso reconocible (ej.
`/felidos-torres-barraza`, `/ortopedia-lopez-hernandez`) se clasifica por ese
curso, no por el nombre: cae en `curso_historico` y 301 a su destino, igual
que cualquier otra cohorte de ese mismo curso. El apellido nunca se copia a
`topic_or_cohort`. Solo cuando la URL no trae ninguna señal de curso
(`/lopez-hernandez`) se considera sin equivalente y va a 404.

**Regla de negocio explícita:** solo Lenguaje y Comunicación de los Gatos
está disponible para inscripción. Ningún otro curso o diplomado se redirige
a `/` — cada uno cae en su página informativa si el sitio nuevo ya la
construyó, o en el catálogo `/cursos` como destino histórico.

## Lo que este inventario NO hace

- No modifica `aula/`, Supabase, exámenes, videos, importadores, exports de
  Kajabi, DNS ni el estado de ninguna cuenta.
- No escribe redirects en `vercel.json` — `redirects.csv` es el contrato de
  datos; conectarlo al build es un paso posterior.
- No recolecta contenido de las páginas de egresados (nombres, textos): solo
  su URL, que es lo único necesario para decidir el código de redirect.

## Pendiente externo

Antes del corte real (apuntar `celebios.com` al sitio nuevo) hace falta
importar clicks/impressions/position desde un export autenticado de Search
Console y Wix Analytics, y backlinks desde alguna herramienta de SEO. Ese
paso no se puede automatizar sin esa sesión — se deja documentado, no
fabricado.
