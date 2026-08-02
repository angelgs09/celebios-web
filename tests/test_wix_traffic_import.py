"""Pruebas del importador de evidencia autenticada de Wix Analytics
(Page Visits). Cubre: parseo/validacion estricta del CSV crudo de Wix
(encabezado exacto, metricas numericas no negativas con separador de miles,
rutas raiz-relativas, sin duplicados, al menos una fila), normalizacion de
source_url contra el origen canonico, join de solo-lectura contra
migracion/urls-wix.csv para inventory_match, y el manifiesto de evidencia
(sin datos personales, cutover_allowed=false).

No fabrica ninguna metrica: todo lo que compara contra un valor fijo (hash,
conteo de filas, totales resumen) viene del brief de evidencia observado.
"""
import csv
import io
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from scripts.import_wix_traffic import (
    CANONICAL_ORIGIN,
    EXPECTED_HEADER,
    NORMALIZED_FIELDS,
    build_manifest,
    build_normalized_rows,
    load_inventory_keys,
    parse_wix_traffic_csv,
    source_url_for_path,
    write_normalized_csv,
)

RAIZ = Path(__file__).resolve().parent.parent
MIGRACION = RAIZ / "migracion"

# Solo los tests de .gitattributes necesitan git: la propiedad que defienden ES
# una propiedad de Git. Fuera de un checkout se saltan en vez de reventar con
# CalledProcessError. En un worktree '.git' es un archivo, no un directorio;
# .exists() cubre ambos casos.
SIN_GIT = not (shutil.which("git") and (RAIZ / ".git").exists())

RAW_SHA256_ESPERADO = "9f2395146a666be9792fc63da03e0cdcc894d23f26e2e8f31ab644b2595a0952"
RAW_ROW_COUNT_ESPERADO = 152
RAW_SIZE_BYTES_ESPERADO = 4402
SUMMARY_PAGE_VIEWS_ESPERADO = 3543
SUMMARY_SITE_SESSIONS_ESPERADO = 2174
SUMMARY_UNIQUE_VISITORS_ESPERADO = 1592

ENCABEZADO_VALIDO = "Ruta de página,Vistas de página,Sesiones del sitio,Visitantes únicos"


def _csv_valido(filas="/,\"1,004\",870,642\n/cursos,457,390,322\n"):
    return f"{ENCABEZADO_VALIDO}\n{filas}"


class TestParseWixTrafficCsv(unittest.TestCase):
    def test_filas_validas_se_parsean_con_enteros(self):
        filas = parse_wix_traffic_csv(_csv_valido())
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[0], {
            "path": "/", "page_views": 1004, "site_sessions": 870, "unique_visitors": 642,
        })
        self.assertEqual(filas[1], {
            "path": "/cursos", "page_views": 457, "site_sessions": 390, "unique_visitors": 322,
        })

    def test_separador_de_miles_se_limpia(self):
        filas = parse_wix_traffic_csv(_csv_valido("/,\"12,345\",1,1\n"))
        self.assertEqual(filas[0]["page_views"], 12345)

    def test_maneja_utf8_bom(self):
        texto_con_bom = "﻿" + _csv_valido()
        filas = parse_wix_traffic_csv(texto_con_bom)
        self.assertEqual(len(filas), 2)

    def test_encabezado_inesperado_revienta(self):
        texto = "Path,Views,Sessions,Visitors\n/,1,1,1\n"
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(texto)

    def test_columna_extra_revienta(self):
        texto = ENCABEZADO_VALIDO + ",Extra\n/,1,1,1,x\n"
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(texto)

    def test_metrica_no_numerica_revienta(self):
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(_csv_valido("/,abc,1,1\n"))

    def test_metrica_negativa_revienta(self):
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(_csv_valido("/,-5,1,1\n"))

    def test_ruta_no_root_relativa_revienta(self):
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(_csv_valido("cursos,1,1,1\n"))

    def test_ruta_absoluta_externa_revienta(self):
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(_csv_valido("https://www.celebios.com/cursos,1,1,1\n"))

    def test_ruta_duplicada_revienta(self):
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(_csv_valido("/cursos,1,1,1\n/cursos,2,2,2\n"))

    def test_sin_filas_de_datos_revienta(self):
        with self.assertRaises(ValueError):
            parse_wix_traffic_csv(ENCABEZADO_VALIDO + "\n")


