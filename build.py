#!/usr/bin/env python3
"""Arma el sitio publico de CELEBIOS para Vercel desde redesign-v2/.

Cada pagina aterriza en la ruta que dice su propio <link rel="canonical">, y
todos los enlaces internos se reescriben a rutas ABSOLUTAS: con cleanUrls una
ruta relativa se resuelve contra el directorio, asi que "catalogo.html" dentro
de /cursos/anestesia-contencion-fauna apuntaria a /cursos/catalogo.html.

Uso:  python build.py          -> arma site/ y verifica
      python build.py --check  -> solo verifica lo que ya esta en site/
"""
import csv
import json
import os
import re
import shutil
import sys
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "redesign-v2"
OUT = RAIZ / "site"
DOMINIO = "https://www.celebios.com"
CONTENIDO_PROGRAMAS = RAIZ / "contenido" / "programas.json"
REDIRECTS_CSV = RAIZ / "migracion" / "redirects.csv"

CANONICAL = re.compile(r'<link[^>]*rel=["\']canonical["\'][^>]*>', re.I)
HREF_CANON = re.compile(r'href=["\']([^"\']+)["\']', re.I)
MARCA = "\x00CANONICAL\x00"

# `planned` se agrega el 2026-08-02, desviandose del enum cerrado del plan
# (available/historical), y la razon esta documentada: dos programas no son
# ninguna de las dos cosas. Nacieron como ejemplos de catalogo en la ronda de
# diseno de junio, con precio placeholder; no hay ni una prueba de que se
# hayan impartido, y su propio HTML dice "Edicion en preparacion". Marcarlos
# `historical` afirmaba una imparticion que nadie puede respaldar, y marcarlos
# `available` habria sido peor. Un estado que dice la verdad es mejor que un
# enum bonito. `planned` tiene exactamente las mismas restricciones que
# `historical`: sin oferta, sin precio, sin CTA de inscripcion.
ESTADOS_VALIDOS = {"available", "historical", "planned"}
ESTADOS_SIN_OFERTA = {"historical", "planned"}
CAMPOS_REQUERIDOS = {
    "slug", "title", "status", "category", "topic",
    "summary", "evidence", "interest_topic",
}
CAMPOS_OFFER = {"price_mxn", "payment_type", "hours", "topics_count", "access_months"}
TIPOS_OFFER = {
    "price_mxn": int, "hours": int, "topics_count": int, "access_months": int,
    "payment_type": str,
}
CAMPOS_REDIRECT = {"source_url", "destination_path", "status_code"}
EVIDENCIA_ANCLA_RE = re.compile(r'^(?P<path>[^#]+)#L(?P<inicio>\d+)(?:-L(?P<fin>\d+))?$')
GA4_RE = re.compile(r'G-[A-Z0-9]+')

# Afirmaciones que INVESTIGACION.md (tabla "Rechazadas") descarto por falta de
# evidencia, y que el plan prohibe publicar. Limpiarlas del HTML no basta: sin
# esta guarda, la siguiente persona que reescriba una plantilla las reintroduce
# y nadie se entera hasta que ya estan en produccion. Los patrones aceptan la
# forma con y sin tilde porque el JSON-LD de las maquetas va sin tildes.
FRASES_RECHAZADAS = [
    (re.compile(r'[úu]nica\s+academia', re.I),
     "superlativo de exclusividad sin fuente"),
    (re.compile(r'validez\s+oficial', re.I),
     "'validez oficial' es un termino legal (RVOE/SEP) que ninguna fuente confirma"),
    (re.compile(r'\d+\s+especialistas', re.I),
     "conteo de docentes sin fuente"),
]

# Una tarjeta de catalogo que se anuncia disponible. El contrato de datos vive
# en contenido/programas.json, pero lo que se publica es el HTML: sin esta
# guarda los dos pueden divergir, y de hecho divergieron (el catalogo anunciaba
# como disponibles, con precio, tres programas que el contrato marca historicos).
TARJETA_DISPONIBLE_RE = re.compile(
    r'<article\b[^>]*\bdata-estado="disp"[^>]*>.*?</article>', re.S | re.I
)
TARJETA_RE = re.compile(r'<article\b[^>]*>.*?</article>', re.S | re.I)
HREF_RE = re.compile(r'href="([^"#?]+\.html)', re.I)
# La otra mitad de la restriccion: un programa historico no lleva precio. Los
# de Primeros Auxilios ($1,200) y Reptiles ($1,600) eran placeholders de una
# ronda de diseno y se publicaron un mes como si fueran oferta real.
PRECIO_RE = re.compile(r'\$\s?[\d,]+\s*(?:MXN|USD)\b', re.I)


def ruta_canonica(html):
    """La ruta que la pagina declara para si misma, o None si no declara."""
    tag = CANONICAL.search(html)
    if not tag:
        return None
    href = HREF_CANON.search(tag.group(0))
    if not href:
        return None
    return href.group(1).replace(DOMINIO, "").rstrip("/") or "/"


def archivo_destino(ruta):
    """/ -> index.html ; /cursos -> cursos.html ; /a/b -> a/b.html"""
    return "index.html" if ruta == "/" else ruta.lstrip("/") + ".html"


