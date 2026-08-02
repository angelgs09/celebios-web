#!/usr/bin/env python3
"""Importa la evidencia autenticada de Wix Analytics (reporte Page Visits del
sitio Wix `celebios`) sin declarar completo el gate SEO.

No hay conexion de este sitio Wix a Google Search Console ni una propiedad de
CELEBIOS en la cuenta de Google autenticada: clicks, impressions, position y
backlinks siguen sin evidencia y el cutover sigue bloqueado (ver
migracion/wix-analytics-manifest.json). Este importador solo agrega
page_views, site_sessions y unique_visitors por ruta, y marca si esa ruta ya
existe en el inventario de migracion (migracion/urls-wix.csv, de solo
lectura: este script nunca lo modifica).

Uso:
    python scripts/import_wix_traffic.py

Lee migracion/evidencia/wix-page-visits-2025-08-02_2026-08-02.csv (copia
cruda, byte a byte, del export de Wix) y escribe
migracion/wix-page-visits-normalized.csv y
migracion/wix-analytics-manifest.json.
"""
import csv
import hashlib
import io
import json
from pathlib import Path

from scripts.sync_migration_inventory import normalize_source_url

RAIZ = Path(__file__).resolve().parent.parent
MIGRACION = RAIZ / "migracion"
RAW_EVIDENCE_PATH = MIGRACION / "evidencia" / "wix-page-visits-2025-08-02_2026-08-02.csv"
URLS_WIX_CSV_PATH = MIGRACION / "urls-wix.csv"
NORMALIZED_CSV_PATH = MIGRACION / "wix-page-visits-normalized.csv"
MANIFEST_PATH = MIGRACION / "wix-analytics-manifest.json"

CANONICAL_ORIGIN = "https://www.celebios.com"

EXPECTED_HEADER = [
    "Ruta de página", "Vistas de página", "Sesiones del sitio", "Visitantes únicos",
]

NORMALIZED_FIELDS = [
    "source_url", "page_views", "site_sessions", "unique_visitors",
    "period_start", "period_end", "inventory_match",
]

# El nombre del archivo descargado expresa este rango; la UI de Wix mostraba
# "Last 365 days (Aug 2, 2025 - Today)" observado el 2026-08-01 -- un dia de
# discrepancia con el fin de rango del nombre de archivo. Se preserva tal
# cual en vez de elegir una fecha de cierre arbitraria (ver manifiesto).
FILENAME_PERIOD_START = "2025-08-02"
FILENAME_PERIOD_END = "2026-08-02"

RAW_SHA256 = "9f2395146a666be9792fc63da03e0cdcc894d23f26e2e8f31ab644b2595a0952"
RAW_ROW_COUNT = 152
RAW_SIZE_BYTES = 4402

# Totales del panel resumen de Wix tal como se observaron en la UI (no son la
# suma de las filas por pagina de site_sessions/unique_visitors: una misma
# sesion o visitante puede aparecer en varias paginas y el resumen del sitio
# deduplica; page_views si coincide con la suma por pagina, ver test).
SUMMARY_PAGE_VIEWS = 3543
SUMMARY_SITE_SESSIONS = 2174
SUMMARY_UNIQUE_VISITORS = 1592


def _parse_metric(crudo: str) -> int:
    limpio = crudo.replace(",", "").strip()
    if not limpio.isdigit():
        raise ValueError(f"metrica invalida (se esperaba un entero no negativo): {crudo!r}")
    return int(limpio)


def parse_wix_traffic_csv(texto: str) -> list[dict]:
    """Parsea y valida el CSV crudo de Wix Page Visits. Falla cerrado ante
    encabezado inesperado, columnas de mas o de menos, metricas no
    numericas/negativas, rutas no raiz-relativas, rutas duplicadas o ausencia
    de filas de datos."""
    texto = texto.lstrip("﻿")
    lector = csv.reader(io.StringIO(texto))
    filas = list(lector)
    if not filas:
        raise ValueError("CSV vacio: falta encabezado")

    encabezado, *filas_datos = filas
    if encabezado != EXPECTED_HEADER:
        raise ValueError(f"encabezado inesperado: {encabezado!r}, se esperaba {EXPECTED_HEADER!r}")
    if not filas_datos:
        raise ValueError("el CSV no trae ninguna fila de datos")

    rutas_vistas: set[str] = set()
    resultado = []
    for fila in filas_datos:
        if len(fila) != len(EXPECTED_HEADER):
            raise ValueError(f"fila con numero de columnas inesperado: {fila!r}")
        ruta, vistas, sesiones, visitantes = fila
        ruta = ruta.strip()
        if not ruta.startswith("/") or "://" in ruta:
            raise ValueError(f"ruta no raiz-relativa: {ruta!r}")
        if ruta in rutas_vistas:
            raise ValueError(f"ruta duplicada: {ruta!r}")
        rutas_vistas.add(ruta)
        resultado.append({
            "path": ruta,
            "page_views": _parse_metric(vistas),
            "site_sessions": _parse_metric(sesiones),
            "unique_visitors": _parse_metric(visitantes),
        })
    return resultado


