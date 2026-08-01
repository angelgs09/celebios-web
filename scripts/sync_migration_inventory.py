#!/usr/bin/env python3
"""Inventario SEO de celebios.com (Wix) y celebios.online (Kajabi), y su
contrato de redirects hacia el sitio nuevo (Vercel).

No hay export autenticado de GSC ni de Wix Analytics todavia: clicks,
impressions, position y backlinks quedan vacios a proposito. Se llenan
importando ese export mas adelante, no se inventan aqui.

Requiere: pip install requests (urllib.request choca con la proteccion
anti-bot de Wix; ver el comentario en _descargar).

Uso:
    python scripts/sync_migration_inventory.py

Escribe migracion/urls-wix.csv, migracion/urls-kajabi.csv y
migracion/redirects.csv (el segundo es la union de los dos primeros).
"""
import csv
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "migracion"

WIX_SITEMAP = "https://www.celebios.com/sitemap.xml"
KAJABI_SITEMAP = "https://www.celebios.online/sitemap.xml"

# El snapshot publico documentado en migracion/README.md. main() lo verifica
# contra lo que baja en vivo antes de escribir los CSV: si Wix o Kajabi
# publican paginas nuevas, esto revienta en vez de generar un inventario
# incompleto en silencio.
WIX_URLS_ESPERADAS = 371
KAJABI_URLS_ESPERADAS = 15

_REINTENTOS_429 = 4
_ESPERA_BASE_SEGUNDOS = 5

CSV_FIELDS = [
    "source_url", "destination_path", "status_code", "category",
    "topic_or_cohort", "clicks", "impressions", "position", "backlinks",
    "priority", "confidence", "manual_review",
]

_LOC_RE = re.compile(r"<loc>(.*?)</loc>", re.I)
_SITEMAPINDEX_RE = re.compile(r"<sitemapindex\b", re.I)


def _descargar(url: str) -> str:
    """GET con reintentos ante 429. Usa requests, no urllib.request: la
    proteccion anti-bot de Wix bloquea con 429 el fingerprint TLS/HTTP de
    urllib.request incluso en la primera peticion, mientras que requests (y
    curl) pasan sin problema -- no es throttling real por volumen. Respeta
    Retry-After si lo manda."""
    encabezados = {"User-Agent": "Mozilla/5.0"}
    for intento in range(_REINTENTOS_429):
        respuesta = requests.get(url, headers=encabezados, timeout=20)
        if respuesta.status_code == 429:
            if intento == _REINTENTOS_429 - 1:
                respuesta.raise_for_status()
            espera = int(respuesta.headers.get("Retry-After", 0)) or (
                _ESPERA_BASE_SEGUNDOS * (2 ** intento)
            )
            time.sleep(espera)
            continue
        respuesta.raise_for_status()
        return respuesta.text
    raise AssertionError("inalcanzable")  # el ultimo intento siempre retorna o revienta


def fetch_sitemap_urls(url: str) -> list[str]:
    """Descarga un sitemap.xml y devuelve sus <loc>. Sigue sitemap-index."""
    cuerpo = _descargar(url)
    ubicaciones = _LOC_RE.findall(cuerpo)
    if _SITEMAPINDEX_RE.search(cuerpo):
        urls = []
        for hijo in ubicaciones:
            urls.extend(fetch_sitemap_urls(hijo))
        return urls
    return ubicaciones


def normalize_source_url(url: str) -> str:
    """Forma canonica para deduplicar: host sin 'www.', ruta decodificada
    y en minusculas, sin slash final, sin query ni fragmento."""
    partes = urlsplit(url.strip())
    host = partes.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    ruta = unquote(partes.path).rstrip("/").lower()
    return f"{host}{ruta}"


# --------------------------------------------------------------------------
# Reglas de clasificacion. Wix (celebios.com) es el sitio institucional
# viejo: casi todo son certificados de egresados y cohortes historicas.
# Kajabi (celebios.online) es chico y se enumera completo a mano.
# --------------------------------------------------------------------------