def rutas_canonicas_fuente():
    """El conjunto de rutas canonicas que redesign-v2 declara hoy (las
    paginas reales, sin maquetas sin canonical). Es contra esto que se valida
    la consistencia canonica de contenido/programas.json."""
    rutas = set()
    for f in SRC.glob("*.html"):
        ruta = ruta_canonica(f.read_text(encoding="utf-8"))
        if ruta:
            rutas.add(ruta)
    return rutas


def cargar_programas(path=CONTENIDO_PROGRAMAS):
    datos = json.loads(Path(path).read_text(encoding="utf-8"))
    # ValueError, no KeyError: construir() solo atrapa ValueError, y un KeyError
    # sale como traceback crudo en vez del 'ERROR: ...' legible.
    if not isinstance(datos, dict) or "programas" not in datos:
        raise ValueError(f"{path}: falta la clave 'programas'")
    return datos["programas"]


def _validar_evidencia(slug, fuente):
    """fuente debe ser 'path#Lx' o 'path#Lx-Ly' (ancla de linea auditable), o
    una URL publica http(s) ya formateada con claridad. Revienta si el
    archivo base no existe, si el rango de lineas es invalido, o si el rango
    citado esta vacio (sin texto)."""
    # fullmatch, no match: con '$' un '\n' final se cuela (igual que en validar_ga4).
    if fuente.startswith(("http://", "https://")):
        if not re.fullmatch(r'https?://\S+', fuente):
            raise ValueError(f"{slug}: evidencia URL mal formateada: {fuente}")
        return

    m = EVIDENCIA_ANCLA_RE.fullmatch(fuente)
    if not m:
        raise ValueError(
            f"{slug}: evidencia sin ancla de linea (formato esperado 'path#Lx' o 'path#Lx-Ly'): {fuente}"
        )
    ruta = RAIZ / m.group("path")
    if not ruta.exists():
        raise ValueError(f"{slug}: evidencia inexistente: {fuente}")

    # Una pagina no puede ser su propia evidencia. Dos programas se sostenian
    # citando la linea del <link rel="canonical"> de la maqueta que este mismo
    # redisenio escribio, o sea nada. Los .md de redesign-v2 (el harvest de
    # redes) si valen: son registro de fuentes externas, no maquetas.
    if ruta.suffix.lower() == ".html" and SRC in ruta.parents:
        raise ValueError(
            f"{slug}: evidencia circular, es una maqueta del propio redisenio: {fuente}"
        )

    lineas = ruta.read_text(encoding="utf-8").splitlines()
    inicio = int(m.group("inicio"))
    fin = int(m.group("fin") or inicio)
    if inicio < 1 or fin < inicio or fin > len(lineas):
        raise ValueError(
            f"{slug}: rango de linea invalido en {fuente} (archivo tiene {len(lineas)} lineas)"
        )
    if not any(l.strip() for l in lineas[inicio - 1:fin]):
        raise ValueError(f"{slug}: rango de linea citado esta vacio: {fuente}")


def validar_programas(programas, rutas_validas=None):
    """Revienta con ValueError ante cualquier violacion del contrato de
    contenido/programas.json: campos requeridos, enum cerrado de status, un
    solo disponible, cierre estricto de campos por status, oferta con forma
    exacta, evidencia con ancla de linea auditable, slugs unicos y
    consistencia canonica contra redesign-v2."""
    if rutas_validas is None:
        rutas_validas = rutas_canonicas_fuente()

    slugs_vistos = set()
    disponibles = []
    for p in programas:
        if "slug" not in p:
            raise ValueError("programa sin campo requerido 'slug'")
        slug = p["slug"]
        if slug in slugs_vistos:
            raise ValueError(f"slug duplicado: {slug}")
        slugs_vistos.add(slug)

        faltantes = CAMPOS_REQUERIDOS - p.keys()
        if faltantes:
            raise ValueError(f"{slug}: faltan campos requeridos: {sorted(faltantes)}")

        if p["status"] not in ESTADOS_VALIDOS:
            raise ValueError(f"status invalido en {slug}: {p['status']!r}")

        permitidos = CAMPOS_REQUERIDOS | ({"offer"} if p["status"] == "available" else set())
        extra = p.keys() - permitidos
        if extra:
            raise ValueError(f"{slug}: campos no permitidos para status={p['status']!r}: {sorted(extra)}")

        if p["status"] == "available":
            disponibles.append(p)
            offer = p.get("offer")
            if not isinstance(offer, dict) or offer.keys() != CAMPOS_OFFER:
                raise ValueError(
                    f"{slug}: 'offer' debe traer exactamente {sorted(CAMPOS_OFFER)}, trae {sorted((offer or {}).keys())}"
                )
            for campo, tipo in TIPOS_OFFER.items():
                valor = offer[campo]
                # isinstance(True, int) es True: un booleano no es un precio ni unas horas.
                if not isinstance(valor, tipo) or isinstance(valor, bool):
                    raise ValueError(
                        f"{slug}: offer.{campo} debe ser {tipo.__name__}, trae {valor!r}"
                    )
                if tipo is int and valor <= 0:
                    raise ValueError(f"{slug}: offer.{campo} debe ser > 0, trae {valor!r}")
                if tipo is str and not valor.strip():
                    raise ValueError(f"{slug}: offer.{campo} no puede ir vacio")

        evidencia = p.get("evidence") or []
        if not evidencia:
            raise ValueError(f"{slug} no trae evidencia")
        for fuente in evidencia:
            _validar_evidencia(slug, fuente)

        if slug not in rutas_validas:
            raise ValueError(f"{slug} no tiene pagina canonica en {SRC}")

    if len(disponibles) != 1:
        raise ValueError(f"debe haber exactamente 1 programa disponible, hay {len(disponibles)}")


