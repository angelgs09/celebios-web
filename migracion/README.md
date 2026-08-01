# Inventario SEO de migración — Wix + Kajabi → sitio nuevo

Contrato de redirects para retirar `celebios.com` (Wix) y, más adelante,
`celebios.online` (Kajabi) sin perder el tráfico que ya tienen indexado.

## Cómo se generó

```
pip install -r requirements.txt
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
- **destination_path**: ruta raíz-relativa contra la arquitectura de
  información FINAL planeada del sitio nuevo (no el sitio actual — ver
  `DESTINOS_BASE_VALIDOS` en el script). Puede traer un fragmento (`#...`)
  que Task 3 implementa como ancla; la base antes del `#` siempre es una de:
  `/`, `/aula`, `/cursos`, `/curso-lenguaje-felino`, `/historia`,
  `/egresados`, `/practicas-de-campo`, `/docentes`, `/admisiones`,
  `/contacto`, `/aviso-de-privacidad`. Nunca es `/` salvo la propia home.
- **clicks, impressions, position, backlinks**: **vacíos a propósito.** No
  hay una sesión autenticada de Google Search Console ni de Wix Analytics
  todavía — importar ese export es un paso externo pendiente, y no se
  inventan métricas para llenar la tabla.
- **confidence**: `alta` para mapeos explícitos o basura de editor curada a
  mano; `media` para páginas de egresado con año de cohorte o tema inferido
  con evidencia en la URL; `baja` para páginas de egresado sin ninguna
  evidencia inferible (solo un nombre propio en el slug).
- **manual_review**: `true` únicamente cuando `confidence` es `baja` — hoy
  eso son las páginas de egresado que solo traen un nombre propio en el
  slug (van a `/egresados` sin ancla, pero conviene revisar a mano si algún
  caso amerita una ancla que el script no pudo inferir).

## Categorías

| category | Significa | status_code típico |
|---|---|---|
| `home` | La raíz del sitio. | 301 → `/` |
| `curso_disponible` | Lenguaje y Comunicación de los Gatos — el único curso a la venta hoy. | 301 → `/curso-lenguaje-felino` |
| `curso_historico` | Programa, diplomado o catálogo histórico. | 301 → `/cursos#historico-<tema>` (o `/cursos` si es el catálogo/calendario) |
| `institucional` | Nosotros→historia, contacto, aviso de privacidad, aula, docentes, prácticas de campo, admisión. | 301 a la página viva correspondiente |
| `egresado` | Perfil o certificado individual de egresado. Nunca expone el nombre de la persona en `topic_or_cohort` ni en el destino. | 301 → `/egresados`, `/egresados#cohorte-YYYY` o `/egresados#tema-<tema>` según lo que sea inferible con confianza |
| `sin_equivalente` | Basura real del editor de Wix/Kajabi: `blank`, `copia-de-*`, `keeper`, `galeria-N`, `/test`. Sin contenido real. | 404 |

Una página de egresado con año de cohorte reconocible en la URL
(`/vazquez-santiago-2016`) preserva ese valor con
`/egresados#cohorte-2016`; una con un tema de curso reconocible pero sin año
(`/egresadosbioetica`) usa `/egresados#tema-bioetica`; una sin ninguna señal
(`/lopez-hernandez`) cae en `/egresados` sin ancla, con `confidence=baja` y
`manual_review=true`. El apellido nunca se copia a `topic_or_cohort` ni al
destino.

Un certificado cuya URL trae un curso reconocible pero no el prefijo
`egresados`/`gen<año>` (ej. `/felidos-torres-barraza`,
`/ortopedia-lopez-hernandez`) se clasifica por ese curso histórico, igual
que cualquier otra cohorte del mismo programa: cae en `curso_historico` con
`/cursos#historico-<tema>`.

**Regla de negocio explícita:** solo Lenguaje y Comunicación de los Gatos
está disponible para inscripción. Ningún otro curso o diplomado se redirige
a `/` — cada uno cae en su ancla de archivo histórico en `/cursos`.

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
