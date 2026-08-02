#!/usr/bin/env python3
"""Inventario SEO de celebios.com (Wix) y celebios.online (Kajabi), y su
contrato de redirects hacia el sitio nuevo (Vercel).

No hay export autenticado de GSC ni de Wix Analytics todavia: clicks,
impressions, position y backlinks quedan vacios a proposito. Se llenan
importando ese export mas adelante, no se inventan aqui.

Los destinos se validan contra la arquitectura de informacion FINAL
planeada (ver migracion/README.md), no contra el sitio actual: paginas como
/cursos/anestesia-contencion-fauna existen hoy pero Task 3 las reemplaza por
anclas de archivo historico en /cursos, asi que los redirects apuntan ahi
directamente para no generar un salto doble cuando el rediseno se publique.

Requiere: pip install -r requirements.txt (urllib.request choca con la
proteccion anti-bot de Wix; ver el comentario en _descargar).

Uso:
    python scripts/sync_migration_inventory.py

Escribe migracion/urls-wix.csv, migracion/urls-kajabi.csv y
migracion/redirects.csv (el segundo es la union de los dos primeros).
"""
import csv
import re
import sys
import time
from email.utils import parsedate_to_datetime
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
# Tope duro para el Retry-After del servidor: sin el, un "Retry-After: 86400"
# duerme 24 h y un valor negativo revienta en time.sleep(). El backoff propio
# llega a 40 s (5*2^3) en el ultimo intento, asi que 60 s no estorba el camino
# normal y acota el peor caso a ~4 min.
_TOPE_ESPERA_SEGUNDOS = 60

CSV_FIELDS = [
    "source_url", "destination_path", "status_code", "category",
    "topic_or_cohort", "clicks", "impressions", "position", "backlinks",
    "priority", "confidence", "manual_review",
]

# Las unicas bases de destino que existiran en la arquitectura final del
# sitio (ver plan de rediseno). Cualquier fragmento (#...) es adicional a
# esto, nunca reemplaza la base.
DESTINOS_BASE_VALIDOS = {
    "/", "/aula", "/cursos", "/curso-lenguaje-felino", "/historia",
    "/egresados", "/practicas-de-campo", "/docentes", "/admisiones",
    "/contacto", "/aviso-de-privacidad",
}

_LOC_RE = re.compile(r"<loc>(.*?)</loc>", re.I)
_SITEMAPINDEX_RE = re.compile(r"<sitemapindex\b", re.I)


def _descargar(url: str) -> str:
    """GET con reintentos ante 429. Usa requests, no urllib.request: la
    proteccion anti-bot de Wix bloquea con 429 el fingerprint TLS/HTTP de
    urllib.request incluso en la primera peticion, mientras que requests (y
    curl) pasan sin problema -- no es throttling real por volumen. Respeta
    Retry-After si lo manda, en segundos o en formato de fecha HTTP
    (RFC 9110 permite ambos)."""
    encabezados = {"User-Agent": "Mozilla/5.0"}
    for intento in range(_REINTENTOS_429):
        respuesta = requests.get(url, headers=encabezados, timeout=20)
        if respuesta.status_code == 429:
            if intento == _REINTENTOS_429 - 1:
                respuesta.raise_for_status()
            espera = max(0, min(_TOPE_ESPERA_SEGUNDOS, _segundos_de_retry_after(
                respuesta.headers.get("Retry-After")
            ) or (_ESPERA_BASE_SEGUNDOS * (2 ** intento))))
            time.sleep(espera)
            continue
        respuesta.raise_for_status()
        return respuesta.text


def _segundos_de_retry_after(valor) -> int:
    if not valor:
        return 0
    try:
        return int(valor)
    except ValueError:
        pass
    try:
        from datetime import datetime, timezone
        fecha = parsedate_to_datetime(valor)
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        return max(0, int((fecha - datetime.now(timezone.utc)).total_seconds()))
    except (TypeError, ValueError):
        return 0


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


def _host_y_ruta(url: str) -> tuple[str, str]:
    """host sin 'www.' en minusculas, y ruta decodificada tal cual (con
    mayusculas y slash final intactos: quien llama decide si normaliza)."""
    partes = urlsplit(url.strip())
    host = partes.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host, unquote(partes.path)