def generar_sitemap(rutas):
    """XML de sitemap a partir de rutas canonicas ya publicadas. /aula nunca
    entra (no tiene canonical) y 404 tampoco (no es una pagina real de
    redesign-v2); si algo las pasara igual, se filtran aqui por si acaso."""
    entradas = sorted(
        r for r in rutas
        if r != "/404" and not r.startswith("/aula")
    )
    urls = "".join(
        f"  <url><loc>{escape(DOMINIO + ('' if r == '/' else r) + ('/' if r == '/' else ''))}</loc></url>\n"
        for r in entradas
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}"
        '</urlset>\n'
    )


def generar_robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /aula\n"
        "Disallow: /api\n"
        "\n"
        f"Sitemap: {DOMINIO}/sitemap.xml\n"
    )


def generar_404():
    return (
        '<!doctype html>\n'
        '<html lang="es">\n'
        '<head>\n'
        '  <meta charset="utf-8">\n'
        '  <title>Pagina no encontrada · CELEBIOS</title>\n'
        '  <meta name="robots" content="noindex">\n'
        '</head>\n'
        '<body>\n'
        '  <h1>404 — No encontramos esta pagina</h1>\n'
        '  <p>El enlace que seguiste no existe o ya no esta disponible.</p>\n'
        '  <p><a href="/">Volver al inicio de CELEBIOS</a></p>\n'
        '</body>\n'
        '</html>\n'
    )


# Tope del propio esquema de Vercel para `redirects` (openapi.vercel.sh/vercel.json,
# maxItems). Si el inventario lo rebasa, el CSV deja de caber inline y la unica
# salida es bulkRedirectsPath, que es de pago.
MAX_REDIRECTS_INLINE = 2048


def generar_vercel_json(reglas=()):
    """`redirects` inline, NO bulkRedirectsPath.

    El deploy del 2026-08-03 lo dejo claro en los logs: "Bulk redirects are not
    available for teams on the Hobby plan". La cuenta esta en Hobby, asi que
    esa propiedad no publicaba ni una sola regla.

    Inline si funciona en Hobby y el esquema admite hasta 2048 reglas. Se emite
    `statusCode` en vez de `permanent`, porque `permanent: true` responde 308 y
    el inventario dice 301: son equivalentes para SEO, pero el contrato del CSV
    es explicito y no hay razon para traicionarlo."""
    if len(reglas) > MAX_REDIRECTS_INLINE:
        raise SystemExit(
            f"ERROR: {len(reglas)} redirects exceden el tope de {MAX_REDIRECTS_INLINE} "
            f"que Vercel admite en vercel.json. Haria falta bulkRedirectsPath (plan Pro)."
        )
    config = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        # Lo que se publica ya esta construido. Sin esto Vercel autodetecta el
        # package.json y corre un build que no tiene nada que construir.
        "buildCommand": "",
        "cleanUrls": True,
        "trailingSlash": False,
        "redirects": [
            {"source": r["source"], "destination": r["destination"],
             "statusCode": r["statusCode"]}
            for r in reglas
        ],
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {"key": "X-Content-Type-Options", "value": "nosniff"},
                    {"key": "X-Frame-Options", "value": "DENY"},
                    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                ],
            },
            {
                "source": "/brand/(.*)",
                "headers": [
                    {"key": "Cache-Control", "value": "public, max-age=3600, stale-while-revalidate=86400"},
                ],
            },
            # La copia de revision en *.vercel.app no se indexa, y el sitio real
            # si. Va condicionado al host y NO como noindex global ni como
            # Disallow en robots.txt, porque las dos alternativas son trampas:
            # habria que acordarse de quitarlas el dia del cutover, y nadie se
            # acuerda. Asi la regla simplemente deja de coincidir cuando el
            # dominio sea celebios.com.
            #
            # Hace falta ademas del canonical: los canonical apuntan a
            # www.celebios.com/<ruta>, y esas rutas hoy NO existen (ahi sigue el
            # Wix viejo). Un canonical que apunta a un 404 lo ignora Google, y
            # entonces indexa la copia de revision.
            {
                "source": "/(.*)",
                "has": [{"type": "host", "value": "(.*)\\.vercel\\.app"}],
                "headers": [
                    {"key": "X-Robots-Tag", "value": "noindex, nofollow"},
                ],
            },
        ],
    }
    return json.dumps(config, indent=2, ensure_ascii=False) + "\n"


def url_a_ruta(url):
    """https://www.celebios.com/x -> /x ; https://www.celebios.com -> /"""
    return re.sub(r'^https?://[^/]+', '', url) or "/"