_KAJABI_MAP = {
    "": ("home", "home", "/"),
    "/home": ("home", "home", "/"),
    "/cursos": ("curso_historico", "catalogo", "/cursos"),
    "/store": ("curso_historico", "catalogo", "/cursos"),
    "/nosotros": ("institucional", "nosotros", "/nosotros"),
    "/about": ("institucional", "nosotros", "/nosotros"),
    "/contact": ("institucional", "contacto", "/nosotros"),
    "/test": ("sin_equivalente", "", ""),
    "/nutricionfauna": ("curso_historico", "nutricion", "/cursos/nutricion-fauna-cautiverio"),
    "/nutricion2024": ("curso_historico", "nutricion", "/cursos/nutricion-fauna-cautiverio"),
    "/nutricion2025": ("curso_historico", "nutricion", "/cursos/nutricion-fauna-cautiverio"),
    "/lenguaje-y-comunicacion-de-los-gatos": ("curso_disponible", "gatos", "/curso-lenguaje-felino"),
    "/curso-lenguaje-felino": ("curso_disponible", "gatos", "/curso-lenguaje-felino"),
    "/diplomado-rescate-rehabilitacion-fauna": ("curso_historico", "rehabilitacion", "/diplomado-rescate-rehabilitacion-fauna"),
    "/curso-anestesia": ("curso_historico", "anestesia", "/cursos/anestesia-contencion-fauna"),
}

_WIX_EXPLICITAS = {
    "/nosotros": ("institucional", "nosotros", "/nosotros"),
    "/contacto": ("institucional", "contacto", "/nosotros"),
    # Sin pagina de privacidad todavia en el sitio nuevo: no se fabrica un
    # destino. Queda 404 y marcada para revision manual (ver README).
    "/aviso-de-privacidad": ("institucional", "aviso-privacidad", ""),
    "/aula-virtual": ("institucional", "aula", "/aula"),
    "/cursos": ("curso_historico", "catalogo", "/cursos"),
    # Mismo trato que /inscripcion*: formularios de admision sin curso propio.
    "/formato-ingreso": ("curso_historico", "admision", "/cursos"),
    "/programacion": ("curso_historico", "programacion", "/cursos"),
}

# (patron, destino, tema, categoria), probado en orden: el primero que haga
# match gana. "felidos" es un diplomado historico sobre felidos silvestres
# y domesticos, NO el curso vivo de Lenguaje y Comunicacion de los Gatos.
_WIX_CURSOS = [
    (r"gatos|felino|lenguaje-y-comunicacion", "/curso-lenguaje-felino", "gatos", "curso_disponible"),
    (r"rehabilitacion|rescate", "/diplomado-rescate-rehabilitacion-fauna", "rehabilitacion", "curso_historico"),
    (r"anestesia", "/cursos/anestesia-contencion-fauna", "anestesia", "curso_historico"),
    (r"conductual", "/cursos/manejo-conductual-fauna", "conductual", "curso_historico"),
    (r"nutri", "/cursos/nutricion-fauna-cautiverio", "nutricion", "curso_historico"),
    (r"ortopedia|aves", "/cursos/ortopedia-aves", "ortopedia-aves", "curso_historico"),
    (r"reptil", "/cursos/manejo-reptiles", "reptiles", "curso_historico"),
    (r"auxilio", "/cursos/primeros-auxilios-fauna", "primeros-auxilios", "curso_historico"),
    (r"felidos", "/cursos", "felidos", "curso_historico"),
    (r"medicina-interna|medint", "/cursos", "medicina-interna", "curso_historico"),
    (r"medicina-preventiva", "/cursos", "medicina-preventiva", "curso_historico"),
    (r"bioetica", "/cursos", "bioetica", "curso_historico"),
    (r"caballos", "/cursos", "imagenologia-caballos", "curso_historico"),
    (r"imagen", "/cursos", "imagenologia", "curso_historico"),
    (r"\bsig\d*\b|cartografia", "/cursos", "sig-cartografia", "curso_historico"),
    (r"dato", "/cursos", "manejo-datos", "curso_historico"),
    (r"impacto-ambiental", "/cursos", "impacto-ambiental", "curso_historico"),
    (r"diagnostico-terapeutica", "/cursos", "diagnostico-terapeutica", "curso_historico"),
]
_WIX_CURSOS = [(re.compile(patron), destino, tema, categoria)
               for patron, destino, tema, categoria in _WIX_CURSOS]

# Certificados/cohortes historicas sin curso reconocible en la ruta: van al
# catalogo, no a la raiz ni a un 404 (todavia son trafico de la academia).
_WIX_PREFIJOS_GENERICOS = re.compile(r"^/(egresados|inscripcion|convoc|gen\d)")

_REVISION_MANUAL_WIX = {"/aviso-de-privacidad"}


