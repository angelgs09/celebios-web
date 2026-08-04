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
| `redirects.csv` | El contrato completo. Nace de la unión de los dos anteriores, pero **ya no es idéntico**: 5 filas se corrigieron a mano al decidir destinos (`/nosotros`, `/galeria-1`, `/about`, `/diplomado-rescate-rehabilitacion-fauna`, `.online/nosotros`), así que volver a correr el script sobrescribe esas decisiones. |

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
- **clicks, impressions, position, backlinks**: **vacíos a propósito.** Desde
  el 2026-08-01 sí existe la propiedad `sc-domain:celebios.com` en Google
  Search Console (verificada con un TXT en el DNS de Wix), pero al 2026-08-02
  sigue procesando datos y no hay export descargable — propiedad verificada no
  es dato disponible, así que estas columnas siguen vacías. Importar ese export
  sigue siendo un paso externo pendiente y no se inventan métricas para llenar
  la tabla. El export autenticado de Wix Analytics (Page Visits) ya se importó
  por separado — ver "Pendiente externo" más abajo — pero esa métrica no
  llena estas columnas: mide tráfico de página, no señal de búsqueda
  orgánica de Google.
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

## Del contrato al build (ya conectado)

Este CSV dejó de ser solo un contrato de datos en el commit `af7b766`
("establish verified content and build contracts"): `build.py` lo consume.

- El `vercel.json` generado declara las reglas **inline**, en `redirects`, con
  `{source, destination, statusCode: 301}` (`build.generar_vercel_json`).
  **No** usa `bulkRedirectsPath`: el deploy del 2026-08-03 lo dejó en los logs
  — "Bulk redirects are not available for teams on the Hobby plan" — y esa
  propiedad no publicaba ni una sola regla. El esquema de Vercel admite hasta
  2048 inline, y el build revienta si el inventario las rebasa.
- Por lo mismo, el build ya **no** escribe `site/migracion/redirects.csv`: no
  lo leía nadie y publicaba 17 KB con el mapa completo de la migración.
- `build.convertir_redirects_bulk` decide qué entra.

Cifras del 2026-08-04, contra el CSV comiteado y las 33 rutas canónicas que hoy
publica `redesign-v2/`. Son un snapshot que se mueve conforme Task 3 publica
páginas; para recalcularlas sin escribir en `site/`:

```python
import csv, build
publicadas = set(build.rutas_canonicas_fuente())
with open("migracion/redirects.csv", encoding="utf-8") as f:
    activas, diferidas = build.convertir_redirects_bulk(list(csv.DictReader(f)), publicadas)
print(len(activas), len(diferidas))
```

| | Filas |
|---|---|
| Filas en `migracion/redirects.csv` | 386 |
| — con `status_code=404` (no generan regla) | 5 |
| — con `status_code=301` | 381 |
| Descartadas: origen igual al destino | 11 |
| **Reglas activas emitidas** | **368** |
| **Reglas diferidas (no se emiten)** | **0** |

Una regla se DIFIERE si su origen ya es una página publicada (la sombrearía) o
si la base de su destino todavía no se publica (sería un 301 a un 404); `/aula`
es la única excepción explícita. **Hoy no queda ninguna diferida**: las 33
páginas publicadas cubren todos los destinos, incluidos `/egresados` (161
reglas), `/admisiones` (14) y `/contacto`, que en agosto todavía no existían.

`python build.py --cutover` revienta si queda alguna diferida, así que ese 0 es
la condición que ya se cumple para el corte. Un mismo origen con dos destinos
distintos también revienta el build, en cualquier modo.

## Lo que este inventario NO hace

- No modifica `aula/`, Supabase, exámenes, videos, importadores, exports de
  Kajabi, DNS ni el estado de ninguna cuenta.
- No escribe reglas `redirects[]` a mano en `vercel.json`, ni se edita el CSV a
  mano: el contrato de datos vive aquí y el build lo traduce (ver "Del contrato
  al build" arriba).
- No recolecta contenido de las páginas de egresados (nombres, textos): solo
  su URL, que es lo único necesario para decidir el código de redirect.

## Pendiente externo

Antes del corte real (apuntar `celebios.com` al sitio nuevo) hace falta
importar clicks/impressions/position desde un export autenticado de Search
Console, y backlinks desde alguna herramienta de SEO. Ese paso depende de que
Google entregue datos y de una descarga manual — se deja documentado, no
fabricado.

**Wix Analytics (Page Visits) ya se importó, parcialmente.** El 2026-08-01 se
importó el primer export autenticado: `Page Visits` del sitio Wix `celebios`,
copiado byte a byte en
`migracion/evidencia/wix-page-visits-2025-08-02_2026-08-02.csv` y normalizado
por `scripts/import_wix_traffic.py` en
`migracion/wix-page-visits-normalized.csv` (152 filas,
`source_url,page_views,site_sessions,unique_visitors,period_start,period_end,inventory_match`,
join de solo lectura contra `urls-wix.csv` sin cambiar su esquema). El detalle
completo — hash, totales de resumen, discrepancia entre el período mostrado en
la UI y el expresado en el nombre del archivo — vive en
`migracion/wix-analytics-manifest.json`.

Esto **no** es evidencia de Google Search Console: page views de Wix miden
tráfico de página, no clicks/impressions/position de búsqueda orgánica. Este
sitio Wix sigue sin estar conectado a GSC (`Top Search Queries on Google` no
disponible ahí).

**Estado de Search Console al 2026-08-02.** La propiedad `sc-domain:celebios.com`
existe y está verificada desde el 2026-08-01 (TXT en el DNS de Wix), **y aun así
el gate sigue BLOQUEADO**: Rendimiento, Indexación, Enlaces y Mejoras muestran
"Se están procesando los datos", sus tablas dicen "Sin datos" y EXPORTAR está
deshabilitado en Rendimiento y en Enlaces. Lo único con cifras es el informe
HTTPS (28 URLs), que es estado de certificado, no una métrica de búsqueda. Sin
export, las columnas `clicks`, `impressions`, `position` y `backlinks` de este
inventario siguen vacías a propósito y `cutover_allowed` en el manifiesto queda
en `false`: el corte real sigue bloqueado hasta que la propiedad entregue datos,
se importen y se aprueben.