def _ruta_base(destino):
    """/cursos#historico-x -> /cursos ; /egresados?x=1 -> /egresados"""
    return re.split(r"[#?]", destino, maxsplit=1)[0] or "/"


def _normalizar_ruta(ruta):
    """Clave de comparacion (no de emision): /Nosotros/ -> /nosotros. Misma
    forma canonica que normalize_source_url en scripts/sync_migration_inventory.py."""
    return ruta.rstrip("/").lower() or "/"


def convertir_redirects_bulk(filas, rutas_publicadas):
    """migracion/redirects.csv (source_url,destination_path,status_code,...)
    -> formato bulk de Vercel [{source,destination,statusCode}]. Solo 301 con
    destino no vacio; sin auto-redirects (origen == destino tras normalizar a
    ruta); duplicados identicos se colapsan; un mismo origen con destinos
    distintos revienta (dos hosts viejos no pueden pelear la misma ruta).

    rutas_publicadas es el conjunto de rutas canonicas que este build esta
    publicando ahora mismo. Una regla se DIFIERE (no se emite) en vez de
    publicarse si su origen es hoy una pagina publicada (la sombrearia) o si
    la base de su destino no esta publicada todavia (301 a un 404), salvo
    '/aula', que es un destino real preservado aunque no tenga canonical.

    Devuelve (reglas_activas, reglas_diferidas); reglas_diferidas trae
    {source, destination, reasons} para que quien llame decida si eso es
    aceptable (preview) o debe reventar el build (--cutover)."""
    # Se compara contra las rutas publicadas ya normalizadas para que la
    # comparacion sea simetrica con la clave del origen. El DESTINO se compara
    # sin normalizar a proposito: es la URL que se emitiria tal cual, asi que si
    # viene con otra caja o slash final se difiere en vez de publicar un 301 que
    # puede caer en 404.
    publicadas = {_normalizar_ruta(r) for r in rutas_publicadas}
    vistos = {}
    activas = []
    diferidas = []
    for fila in filas:
        faltantes = CAMPOS_REDIRECT - fila.keys()
        if faltantes:
            raise ValueError(f"fila sin columnas requeridas: {sorted(faltantes)}")
        if str(fila["status_code"]) != "301":
            continue
        destino = fila["destination_path"]
        if not destino:
            continue
        origen = url_a_ruta(fila["source_url"])
        clave = _normalizar_ruta(origen)
        if clave == destino:
            continue
        if clave in vistos:
            if vistos[clave] != destino:
                raise ValueError(
                    f"conflicto: {origen} -> {vistos[clave]!r} y -> {destino!r}"
                )
            continue
        vistos[clave] = destino

        razones = []
        if clave in publicadas:
            razones.append("source_shadows_published_page")
        base = _ruta_base(destino)
        if base not in publicadas and base != "/aula":
            razones.append("destination_not_published")

        if razones:
            diferidas.append({"source": origen, "destination": destino, "reasons": razones})
            continue
        activas.append({"source": origen, "destination": destino, "statusCode": 301})
    return activas, diferidas


def validar_ga4(measurement_id):
    if measurement_id is not None and not GA4_RE.fullmatch(measurement_id):
        raise ValueError(f"GA4_MEASUREMENT_ID invalido: {measurement_id!r}")


def inyectar_ga4(html, measurement_id):
    """Sin measurement_id, el HTML no cambia (sin analytics). Con uno valido,
    inyecta el loader estandar de gtag.js antes de </head>: sin user_id ni
    ninguna propiedad de usuario/PII."""
    if not measurement_id:
        return html
    snippet = (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>\n'
        '<script>\n'
        "  window.dataLayer = window.dataLayer || [];\n"
        "  function gtag(){dataLayer.push(arguments);}\n"
        "  gtag('js', new Date());\n"
        f"  gtag('config', '{measurement_id}');\n"
        '</script>\n'
    )
    return html.replace('</head>', snippet + '</head>', 1)


def reescribir(html, mapa):
    # El canonical debe conservar el dominio absoluto: lo saco de la jugada.
    tag = CANONICAL.search(html)
    canonical_original = tag.group(0) if tag else None
    if canonical_original:
        html = html.replace(canonical_original, MARCA, 1)

    # nombre-viejo.html -> /ruta/canonica, conservando #ancla y ?query
    for viejo, ruta in mapa.items():
        html = re.sub(
            r'(href|src)=["\']' + re.escape(viejo) + r'([#?][^"\']*)?["\']',
            lambda m: f'{m.group(1)}="{ruta}{m.group(2) or ""}"',
            html,
        )

    # Enlaces ya absolutos al dominio -> raiz-relativos, para que el deploy de
    # preview sea navegable antes de que el DNS apunte a Vercel.
    for attr in ("href", "src"):
        html = html.replace(f'{attr}="{DOMINIO}/', f'{attr}="/')
        html = html.replace(f'{attr}="{DOMINIO}"', f'{attr}="/"')

    # Assets relativos -> absolutos (misma razon que los enlaces).
    for attr in ("href", "src"):
        html = html.replace(f'{attr}="brand/', f'{attr}="/brand/')

    if canonical_original:
        html = html.replace(MARCA, canonical_original, 1)
    return html