def classify_source(path: str, host: str) -> tuple[str, str, str]:
    """category, topic_or_cohort, destination para una ruta sin dominio."""
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]

    ruta = path if (path == "" or path.startswith("/")) else f"/{path}"
    ruta = ruta.lower() or "/"

    if host == "celebios.online":
        clave = "" if ruta == "/" else ruta
        if clave in _KAJABI_MAP:
            return _KAJABI_MAP[clave]
        raise ValueError(f"ruta Kajabi sin clasificar: {path!r}")

    if host != "celebios.com":
        raise ValueError(f"host no reconocido: {host!r}")

    if ruta == "/":
        return ("home", "home", "/")
    if ruta in _WIX_EXPLICITAS:
        return _WIX_EXPLICITAS[ruta]
    for patron, destino, tema, categoria in _WIX_CURSOS:
        if patron.search(ruta):
            return (categoria, tema, destino)
    if _WIX_PREFIJOS_GENERICOS.match(ruta):
        return ("curso_historico", "cohorte-historica", "/cursos")
    return ("sin_equivalente", "", "")


_PRIORIDAD_POR_CATEGORIA = {
    "home": "alta",
    "curso_disponible": "alta",
    "institucional": "media",
    "curso_historico": "media",
    "sin_equivalente": "baja",
}


def _status_code(destino: str) -> int:
    return 301 if destino else 404


def _confianza(categoria: str, tema: str) -> str:
    if categoria == "curso_historico" and tema == "cohorte-historica":
        return "media"
    return "alta"


def _revision_manual(ruta: str, host: str) -> bool:
    return host == "celebios.com" and ruta in _REVISION_MANUAL_WIX


def build_inventory_rows(urls: list[str]) -> list[dict]:
    """Clasifica una lista de URLs de sitemap y deduplica por su forma
    canonica. Conserva el orden de primera aparicion."""
    vistas = set()
    filas = []
    for url in urls:
        clave = normalize_source_url(url)
        if clave in vistas:
            continue
        vistas.add(clave)

        partes = urlsplit(url.strip())
        host = partes.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        ruta = unquote(partes.path)
        ruta_normalizada = ruta if (ruta == "" or ruta.startswith("/")) else f"/{ruta}"
        ruta_normalizada = ruta_normalizada.lower() or "/"

        categoria, tema, destino = classify_source(ruta, host)
        filas.append({
            "source_url": url.strip(),
            "destination_path": destino,
            "status_code": _status_code(destino),
            "category": categoria,
            "topic_or_cohort": tema,
            "clicks": "",
            "impressions": "",
            "position": "",
            "backlinks": "",
            "priority": _PRIORIDAD_POR_CATEGORIA[categoria],
            "confidence": _confianza(categoria, tema),
            "manual_review": "true" if _revision_manual(ruta_normalizada, host) else "false",
        })
    return filas


def write_csv(destino, filas: list[dict]) -> None:
    """destino puede ser un Path o un objeto con .write (para pruebas)."""
    if hasattr(destino, "write"):
        _escribir(destino, filas)
    else:
        with Path(destino).open("w", encoding="utf-8", newline="") as f:
            _escribir(f, filas)


def _escribir(f, filas):
    escritor = csv.DictWriter(f, fieldnames=CSV_FIELDS)
    escritor.writeheader()
    escritor.writerows(filas)


def main() -> None:
    print("Descargando sitemaps:")
    wix_urls = fetch_sitemap_urls(WIX_SITEMAP)
    kajabi_urls = fetch_sitemap_urls(KAJABI_SITEMAP)
    print(f"  wix: {len(wix_urls)} URLs, kajabi: {len(kajabi_urls)} URLs")

    # Verificacion en vivo del snapshot documentado, no un conteo de adorno:
    # si el sitio publico cambio, hay que revisar la clasificacion antes de
    # confiar en el CSV que este comando esta por escribir.
    if len(wix_urls) != WIX_URLS_ESPERADAS:
        raise SystemExit(
            f"ERROR: Wix expone {len(wix_urls)} URLs, se esperaban {WIX_URLS_ESPERADAS}. "
            "Revisar migracion/README.md y reclasificar antes de continuar."
        )
    if len(kajabi_urls) != KAJABI_URLS_ESPERADAS:
        raise SystemExit(
            f"ERROR: Kajabi expone {len(kajabi_urls)} URLs, se esperaban {KAJABI_URLS_ESPERADAS}. "
            "Revisar migracion/README.md y reclasificar antes de continuar."
        )

    filas_wix = build_inventory_rows(wix_urls)
    filas_kajabi = build_inventory_rows(kajabi_urls)

    SALIDA.mkdir(exist_ok=True)
    write_csv(SALIDA / "urls-wix.csv", filas_wix)
    write_csv(SALIDA / "urls-kajabi.csv", filas_kajabi)
    write_csv(SALIDA / "redirects.csv", filas_wix + filas_kajabi)
    print(f"  {len(filas_wix)} + {len(filas_kajabi)} filas -> {SALIDA}")


if __name__ == "__main__":
    main()