def normalize_source_url(url: str) -> str:
    """Forma canonica para deduplicar: host sin 'www.', ruta decodificada
    y en minusculas, sin slash final, sin query ni fragmento."""
    host, ruta = _host_y_ruta(url)
    return f"{host}{ruta.rstrip('/').lower()}"


# --------------------------------------------------------------------------
# Reglas de clasificacion. Wix (celebios.com) es el sitio institucional
# viejo: casi todo son certificados de egresados y cohortes historicas.
# Kajabi (celebios.online) es chico y se enumera completo a mano.
#
# Orden de prioridad en classify_source (de mas a menos especifico):
#   1. home exacto
#   2. paginas institucionales explicitas (contacto, historia, aula, aviso...)
#   3. paginas de egresados/generaciones (prefijo egresados*/gen<anio>)
#   4. paginas de inscripcion/convocatoria (formularios de admision)
#   5. paginas de curso (vivo o historico, por palabra clave)
#   6. residual: basura del editor -> 404; cualquier otra cosa -> perfil de
#      egresado individual (nunca se expone el nombre de la persona)
# --------------------------------------------------------------------------

_KAJABI_MAP = {
    "": ("home", "home", "/"),
    "/home": ("home", "home", "/"),
    "/cursos": ("curso_historico", "catalogo", "/cursos"),
    "/store": ("curso_historico", "catalogo", "/cursos"),
    "/nosotros": ("institucional", "historia", "/historia"),
    "/about": ("institucional", "historia", "/historia"),
    "/contact": ("institucional", "contacto", "/contacto"),
    "/test": ("sin_equivalente", "", ""),
    "/nutricionfauna": ("curso_historico", "nutricion", "/cursos#historico-nutricion"),
    "/nutricion2024": ("curso_historico", "nutricion", "/cursos#historico-nutricion"),
    "/nutricion2025": ("curso_historico", "nutricion", "/cursos#historico-nutricion"),
    "/lenguaje-y-comunicacion-de-los-gatos": ("curso_disponible", "gatos", "/curso-lenguaje-felino"),
    "/curso-lenguaje-felino": ("curso_disponible", "gatos", "/curso-lenguaje-felino"),
    "/diplomado-rescate-rehabilitacion-fauna": ("curso_historico", "rehabilitacion", "/cursos#historico-rehabilitacion"),
    "/curso-anestesia": ("curso_historico", "anestesia", "/cursos#historico-anestesia"),
}

_WIX_EXPLICITAS = {
    "/nosotros": ("institucional", "historia", "/historia"),
    "/contacto": ("institucional", "contacto", "/contacto"),
    "/aviso-de-privacidad": ("institucional", "aviso-privacidad", "/aviso-de-privacidad"),
    "/aula-virtual": ("institucional", "aula", "/aula"),
    "/cursos": ("curso_historico", "catalogo", "/cursos"),
    "/formato-ingreso": ("institucional", "admision", "/admisiones"),
    # Pagina de calendario/oferta vigente, no un formulario de admision ni un
    # programa historico puntual: se queda en el catalogo vivo.
    "/programacion": ("curso_historico", "programacion", "/cursos"),
}

# (patron, tema, categoria), probado en orden: el primero que haga match
# gana. "felidos" es un diplomado historico sobre felidos silvestres y
# domesticos, NO el curso vivo de Lenguaje y Comunicacion de los Gatos.
_WIX_CURSOS = [
    (r"gatos|felino|lenguaje-y-comunicacion", "gatos", "curso_disponible"),
    (r"rehabilitacion|rescate", "rehabilitacion", "curso_historico"),
    (r"anestesia", "anestesia", "curso_historico"),
    (r"conductual", "conductual", "curso_historico"),
    (r"nutri", "nutricion", "curso_historico"),
    (r"ortopedia|aves", "ortopedia-aves", "curso_historico"),
    (r"reptil", "reptiles", "curso_historico"),
    (r"auxilio", "primeros-auxilios", "curso_historico"),
    (r"felidos", "felidos", "curso_historico"),
    (r"medicina-interna|medint", "medicina-interna", "curso_historico"),
    (r"medicina-preventiva", "medicina-preventiva", "curso_historico"),
    (r"bioetica", "bioetica", "curso_historico"),
    (r"caballos", "imagenologia-caballos", "curso_historico"),
    (r"imagen", "imagenologia", "curso_historico"),
    (r"\bsig\d*\b|cartografia", "sig-cartografia", "curso_historico"),
    (r"dato", "manejo-datos", "curso_historico"),
    (r"impacto-ambiental", "impacto-ambiental", "curso_historico"),
    (r"diagnostico-terapeutica", "diagnostico-terapeutica", "curso_historico"),
]
_WIX_CURSOS = [(re.compile(patron), tema, categoria)
               for patron, tema, categoria in _WIX_CURSOS]