class TestSourceUrlForPath(unittest.TestCase):
    def test_home_no_lleva_slash_final(self):
        self.assertEqual(source_url_for_path("/"), CANONICAL_ORIGIN)

    def test_ruta_normal_se_concatena(self):
        self.assertEqual(
            source_url_for_path("/cursos"), f"{CANONICAL_ORIGIN}/cursos"
        )


class TestBuildNormalizedRows(unittest.TestCase):
    def test_columnas_exactas(self):
        filas = build_normalized_rows(
            [{"path": "/", "page_views": 1, "site_sessions": 1, "unique_visitors": 1}],
            inventory_keys=set(),
        )
        self.assertEqual(set(filas[0].keys()), set(NORMALIZED_FIELDS))

    def test_periodo_es_constante_y_preserva_discrepancia_de_nombre_de_archivo(self):
        filas = build_normalized_rows(
            [{"path": "/", "page_views": 1, "site_sessions": 1, "unique_visitors": 1}],
            inventory_keys=set(),
        )
        self.assertEqual(filas[0]["period_start"], "2025-08-02")
        self.assertEqual(filas[0]["period_end"], "2026-08-02")

    def test_inventory_match_true_en_minusculas(self):
        clave_home = "celebios.com"
        filas = build_normalized_rows(
            [{"path": "/", "page_views": 1, "site_sessions": 1, "unique_visitors": 1}],
            inventory_keys={clave_home},
        )
        self.assertEqual(filas[0]["inventory_match"], "true")

    def test_inventory_match_false_en_minusculas(self):
        filas = build_normalized_rows(
            [{"path": "/no-existe-en-el-inventario", "page_views": 1, "site_sessions": 1, "unique_visitors": 1}],
            inventory_keys=set(),
        )
        self.assertEqual(filas[0]["inventory_match"], "false")

    def test_preserva_el_orden_de_entrada(self):
        entradas = [
            {"path": "/b", "page_views": 1, "site_sessions": 1, "unique_visitors": 1},
            {"path": "/a", "page_views": 2, "site_sessions": 2, "unique_visitors": 2},
        ]
        filas = build_normalized_rows(entradas, inventory_keys=set())
        self.assertEqual([f["source_url"] for f in filas], [
            f"{CANONICAL_ORIGIN}/b", f"{CANONICAL_ORIGIN}/a",
        ])

    def test_write_normalized_csv_produce_encabezado_exacto(self):
        filas = build_normalized_rows(
            [{"path": "/", "page_views": 1, "site_sessions": 1, "unique_visitors": 1}],
            inventory_keys=set(),
        )
        buffer = io.StringIO()
        write_normalized_csv(buffer, filas)
        lector = csv.reader(io.StringIO(buffer.getvalue()))
        encabezado = next(lector)
        self.assertEqual(encabezado, NORMALIZED_FIELDS)


class TestLoadInventoryKeys(unittest.TestCase):
    def test_lee_urls_wix_csv_sin_modificarlo(self):
        contenido_antes = (MIGRACION / "urls-wix.csv").read_bytes()
        claves = load_inventory_keys(MIGRACION / "urls-wix.csv")
        contenido_despues = (MIGRACION / "urls-wix.csv").read_bytes()
        self.assertEqual(contenido_antes, contenido_despues)
        self.assertIn("celebios.com", claves)