def buscar_frases_rechazadas(paginas):
    """[(archivo, linea, texto, motivo)] por cada afirmacion rechazada que
    seguiria publicandose. Se busca en la fuente de redesign-v2 y no en la
    salida porque `reescribir` solo toca enlaces: la prosa publicada es la
    misma, y asi se puede reventar antes de escribir nada en disco."""
    hallados = []
    for f in sorted(paginas, key=lambda p: p.name):
        for i, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for patron, motivo in FRASES_RECHAZADAS:
                m = patron.search(linea)
                if m:
                    hallados.append((f.name, i, m.group(0), motivo))
    return hallados


def buscar_disponibilidad_falsa(paginas, programas):
    """[(archivo, linea, destinos)] por cada tarjeta de catalogo que se anuncia
    disponible sin enlazar a ningun programa que el contrato marque disponible.

    El contrato de datos (contenido/programas.json) y el HTML publicado son dos
    fuentes de verdad distintas y pueden divergir. Divergieron: el catalogo
    anunciaba como disponibles, con precio, el diplomado de $19,500 y dos cursos
    marcados historicos. Falla cerrado: una tarjeta 'disp' cuyo enlace no se
    puede resolver cuenta como violacion."""
    disponibles = {p["slug"] for p in programas if p["status"] == "available"}
    mapa = {f.name: ruta for f, ruta in paginas.items()}
    hallados = []
    for f in sorted(paginas, key=lambda p: p.name):
        texto = f.read_text(encoding="utf-8")
        for m in TARJETA_DISPONIBLE_RE.finditer(texto):
            destinos = {mapa.get(h) for h in HREF_RE.findall(m.group(0))}
            destinos.discard(None)
            if not (destinos & disponibles):
                linea = texto.count("\n", 0, m.start()) + 1
                hallados.append((f.name, linea, sorted(destinos)))
        # Un precio en una tarjeta que solo apunta a programas historicos es la
        # misma afirmacion de disponibilidad, dicha con dinero en vez de con un
        # pill: lo cazamos aunque la tarjeta no se marque 'disp'.
        for m in TARJETA_RE.finditer(texto):
            if not PRECIO_RE.search(m.group(0)):
                continue
            destinos = {mapa.get(h) for h in HREF_RE.findall(m.group(0))}
            destinos.discard(None)
            if destinos and not (destinos & disponibles):
                linea = texto.count("\n", 0, m.start()) + 1
                if not any(h[:2] == (f.name, linea) for h in hallados):
                    hallados.append((f.name, linea, sorted(destinos)))
    return hallados


def buscar_oferta_en_historicos(paginas, programas):
    """[(archivo, motivo)] por cada pagina de un programa historico que publica
    una oferta: `offers` en JSON-LD, o un precio que no sea el del unico
    programa disponible (esas paginas si pueden cruzar-vender el curso de
    gatos, y por eso su precio se permite).

    El caso que motivo la guarda: la pagina del diplomado declaraba un Offer
    con `availability: InStock` y precios 19500/26000 para un programa cuya
    edicion cerro el 30-jun-2025. Structured data es lo que Google lee como
    producto comprable, asi que el dano no depende de lo que diga el texto."""
    disponibles = [p for p in programas if p["status"] == "available"]
    precios_ok = {
        f"${p['offer']['price_mxn']:,} MXN".lower()
        for p in disponibles if isinstance(p.get("offer"), dict)
    }
    historicos = {p["slug"] for p in programas if p["status"] in ESTADOS_SIN_OFERTA}
    hallados = []
    for f in sorted(paginas, key=lambda p: p.name):
        if paginas[f] not in historicos:
            continue
        texto = f.read_text(encoding="utf-8")
        if re.search(r'"offers"\s*:', texto):
            hallados.append((f.name, "JSON-LD con 'offers' en un programa historico"))
        ajenos = {
            p for p in PRECIO_RE.findall(texto)
            if re.sub(r"\s+", " ", p).strip().lower() not in precios_ok
        }
        if ajenos:
            hallados.append((f.name, f"precio propio en un programa historico: {sorted(ajenos)}"))
    return hallados


def package_json_de_salida():
    """El package.json que se publica, derivado del de la raiz.

    Copiarlo tal cual reventaba el deploy: arrastra `"build": "python
    build.py"`, asi que Vercel intentaba reconstruir un sitio YA construido,
    desde un directorio donde `redesign-v2/` no existe -- `npm run build`
    salia con codigo 2 y el despliegue moria antes de servir nada.

    El output solo necesita lo que la funcion de `api/` requiere para
    compilar: sus dependencias y el tipo de modulo. Como construirse no es
    asunto suyo, ya esta construido."""
    fuente = json.loads((RAIZ / "package.json").read_text(encoding="utf-8"))
    salida = {
        "private": True,
        "name": fuente["name"],
        "description": fuente["description"],
        "type": fuente["type"],
        "dependencies": fuente["dependencies"],
    }
    return json.dumps(salida, ensure_ascii=False, indent=2) + "\n"


