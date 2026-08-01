#!/usr/bin/env python3
"""Arma el sitio publico de CELEBIOS para Vercel desde redesign-v2/.

Cada pagina aterriza en la ruta que dice su propio <link rel="canonical">, y
todos los enlaces internos se reescriben a rutas ABSOLUTAS: con cleanUrls una
ruta relativa se resuelve contra el directorio, asi que "catalogo.html" dentro
de /cursos/anestesia-contencion-fauna apuntaria a /cursos/catalogo.html.

Uso:  python build.py          -> arma site/ y verifica
      python build.py --check  -> solo verifica lo que ya esta en site/
"""
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "redesign-v2"
OUT = RAIZ / "site"
DOMINIO = "https://www.celebios.com"

CANONICAL = re.compile(r'<link[^>]*rel=["\']canonical["\'][^>]*>', re.I)
HREF_CANON = re.compile(r'href=["\']([^"\']+)["\']', re.I)
MARCA = "\x00CANONICAL\x00"


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
        destino = OUT / archivo_destino(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(reescribir(f.read_text(encoding="utf-8"), mapa), encoding="utf-8")

    shutil.copytree(SRC / "brand", OUT / "brand")

    # El aula es estatica y va tal cual: no tiene canonical porque no debe
    # indexarse, asi que no pasa por el mapeo de rutas de arriba.
    shutil.copytree(RAIZ / "aula", OUT / "aula")

    # Lo unico que no es estatico: la funcion que firma las URLs de video.
    shutil.copytree(RAIZ / "api", OUT / "api")
    shutil.copy2(RAIZ / "package.json", OUT / "package.json")

    # cleanUrls sirve /cursos/x desde cursos/x.html. El redirect es la palanca
    # de SEO: esa URL de Wix rankea #3 nacional y hoy dice "inscripciones
    # cerradas"; mandarla al diplomado vivo es lo unico que recupera ese trafico.
    (OUT / "vercel.json").write_text(
        '{\n'
        '  "cleanUrls": true,\n'
        '  "trailingSlash": false,\n'
        '  "redirects": [\n'
        '    { "source": "/rehabilitacion-fauna-2024",\n'
        '      "destination": "/diplomado-rescate-rehabilitacion-fauna",\n'
        '      "permanent": true }\n'
        '  ]\n'
        '}\n',
        encoding="utf-8",
    )
    print(f"  {len(paginas)} paginas + vercel.json -> {OUT}")
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
            valor = re.split(r"[#?]", valor, 1)[0] or "/"
            if not valor.startswith("/"):
                relativos.append(f"{nombre}: {attr}=\"{valor}\"")
            elif valor.rstrip("/") not in archivos and valor not in assets:
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