class TestBuildManifest(unittest.TestCase):
    def setUp(self):
        self.manifest = build_manifest(
            raw_row_count=RAW_ROW_COUNT_ESPERADO,
            raw_sha256=RAW_SHA256_ESPERADO,
            raw_size_bytes=RAW_SIZE_BYTES_ESPERADO,
            # Asimetrico a proposito (2 true / 1 false): con 1 y 1, unos
            # conteos escritos a mano o con los predicados intercambiados
            # serian indistinguibles de los derivados y el test pasaria igual.
            filas_normalizadas=[
                {"source_url": f"{CANONICAL_ORIGIN}", "inventory_match": "true"},
                {"source_url": f"{CANONICAL_ORIGIN}/cursos", "inventory_match": "true"},
                {"source_url": f"{CANONICAL_ORIGIN}/huerfana", "inventory_match": "false"},
            ],
        )

    def test_resultado_del_join_se_deriva_de_las_filas(self):
        self.assertEqual(self.manifest["inventory_match_counts"], {"true": 2, "false": 1})
        self.assertEqual(
            self.manifest["unmatched_source_urls"], [f"{CANONICAL_ORIGIN}/huerfana"]
        )

    def test_cutover_permanece_bloqueado(self):
        self.assertEqual(self.manifest["cutover_allowed"], False)
        self.assertEqual(self.manifest["gate_status"], "blocked")

    def test_incluye_hash_y_conteo_de_filas(self):
        self.assertEqual(self.manifest["raw_sha256"], RAW_SHA256_ESPERADO)
        self.assertEqual(self.manifest["raw_row_count"], RAW_ROW_COUNT_ESPERADO)
        self.assertEqual(self.manifest["raw_size_bytes"], RAW_SIZE_BYTES_ESPERADO)

    def test_totales_resumen_observados(self):
        totales = self.manifest["summary_totals_observed_in_report"]
        self.assertEqual(totales["page_views"], SUMMARY_PAGE_VIEWS_ESPERADO)
        self.assertEqual(totales["site_sessions"], SUMMARY_SITE_SESSIONS_ESPERADO)
        self.assertEqual(totales["unique_visitors"], SUMMARY_UNIQUE_VISITORS_ESPERADO)

    def test_sin_datos_personales(self):
        texto = json.dumps(self.manifest)
        for patron_prohibido in ("@", "gmail", "angel", "coche"):
            with self.subTest(patron=patron_prohibido):
                self.assertNotIn(patron_prohibido, texto.lower())

    def test_documenta_falta_de_conexion_gsc(self):
        self.assertIn("gsc", json.dumps(self.manifest).lower())
        self.assertIn("no", self.manifest["gsc_connection_status"])