def buscar_paginas_huerfanas(paginas):
    """[ruta] de paginas publicadas a las que no llega ningun enlace interno.

    Una pagina huerfana existe en el sitemap pero no en el sitio: Google la
    descubre sin contexto ni autoridad, y un visitante no puede llegar a ella
    navegando. Paso de verdad: /egresados nacio huerfana aun siendo el destino
    de 234 reglas de redirect."""
    rutas = set(paginas.values())
    entrantes = {ruta: 0 for ruta in rutas}
    por_nombre = {f.name: paginas[f] for f in paginas}
    for f, propia in paginas.items():
        for destino in set(HREF_RE.findall(f.read_text(encoding="utf-8"))):
            ruta = por_nombre.get(destino.split("/")[-1])
            if ruta is not None and ruta != propia:
                entrantes[ruta] += 1
    return sorted(ruta for ruta, n in entrantes.items() if n == 0)


# Una fecha de apertura anunciada con verbo: "Abre Sep 2026", "Inicia Oct 2026".
# No toca fechas en pasado ni fechas sueltas, que son hechos historicos legitimos
# ("la 3a edicion cerro en jun 2025").
APERTURA_RE = re.compile(
    r"(?:Abre|Inicia|Comienza|Arranca|Empieza)\s*(?:</span>)?\s*"
    r"(?:Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\.?\s+20\d\d",
    re.I,
)
# Cuanto texto despues de la fecha se admite para encontrar el marcador. Da para
# el cierre de un par de <span> y el "por confirmar"; no para la siguiente celda.
_MARGEN_MARCADOR = 90


def buscar_fecha_sin_confirmar(paginas):
    """[(archivo, linea, texto)] de fechas de apertura publicadas sin el
    marcador "por confirmar".

    redesign-v2/COWORK-GUIA-MONTAJE.md lista "fecha de la edicion 2026" entre
    los datos que Angel todavia no ha dado, y fija el marcador como la forma
    de publicarlo: "si ves 'por confirmar' en una pagina, es a proposito".
    Una fecha sin el se lee como compromiso firme. Esto no se detecto solo:
    la tarjeta de Manejo Conductual perdio el marcador al copiarse del
    catalogo a dos fichas de curso, y esa es la lamina con mas trafico."""
    hallados = []
    for f in sorted(paginas, key=lambda p: p.name):
        for n, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in APERTURA_RE.finditer(linea):
                if "por confirmar" in linea[m.start():m.end() + _MARGEN_MARCADOR].lower():
                    continue
                hallados.append((f.name, n, re.sub(r"\s+", " ", m.group(0)).strip()))
    return hallados


def buscar_anclas_sin_destino(reglas, paginas):
    """[(source, destination)] de las reglas activas cuyo fragmento no existe
    como id en la pagina destino.

    Un 301 a /cursos#historico-x cuando ese id no existe no rompe nada: el
    navegador aterriza arriba de /cursos. Por eso en preview solo se reporta.
    En --cutover si revienta: a esas alturas la promesa del contrato de
    redirects tiene que estar cumplida, no aproximada."""
    por_ruta = {ruta: f for f, ruta in paginas.items()}
    ids_por_ruta = {}
    sin_destino = []
    for regla in reglas:
        if "#" not in regla["destination"]:
            continue
        base, ancla = regla["destination"].split("#", 1)
        base = base or "/"
        if base not in por_ruta:
            continue          # ya lo cubre el diferimiento por destino ausente
        if base not in ids_por_ruta:
            texto = por_ruta[base].read_text(encoding="utf-8")
            ids_por_ruta[base] = set(re.findall(r'\bid="([^"]+)"', texto))
        if ancla not in ids_por_ruta[base]:
            sin_destino.append((regla["source"], regla["destination"]))
    return sin_destino