# Paginas de perfil/certificado de egresados: prefijo literal "egresados" o
# "gen<anio>" (generacion). Van a /egresados, nunca a un 404 ni al catalogo:
# son trafico real de exalumnos, no basura del editor.
_WIX_PREFIJO_EGRESADOS = re.compile(r"^/(egresados|gen\d)")

# Formularios de inscripcion/convocatoria: intencion de admision, no
# contenido de curso, aunque el slug mencione un curso especifico.
_WIX_PREFIJO_ADMISION = re.compile(r"^/(inscripcion|convoc)")

_WIX_DOCENTES = re.compile(r"docente|profesor|instructor")
_WIX_PRACTICAS = re.compile(r"practica.*campo|campo.*practica|estacion.*campo")

# Basura real del editor de Wix (paginas de andamiaje, nunca contenido):
# nombres de plantilla sin editar, copias duplicadas, galerias vacias.
_WIX_BASURA_EDITOR = re.compile(r"^/(blank|keeper|galeria-\d+|copia-de-.+)$")

_ANIO_RE = re.compile(r"(19|20)\d{2}")


def _fragmento_egresado(ruta: str) -> tuple[str, str]:
    """topic_or_cohort y destino para una pagina de egresado: nunca incluye
    el nombre de la persona. Prioriza la cohorte (si hay un anio en la URL)
    sobre el tema del curso, y cae a /egresados sin ancla si no hay ninguna
    evidencia confiable de ninguno de los dos."""
    anio = _ANIO_RE.search(ruta)
    if anio:
        cohorte = anio.group(0)
        return (f"cohorte-{cohorte}", f"/egresados#cohorte-{cohorte}")
    for patron, tema, _categoria in _WIX_CURSOS:
        if patron.search(ruta):
            return (tema, f"/egresados#tema-{tema}")
    return ("", "/egresados")


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
    if _WIX_DOCENTES.search(ruta):
        return ("institucional", "docentes", "/docentes")
    if _WIX_PRACTICAS.search(ruta):
        return ("institucional", "practicas-de-campo", "/practicas-de-campo")
    if _WIX_PREFIJO_EGRESADOS.match(ruta):
        tema, destino = _fragmento_egresado(ruta)
        return ("egresado", tema, destino)
    if _WIX_PREFIJO_ADMISION.match(ruta):
        return ("institucional", "admision", "/admisiones")
    for patron, tema, categoria in _WIX_CURSOS:
        if patron.search(ruta):
            destino = "/curso-lenguaje-felino" if categoria == "curso_disponible" else f"/cursos#historico-{tema}"
            return (categoria, tema, destino)
    if _WIX_BASURA_EDITOR.match(ruta):
        return ("sin_equivalente", "", "")
    tema, destino = _fragmento_egresado(ruta)
    return ("egresado", tema, destino)


_PRIORIDAD_POR_CATEGORIA = {
    "home": "alta",
    "curso_disponible": "alta",
    "institucional": "media",
    "curso_historico": "media",
    "egresado": "media",
    "sin_equivalente": "baja",
}


def _status_code(destino: str) -> int:
    return 301 if destino else 404


def _confianza(categoria: str, tema: str) -> str:
    if categoria == "egresado":
        return "media" if tema else "baja"
    return "alta"


def _revision_manual(confianza: str) -> bool:
    return confianza == "baja"


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

        host, ruta = _host_y_ruta(url)

        categoria, tema, destino = classify_source(ruta, host)
        confianza = _confianza(categoria, tema)
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
            "confidence": confianza,
            "manual_review": "true" if _revision_manual(confianza) else "false",
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