class TestCommittedArtifacts(unittest.TestCase):
    """Contrato sobre los artefactos ya comiteados: hash crudo exacto, CSV
    normalizado con 152 filas en el orden del reporte, manifiesto bloqueado."""

    def test_evidencia_cruda_hash_y_tamano_exactos(self):
        import hashlib
        ruta = MIGRACION / "evidencia" / "wix-page-visits-2025-08-02_2026-08-02.csv"
        datos = ruta.read_bytes()
        self.assertEqual(len(datos), RAW_SIZE_BYTES_ESPERADO)
        self.assertEqual(hashlib.sha256(datos).hexdigest(), RAW_SHA256_ESPERADO)

    def test_normalizado_tiene_152_filas_y_columnas_exactas(self):
        ruta = MIGRACION / "wix-page-visits-normalized.csv"
        with ruta.open(encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
        self.assertEqual(len(filas), RAW_ROW_COUNT_ESPERADO)
        self.assertEqual(list(filas[0].keys()), NORMALIZED_FIELDS)

    def test_normalizado_conserva_orden_del_reporte_crudo(self):
        ruta_normalizada = MIGRACION / "wix-page-visits-normalized.csv"
        with ruta_normalizada.open(encoding="utf-8", newline="") as f:
            filas_normalizadas = list(csv.DictReader(f))
        ruta_cruda = MIGRACION / "evidencia" / "wix-page-visits-2025-08-02_2026-08-02.csv"
        filas_crudas = parse_wix_traffic_csv(ruta_cruda.read_text(encoding="utf-8-sig"))
        self.assertEqual(
            [f["source_url"] for f in filas_normalizadas],
            [source_url_for_path(f["path"]) for f in filas_crudas],
        )

    def test_suma_de_page_views_normalizado_coincide_con_el_total_resumen(self):
        # A diferencia de sesiones/visitantes unicos (deduplicados a nivel de
        # sitio en el resumen, por eso no suman igual por pagina), cada
        # vista de pagina pertenece a exactamente una ruta: la suma por fila
        # SI debe coincidir con el total de resumen observado.
        ruta = MIGRACION / "wix-page-visits-normalized.csv"
        with ruta.open(encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
        total = sum(int(f["page_views"]) for f in filas)
        self.assertEqual(total, SUMMARY_PAGE_VIEWS_ESPERADO)

    def test_manifiesto_comiteado_sigue_bloqueado(self):
        ruta = MIGRACION / "wix-analytics-manifest.json"
        manifest = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertEqual(manifest["cutover_allowed"], False)
        self.assertEqual(manifest["raw_sha256"], RAW_SHA256_ESPERADO)
        self.assertEqual(manifest["raw_row_count"], RAW_ROW_COUNT_ESPERADO)

    def test_manifiesto_comiteado_registra_el_join_contra_el_inventario(self):
        # El resultado del join es el dato que necesita triage humano: debe
        # vivir en el manifiesto, no solo en las filas del CSV. Los conteos y
        # la lista se cotejan contra la columna inventory_match del CSV ya
        # comiteado, no contra numeros escritos a mano.
        manifest = json.loads(
            (MIGRACION / "wix-analytics-manifest.json").read_text(encoding="utf-8")
        )
        with (MIGRACION / "wix-page-visits-normalized.csv").open(
            encoding="utf-8", newline=""
        ) as f:
            filas = list(csv.DictReader(f))
        self.assertEqual(manifest["inventory_match_counts"], {
            "true": sum(1 for x in filas if x["inventory_match"] == "true"),
            "false": sum(1 for x in filas if x["inventory_match"] == "false"),
        })
        self.assertEqual(manifest["unmatched_source_urls"], [
            x["source_url"] for x in filas if x["inventory_match"] == "false"
        ])

    def test_urls_wix_csv_no_cambio_de_esquema(self):
        with (MIGRACION / "urls-wix.csv").open(encoding="utf-8") as f:
            encabezado = next(csv.reader(f))
        self.assertEqual(encabezado, [
            "source_url", "destination_path", "status_code", "category",
            "topic_or_cohort", "clicks", "impressions", "position", "backlinks",
            "priority", "confidence", "manual_review",
        ])

    @unittest.skipIf(SIN_GIT, "requiere binario de git y un checkout")
    def test_evidencia_cruda_marcada_gitattributes_text_unset(self):
        # Sin -text, el filtro de checkout de Git (core.autocrlf=true en este
        # repo) reescribe el LF crudo a CRLF y el hash deja de coincidir en
        # un clon fresco. Debe estar scopeado solo a migracion/evidencia/**.
        ruta_evidencia = "migracion/evidencia/wix-page-visits-2025-08-02_2026-08-02.csv"
        resultado = subprocess.run(
            ["git", "check-attr", "-a", "--", ruta_evidencia],
            cwd=RAIZ, capture_output=True, text=True, check=True,
        )
        self.assertIn("text: unset", resultado.stdout)

    @unittest.skipIf(SIN_GIT, "requiere binario de git y un checkout")
    def test_gitattributes_no_afecta_al_inventario_protegido(self):
        # -text debe estar scopeado a migracion/evidencia/**, nunca a *.csv
        # ni al inventario protegido de Task 1.
        resultado = subprocess.run(
            ["git", "check-attr", "-a", "--", "migracion/urls-wix.csv"],
            cwd=RAIZ, capture_output=True, text=True, check=True,
        )
        self.assertNotIn("text: unset", resultado.stdout)

    def test_normalizado_comiteado_es_identico_a_la_regeneracion(self):
        # Idempotencia/determinismo entre plataformas: regenerar desde la
        # evidencia cruda debe reproducir el archivo en disco. Se compara
        # contra el working tree (no contra el blob de HEAD via git cat-file):
        # comparar contra HEAD dejaba el test en rojo desde que cambia el
        # generador hasta que se comitea, y exigia git con un checkout. La
        # comparacion es en MODO TEXTO: este archivo no lleva -text, asi que
        # con core.autocrlf=true un clon fresco lo materializa en CRLF
        # mientras el generador escribe LF; read_text traduce \r\n a \n.
        ruta_cruda = MIGRACION / "evidencia" / "wix-page-visits-2025-08-02_2026-08-02.csv"
        filas_crudas = parse_wix_traffic_csv(ruta_cruda.read_text(encoding="utf-8-sig"))
        inventory_keys = load_inventory_keys(MIGRACION / "urls-wix.csv")
        filas_normalizadas = build_normalized_rows(filas_crudas, inventory_keys)

        buffer = io.StringIO()
        write_normalized_csv(buffer, filas_normalizadas)

        self.assertEqual(
            buffer.getvalue(),
            (MIGRACION / "wix-page-visits-normalized.csv").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