def construir(salida=None, cutover=False):
    salida = Path(salida) if salida is not None else OUT

    try:
        validar_programas(cargar_programas())
    except ValueError as e:
        raise SystemExit(f"ERROR: contenido/programas.json invalido: {e}")

    ga4_id = os.environ.get("GA4_MEASUREMENT_ID")
    try:
        validar_ga4(ga4_id)
    except ValueError as e:
        raise SystemExit(f"ERROR: {e}")

    paginas = {}
    for f in sorted(SRC.glob("*.html")):
        ruta = ruta_canonica(f.read_text(encoding="utf-8"))
        if ruta:
            paginas[f] = ruta
        else:
            print(f"  omitida (sin canonical, es maqueta): {f.name}")

    # Choque de rutas = dos paginas peleando la misma URL. Mejor reventar aqui.
    vistas = {}
    for f, ruta in paginas.items():
        if ruta in vistas:
            raise SystemExit(f"ERROR: {f.name} y {vistas[ruta].name} declaran {ruta}")
        vistas[ruta] = f

    # Restriccion global del plan: no se publican afirmaciones sin respaldo.
    # Va antes de tocar disco, igual que el gate de --cutover.
    rechazadas = buscar_frases_rechazadas(paginas)
    if rechazadas:
        detalle = "; ".join(
            f"{arch}:{ln} {txt!r} ({motivo})" for arch, ln, txt, motivo in rechazadas[:5]
        )
        mas = f" (+{len(rechazadas) - 5} mas)" if len(rechazadas) > 5 else ""
        raise SystemExit(
            f"ERROR: {len(rechazadas)} afirmacion(es) que INVESTIGACION.md rechazo "
            f"seguirian publicandose: {detalle}{mas}"
        )

    # Misma restriccion, otra cara: solo el curso de gatos puede anunciarse
    # disponible. El contrato lo dice en programas.json; esto lo hace valer en
    # lo que de verdad se publica, que es el HTML.
    falsas = buscar_disponibilidad_falsa(paginas, cargar_programas())
    if falsas:
        detalle = "; ".join(
            f"{arch}:{ln} -> {dest or 'sin destino resoluble'}" for arch, ln, dest in falsas[:5]
        )
        mas = f" (+{len(falsas) - 5} mas)" if len(falsas) > 5 else ""
        raise SystemExit(
            f"ERROR: {len(falsas)} tarjeta(s) se anuncian disponibles sin enlazar a un "
            f"programa disponible en contenido/programas.json: {detalle}{mas}"
        )

    huerfanas = buscar_paginas_huerfanas(paginas)
    if huerfanas:
        raise SystemExit(
            f"ERROR: {len(huerfanas)} pagina(s) publicadas sin ningun enlace interno "
            f"que lleve a ellas: {', '.join(huerfanas)}"
        )

    fechas = buscar_fecha_sin_confirmar(paginas)
    if fechas:
        detalle = "; ".join(f"{arch}:{ln} {txt!r}" for arch, ln, txt in fechas[:5])
        mas = f" (+{len(fechas) - 5} mas)" if len(fechas) > 5 else ""
        raise SystemExit(
            f"ERROR: {len(fechas)} fecha(s) de apertura se publican sin el marcador "
            f"'por confirmar': {detalle}{mas}"
        )

    ofertas = buscar_oferta_en_historicos(paginas, cargar_programas())
    if ofertas:
        detalle = "; ".join(f"{arch}: {motivo}" for arch, motivo in ofertas[:5])
        mas = f" (+{len(ofertas) - 5} mas)" if len(ofertas) > 5 else ""
        raise SystemExit(
            f"ERROR: {len(ofertas)} pagina(s) de programa historico publican una oferta: "
            f"{detalle}{mas}"
        )

    rutas_publicadas = set(paginas.values())
    with REDIRECTS_CSV.open(encoding="utf-8") as f:
        try:
            reglas_bulk, diferidas = convertir_redirects_bulk(list(csv.DictReader(f)), rutas_publicadas)
        except ValueError as e:
            raise SystemExit(f"ERROR: {REDIRECTS_CSV}: {e}")

    # La validacion de arriba no toca disco: si --cutover va a reventar,
    # revienta antes de tocar `salida`, para no dejar un build a medias.
    if cutover and diferidas:
        detalle = "; ".join(
            f"{d['source']} -> {d['destination']} ({'+'.join(d['reasons'])})"
            for d in diferidas[:5]
        )
        mas = f" (+{len(diferidas) - 5} mas)" if len(diferidas) > 5 else ""
        raise SystemExit(
            f"ERROR --cutover: {len(diferidas)} regla(s) de redirect diferida(s) "
            f"por conflicto con el build actual: {detalle}{mas}"
        )
    anclas_huerfanas = buscar_anclas_sin_destino(reglas_bulk, paginas)
    if cutover and anclas_huerfanas:
        detalle = "; ".join(f"{s} -> {d}" for s, d in anclas_huerfanas[:5])
        mas = f" (+{len(anclas_huerfanas) - 5} mas)" if len(anclas_huerfanas) > 5 else ""
        raise SystemExit(
            f"ERROR --cutover: {len(anclas_huerfanas)} regla(s) 301 apuntan a un ancla "
            f"que no existe en la pagina destino: {detalle}{mas}"
        )

    if diferidas:
        print(f"  {len(diferidas)} regla(s) de redirect diferida(s) (preview, no publicadas)")
    if anclas_huerfanas:
        print(f"  {len(anclas_huerfanas)} regla(s) 301 con ancla inexistente (preview; --cutover revienta)")

    mapa = {f.name: ruta for f, ruta in paginas.items()}

    # Se vacia el contenido en vez de borrar la carpeta entera, por dos
    # razones: .vercel guarda a que proyecto publica el CLI (si se pierde, el
    # deploy se va a un proyecto nuevo), y en Windows rmtree revienta si algun
    # proceso tiene la carpeta como directorio actual.
    salida.mkdir(parents=True, exist_ok=True)
    for hijo in salida.iterdir():
        if hijo.name == ".vercel":
            continue
        shutil.rmtree(hijo) if hijo.is_dir() else hijo.unlink()
    for f, ruta in paginas.items():
        html = reescribir(f.read_text(encoding="utf-8"), mapa)
        html = inyectar_ga4(html, ga4_id)
        destino = salida / archivo_destino(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html, encoding="utf-8")

    shutil.copytree(SRC / "brand", salida / "brand")

    # Fotos y carteles historicos rescatados del Wix vivo. Viven aqui y no en
    # static.wixstatic.com a proposito: si se cancela la cuenta de Wix, las
    # URLs de ese CDN mueren y con ellas el unico registro visual del archivo.
    shutil.copytree(SRC / "media", salida / "media")

    # El aula es estatica y va tal cual: no tiene canonical porque no debe
    # indexarse, asi que no pasa por el mapeo de rutas de arriba. Byte a byte,
    # sin tocar (ni GA4 le entra): es codigo fuente, no una vista publica.
    shutil.copytree(RAIZ / "aula", salida / "aula")

    # Lo unico que no es estatico: la funcion que firma las URLs de video.
    shutil.copytree(RAIZ / "api", salida / "api")
    (salida / "package.json").write_text(package_json_de_salida(), encoding="utf-8")

    (salida / "404.html").write_text(inyectar_ga4(generar_404(), ga4_id), encoding="utf-8")
    (salida / "sitemap.xml").write_text(generar_sitemap(paginas.values()), encoding="utf-8")
    (salida / "robots.txt").write_text(generar_robots(), encoding="utf-8")
    (salida / "vercel.json").write_text(generar_vercel_json(reglas_bulk), encoding="utf-8")

    (salida / "migracion").mkdir(parents=True, exist_ok=True)
    with (salida / "migracion" / "redirects.csv").open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["source", "destination", "statusCode"])
        escritor.writeheader()
        escritor.writerows(reglas_bulk)

    print(f"  {len(paginas)} paginas + sitemap/robots/404/vercel.json -> {salida}")
    print(f"  {len(reglas_bulk)} redirects activos, {len(diferidas)} diferidos")
    return paginas