def source_url_for_path(path: str) -> str:
    """CANONICAL_ORIGIN + path; la home ('/') no lleva slash final, igual
    que el resto de migracion/urls-wix.csv."""
    if path == "/":
        return CANONICAL_ORIGIN
    return f"{CANONICAL_ORIGIN}{path}"


def load_inventory_keys(urls_wix_csv_path: Path) -> set[str]:
    """Claves normalizadas (normalize_source_url) del inventario ya
    comiteado. Solo lectura: nunca escribe en urls_wix_csv_path."""
    with urls_wix_csv_path.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return {normalize_source_url(fila["source_url"]) for fila in filas}


def build_normalized_rows(filas_crudas: list[dict], inventory_keys: set[str]) -> list[dict]:
    resultado = []
    for fila in filas_crudas:
        source_url = source_url_for_path(fila["path"])
        coincide = normalize_source_url(source_url) in inventory_keys
        resultado.append({
            "source_url": source_url,
            "page_views": fila["page_views"],
            "site_sessions": fila["site_sessions"],
            "unique_visitors": fila["unique_visitors"],
            "period_start": FILENAME_PERIOD_START,
            "period_end": FILENAME_PERIOD_END,
            "inventory_match": "true" if coincide else "false",
        })
    return resultado


def write_normalized_csv(destino, filas: list[dict]) -> None:
    """destino puede ser un Path o un objeto con .write (para pruebas)."""
    if hasattr(destino, "write"):
        _escribir_normalizado(destino, filas)
    else:
        with Path(destino).open("w", encoding="utf-8", newline="") as f:
            _escribir_normalizado(f, filas)


def _escribir_normalizado(f, filas):
    escritor = csv.DictWriter(f, fieldnames=NORMALIZED_FIELDS)
    escritor.writeheader()
    escritor.writerows(filas)


def build_manifest(raw_row_count: int, raw_sha256: str, raw_size_bytes: int) -> dict:
    """Manifiesto de evidencia: sin datos personales, cutover_allowed en
    False mientras no exista un export de GSC de CELEBIOS aprobado."""
    return {
        "source_report": "Wix Analytics — Page Visits",
        "site_label": "celebios",
        "raw_evidence_path": "migracion/evidencia/wix-page-visits-2025-08-02_2026-08-02.csv",
        "observation_date": "2026-08-01",
        "ui_period_observed": "Last 365 days (Aug 2, 2025 - Today)",
        "filename_period_start": FILENAME_PERIOD_START,
        "filename_period_end": FILENAME_PERIOD_END,
        "period_discrepancy_note": (
            "El nombre del archivo descargado expresa 2025-08-02 a "
            "2026-08-02; la UI de Wix mostraba 'Last 365 days (Aug 2, 2025 "
            "- Today)' observado el 2026-08-01 local. Se preservan ambos "
            "valores tal cual, sin elegir una fecha de cierre arbitraria."
        ),
        "raw_row_count": raw_row_count,
        "raw_sha256": raw_sha256,
        "raw_size_bytes": raw_size_bytes,
        "summary_totals_observed_in_report": {
            "page_views": SUMMARY_PAGE_VIEWS,
            "site_sessions": SUMMARY_SITE_SESSIONS,
            "unique_visitors": SUMMARY_UNIQUE_VISITORS,
        },
        "summary_totals_note": (
            "Totales del panel resumen de Wix (deduplicados a nivel de "
            "sitio). No son la suma de las filas del CSV normalizado para "
            "site_sessions/unique_visitors: una misma sesion o visitante "
            "puede aparecer en varias paginas. page_views si coincide con "
            "esa suma porque cada vista pertenece a una sola pagina."
        ),
        "gsc_connection_status": "no_conectado",
        "gsc_findings": (
            "El reporte 'Top Search Queries on Google' de Wix no esta "
            "disponible porque este sitio Wix no esta conectado a Google "
            "Search Console. La cuenta de Google autenticada usada en esta "
            "revision no expone ninguna propiedad de CELEBIOS: clicks, "
            "impressions, position y backlinks siguen sin evidencia."
        ),
        "confidence": "alta_para_wix_page_visits",
        "gate_status": "blocked",
        "cutover_allowed": False,
        "contains_personal_data": False,
    }


def main() -> None:
    datos_crudos = RAW_EVIDENCE_PATH.read_bytes()
    sha256 = hashlib.sha256(datos_crudos).hexdigest()
    if sha256 != RAW_SHA256:
        raise SystemExit(
            f"ERROR: hash de {RAW_EVIDENCE_PATH.name} cambio "
            f"({sha256} != {RAW_SHA256}); revisar antes de continuar."
        )

    filas_crudas = parse_wix_traffic_csv(datos_crudos.decode("utf-8-sig"))
    inventory_keys = load_inventory_keys(URLS_WIX_CSV_PATH)
    filas_normalizadas = build_normalized_rows(filas_crudas, inventory_keys)

    write_normalized_csv(NORMALIZED_CSV_PATH, filas_normalizadas)

    manifest = build_manifest(
        raw_row_count=len(filas_crudas),
        raw_sha256=sha256,
        raw_size_bytes=len(datos_crudos),
    )
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  {len(filas_normalizadas)} filas -> {NORMALIZED_CSV_PATH}")
    print(f"  manifiesto -> {MANIFEST_PATH} (cutover_allowed=False)")


if __name__ == "__main__":
    main()
