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

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "redesign-v2"
OUT = RAIZ / "site"
DOMINIO = "https://www.celebios.com"
CONTENIDO_PROGRAMAS = RAIZ / "contenido" / "programas.json"
REDIRECTS_CSV = RAIZ / "migracion" / "redirects.csv"

CANONICAL = re.compile(r'<link[^>]*rel=["\']canonical["\'][^>]*>', re.I)
HREF_CANON = re.compile(r'href=["\']([^"\']+)["\']', re.I)
MARCA = "\x00CANONICAL\x00"

ESTADOS_VALIDOS = {"disponible", "historico"}
CAMPOS_PROHIBIDOS_HISTORICO = {
    "offer", "price", "enrollment_state", "opening_date",
    "availability", "teacher_affiliations",
}
GA4_RE = re.compile(r'^G-[A-Z0-9]+$')


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
    return datos["programas"]


def validar_programas(programas, rutas_validas=None):
    """Revienta con ValueError ante cualquier violacion del contrato de
    contenido/programas.json: enum cerrado de status, un solo disponible,
    campos prohibidos en historicos, evidencia real, slugs unicos y
    consistencia canonica contra redesign-v2."""
    if rutas_validas is None:
        rutas_validas = rutas_canonicas_fuente()

    slugs_vistos = set()
    disponibles = []
    for p in programas:
        slug = p["slug"]
        if slug in slugs_vistos:
            raise ValueError(f"slug duplicado: {slug}")
        slugs_vistos.add(slug)

        if p["status"] not in ESTADOS_VALIDOS:
            raise ValueError(f"status invalido en {slug}: {p['status']!r}")
        if p["status"] == "disponible":
            disponibles.append(p)
        else:
            prohibidos = CAMPOS_PROHIBIDOS_HISTORICO & p.keys()
            if prohibidos:
                raise ValueError(f"{slug} es historico pero trae campos prohibidos: {prohibidos}")

        evidencia = p.get("evidence") or []
        if not evidencia:
            raise ValueError(f"{slug} no trae evidencia")
        for fuente in evidencia:
            if not (RAIZ / fuente).exists():
                raise ValueError(f"{slug}: evidencia inexistente: {fuente}")

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
        f"  <url><loc>{DOMINIO}{'' if r == '/' else r}{'/' if r == '/' else ''}</loc></url>\n"
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


def generar_vercel_json():
    config = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "cleanUrls": True,
        "trailingSlash": False,
        "bulkRedirectsPath": "migracion/redirects.csv",
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
                    {"key": "Cache-Control", "value": "public, max-age=31536000, immutable"},
                ],
            },
        ],
    }
    return json.dumps(config, indent=2, ensure_ascii=False) + "\n"


def url_a_ruta(url):
    """https://www.celebios.com/x -> /x ; https://www.celebios.com -> /"""
    return re.sub(r'^https?://[^/]+', '', url) or "/"


def convertir_redirects_bulk(filas):
    """migracion/redirects.csv (source_url,destination_path,status_code,...)
    -> formato bulk de Vercel [{source,destination,statusCode}]. Solo 301 con
    destino no vacio; sin auto-redirects (origen == destino tras normalizar a
    ruta); duplicados identicos se colapsan; un mismo origen con destinos
    distintos revienta (dos hosts viejos no pueden pelear la misma ruta)."""
    vistos = {}
    resultado = []
    for fila in filas:
        if str(fila["status_code"]) != "301":
            continue
        destino = fila["destination_path"]
        if not destino:
            continue
        origen = url_a_ruta(fila["source_url"])
        if origen == destino:
            continue
        if origen in vistos:
            if vistos[origen] != destino:
                raise ValueError(
                    f"conflicto: {origen} -> {vistos[origen]!r} y -> {destino!r}"
                )
            continue
        vistos[origen] = destino
        resultado.append({"source": origen, "destination": destino, "statusCode": 301})
    return resultado