def verificar(salida=None):
    """Ningun enlace interno puede apuntar a algo que no existe en site/."""
    salida = Path(salida) if salida is not None else OUT
    archivos = {
        "/" + p.relative_to(salida).as_posix().removesuffix(".html").removesuffix("/index")
        for p in salida.rglob("*.html")
    }
    archivos.add("/")
    assets = {"/" + p.relative_to(salida).as_posix() for p in salida.rglob("*") if p.is_file()}

    rotos, relativos = [], []
    for pagina in sorted(salida.rglob("*.html")):
        html = pagina.read_text(encoding="utf-8")
        nombre = pagina.relative_to(salida).as_posix()
        # Dentro de <script> hay plantillas JS como src="${url}" que no son
        # marcado; escanearlas da falsos positivos.
        html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S | re.I)
        canon = CANONICAL.search(html)
        canon = canon.group(0) if canon else ""
        for attr, valor in re.findall(r'(href|src)=["\']([^"\']+)["\']', html):
            if valor.startswith(("http", "mailto:", "tel:", "#", "data:", "//")):
                continue
            if valor in canon:
                continue
            valor = re.split(r"[#?]", valor, maxsplit=1)[0] or "/"
            if not valor.startswith("/"):
                relativos.append(f"{nombre}: {attr}=\"{valor}\"")
            elif (valor if valor == "/" else valor.rstrip("/")) not in archivos and valor not in assets:
                rotos.append(f"{nombre}: {attr}=\"{valor}\"")

    # Un <script> con un error de sintaxis rompe la pagina entera sin avisar, y
    # el aula se edita a mano seguido. `node --check` lo caza antes de publicar.
    import subprocess, tempfile
    for pagina in sorted(salida.rglob("*.html")):
        for i, js in enumerate(re.findall(r'<script type="module">(.*?)</script>',
                                          pagina.read_text(encoding="utf-8"), re.S)):
            with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False,
                                             encoding="utf-8") as f:
                f.write(js)
            r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
            Path(f.name).unlink()
            if r.returncode:
                # node imprime ruta, linea, el codigo, el error y su version;
                # la linea util es la del Error, no la ultima.
                detalle = next((l.strip() for l in r.stderr.splitlines()
                                if "Error" in l), r.stderr.strip()[:120])
                rotos.append(f"{pagina.relative_to(salida).as_posix()}: script {i} no parsea — {detalle}")

    for etiqueta, lista in (("ENLACE ROTO", rotos), ("RUTA RELATIVA", relativos)):
        for x in lista:
            print(f"  {etiqueta}  {x}")
    if rotos or relativos:
        raise SystemExit(f"FALLO: {len(rotos)} rotos, {len(relativos)} relativos")
    print(f"  ok: {len(list(salida.rglob('*.html')))} paginas, 0 enlaces rotos")


def validar_flags(argv):
    """Whitelist de flags. Un '--cutver' mal escrito desactivaba el gate en
    silencio, y '--check --cutover' ignoraba --cutover (--check no construye,
    asi que el gate de cutover nunca corria)."""
    flags = set(argv)
    if flags - {"--check", "--cutover"} or flags == {"--check", "--cutover"}:
        raise SystemExit(
            "Uso: build.py [--check | --cutover]  "
            "(--check y --cutover son incompatibles: --check no construye)"
        )
    return flags


if __name__ == "__main__":
    flags = validar_flags(sys.argv[1:])
    if "--check" not in flags:
        print("Construyendo:")
        construir(cutover="--cutover" in flags)
    print("Verificando:")
    verificar()