def validar_ga4(measurement_id):
    if measurement_id is not None and not GA4_RE.match(measurement_id):
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


def construir():
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

    mapa = {f.name: ruta for f, ruta in paginas.items()}

    # Se vacia el contenido en vez de borrar site/ entero, por dos razones:
    # .vercel guarda a que proyecto publica el CLI (si se pierde, el deploy se
    # va a un proyecto nuevo), y en Windows rmtree revienta si algun proceso
    # tiene la carpeta como directorio actual.
    OUT.mkdir(parents=True, exist_ok=True)
    for hijo in OUT.iterdir():
        if hijo.name == ".vercel":
            continue
        shutil.rmtree(hijo) if hijo.is_dir() else hijo.unlink()
    for f, ruta in paginas.items():
        html = reescribir(f.read_text(encoding="utf-8"), mapa)
        html = inyectar_ga4(html, ga4_id)
        destino = OUT / archivo_destino(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html, encoding="utf-8")

    shutil.copytree(SRC / "brand", OUT / "brand")

    # El aula es estatica y va tal cual: no tiene canonical porque no debe
    # indexarse, asi que no pasa por el mapeo de rutas de arriba. Byte a byte,
    # sin tocar (ni GA4 le entra): es codigo fuente, no una vista publica.
    shutil.copytree(RAIZ / "aula", OUT / "aula")

    # Lo unico que no es estatico: la funcion que firma las URLs de video.
    shutil.copytree(RAIZ / "api", OUT / "api")
    shutil.copy2(RAIZ / "package.json", OUT / "package.json")

    (OUT / "404.html").write_text(inyectar_ga4(generar_404(), ga4_id), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(generar_sitemap(paginas.values()), encoding="utf-8")
    (OUT / "robots.txt").write_text(generar_robots(), encoding="utf-8")
    (OUT / "vercel.json").write_text(generar_vercel_json(), encoding="utf-8")

    with REDIRECTS_CSV.open(encoding="utf-8") as f:
        try:
            filas_bulk = convertir_redirects_bulk(list(csv.DictReader(f)))
        except ValueError as e:
            raise SystemExit(f"ERROR: {REDIRECTS_CSV}: {e}")
    (OUT / "migracion").mkdir(parents=True, exist_ok=True)
    with (OUT / "migracion" / "redirects.csv").open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["source", "destination", "statusCode"])
        escritor.writeheader()
        escritor.writerows(filas_bulk)

    print(f"  {len(paginas)} paginas + sitemap/robots/404/vercel.json -> {OUT}")
    return paginas


def verificar():
    """Ningun enlace interno puede apuntar a algo que no existe en site/."""
    archivos = {
        "/" + p.relative_to(OUT).as_posix().removesuffix(".html").removesuffix("/index")
        for p in OUT.rglob("*.html")
    }
    archivos.add("/")
    assets = {"/" + p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()}

    rotos, relativos = [], []
    for pagina in sorted(OUT.rglob("*.html")):
        html = pagina.read_text(encoding="utf-8")
        nombre = pagina.relative_to(OUT).as_posix()
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
    for pagina in sorted(OUT.rglob("*.html")):
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
                rotos.append(f"{pagina.relative_to(OUT).as_posix()}: script {i} no parsea — {detalle}")

    for etiqueta, lista in (("ENLACE ROTO", rotos), ("RUTA RELATIVA", relativos)):
        for x in lista:
            print(f"  {etiqueta}  {x}")
    if rotos or relativos:
        raise SystemExit(f"FALLO: {len(rotos)} rotos, {len(relativos)} relativos")
    print(f"  ok: {len(list(OUT.rglob('*.html')))} paginas, 0 enlaces rotos")


if __name__ == "__main__":
    if "--check" not in sys.argv:
        print("Construyendo:")
        construir()
    print("Verificando:")
    verificar()
