"""Pruebas del contrato de contenido (contenido/programas.json) y del contrato
de build estatico (sitemap, robots, 404, vercel.json, redirects bulk, GA4).

No son pruebas de grep sobre texto fuente: ejercitan las funciones de
validacion/generacion de build.py y, para el contrato de artefactos, el build
real (build.construir()) contra el sistema de archivos del repo.
"""
import csv
import json
import os
import unittest
from pathlib import Path
from unittest import mock

import build

RAIZ = Path(__file__).resolve().parent.parent
CONTENIDO = RAIZ / "contenido" / "programas.json"


def _cargar_programas_reales():
    return build.cargar_programas(CONTENIDO)


def _programa_base(**overrides):
    base = {
        "slug": "/cursos/prueba",
        "title": "Programa de prueba",
        "status": "historico",
        "category": "curso",
        "topic": "Tema de prueba",
        "summary": "Resumen de prueba.",
        "evidence": ["redesign-v1/CONTENIDO-REAL.md"],
        "interest_topic": "prueba",
    }
    base.update(overrides)
    return base


class TestEstadoCerrado(unittest.TestCase):
    def test_estado_desconocido_revienta(self):
        programas = [_programa_base(status="en-desarrollo")]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_estados_validos_no_revientan_por_si_solos(self):
        for estado in ("disponible", "historico"):
            with self.subTest(estado=estado):
                programas = [
                    _programa_base(slug="/a", status="disponible" if estado == "historico" else "historico"),
                    _programa_base(slug="/b", status=estado),
                ]
                # Con los dos estados presentes y exactamente 1 disponible,
                # nada debe reventar solo por el valor del enum en si.
                build.validar_programas(programas, rutas_validas={"/a", "/b"})


class TestSoloUnDisponible(unittest.TestCase):
    def test_cero_disponibles_revienta(self):
        programas = [_programa_base(status="historico")]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_dos_disponibles_revienta(self):
        programas = [
            _programa_base(slug="/a", status="disponible"),
            _programa_base(slug="/b", status="disponible"),
        ]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/a", "/b"})

    def test_un_disponible_es_valido(self):
        programas = [
            _programa_base(slug="/a", status="disponible"),
            _programa_base(slug="/b", status="historico"),
        ]
        build.validar_programas(programas, rutas_validas={"/a", "/b"})

    def test_el_unico_disponible_en_los_datos_reales_es_el_curso_de_gatos(self):
        programas = _cargar_programas_reales()
        disponibles = [p for p in programas if p["status"] == "disponible"]
        self.assertEqual(len(disponibles), 1)
        self.assertEqual(disponibles[0]["slug"], "/curso-lenguaje-felino")


class TestCamposProhibidosEnHistorico(unittest.TestCase):
    def test_offer_en_historico_revienta(self):
        programas = [_programa_base(status="historico", offer={"price_mxn": 1})]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_campos_prohibidos_individuales_revientan(self):
        for campo in ("price", "enrollment_state", "opening_date", "availability", "teacher_affiliations"):
            with self.subTest(campo=campo):
                programas = [_programa_base(status="historico", **{campo: "x"})]
                with self.assertRaises(ValueError):
                    build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_ningun_programa_historico_real_trae_offer(self):
        programas = _cargar_programas_reales()
        for p in programas:
            if p["status"] == "historico":
                with self.subTest(slug=p["slug"]):
                    self.assertNotIn("offer", p)


class TestEvidenceRequerida(unittest.TestCase):
    def test_evidence_vacia_revienta(self):
        programas = [_programa_base(evidence=[])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_evidence_con_archivo_inexistente_revienta(self):
        programas = [_programa_base(evidence=["no/existe.md"])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_todos_los_programas_reales_tienen_evidencia_existente(self):
        programas = _cargar_programas_reales()
        for p in programas:
            with self.subTest(slug=p["slug"]):
                self.assertTrue(p["evidence"])
                for fuente in p["evidence"]:
                    self.assertTrue((RAIZ / fuente).exists(), f"no existe: {fuente}")


class TestConsistenciaCanonica(unittest.TestCase):
    def test_slug_sin_pagina_canonica_revienta(self):
        programas = [_programa_base(slug="/no-existe-en-redesign-v2")]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/otra-ruta"})

    def test_slugs_reales_coinciden_con_canonical_de_redesign_v2(self):
        rutas = build.rutas_canonicas_fuente()
        programas = _cargar_programas_reales()
        for p in programas:
            with self.subTest(slug=p["slug"]):
                self.assertIn(p["slug"], rutas)

    def test_ocho_programas_slugs_unicos(self):
        programas = _cargar_programas_reales()
        self.assertEqual(len(programas), 8)
        slugs = [p["slug"] for p in programas]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_programas_json_real_pasa_validacion_completa(self):
        programas = _cargar_programas_reales()
        rutas = build.rutas_canonicas_fuente()
        build.validar_programas(programas, rutas_validas=rutas)


class TestOfertaGatos(unittest.TestCase):
    def test_oferta_de_gatos_solo_trae_los_hechos_confirmados(self):
        programas = _cargar_programas_reales()
        gatos = next(p for p in programas if p["slug"] == "/curso-lenguaje-felino")
        self.assertEqual(
            gatos["offer"],
            {
                "price_mxn": 1400,
                "payment_type": "pago_unico",
                "hours": 12,
                "topics_count": 11,
                "access_months": 5,
            },
        )


class TestGenerarSitemap(unittest.TestCase):
    def test_incluye_home_y_rutas_normales(self):
        xml = build.generar_sitemap(["/", "/cursos", "/nosotros"])
        self.assertIn("<loc>https://www.celebios.com/</loc>", xml)
        self.assertIn("<loc>https://www.celebios.com/cursos</loc>", xml)
        self.assertIn("<loc>https://www.celebios.com/nosotros</loc>", xml)

    def test_excluye_404_y_aula_aunque_se_pasen(self):
        xml = build.generar_sitemap(["/", "/404", "/aula"])
        self.assertNotIn("/404", xml)
        self.assertNotIn("/aula", xml)

    def test_es_xml_bien_formado(self):
        import xml.etree.ElementTree as ET

        xml_texto = build.generar_sitemap(["/", "/cursos"])
        raiz = ET.fromstring(xml_texto)
        self.assertTrue(raiz.tag.endswith("urlset"))


class TestGenerarRobots(unittest.TestCase):
    def test_contiene_sitemap_y_disallow_aula(self):
        texto = build.generar_robots()
        self.assertIn("Sitemap: https://www.celebios.com/sitemap.xml", texto)
        self.assertIn("Disallow: /aula", texto)


class TestGenerarVercelJson(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(build.generar_vercel_json())

    def test_campos_obligatorios(self):
        self.assertEqual(self.config["$schema"], "https://openapi.vercel.sh/vercel.json")
        self.assertIs(self.config["cleanUrls"], True)
        self.assertIs(self.config["trailingSlash"], False)
        self.assertEqual(self.config["bulkRedirectsPath"], "migracion/redirects.csv")

    def test_no_usa_el_redirect_inline_viejo(self):
        self.assertNotIn("redirects", self.config)

    def test_trae_headers_de_seguridad(self):
        headers_planos = [h for bloque in self.config["headers"] for h in bloque["headers"]]
        claves = {h["key"] for h in headers_planos}
        self.assertIn("X-Content-Type-Options", claves)
        self.assertIn("X-Frame-Options", claves)


class TestConvertirRedirectsBulk(unittest.TestCase):
    def test_filtra_filas_no_301(self):
        filas = [{"source_url": "https://www.celebios.com/x", "destination_path": "", "status_code": "404"}]
        self.assertEqual(build.convertir_redirects_bulk(filas), [])

    def test_excluye_destino_vacio_aunque_sea_301(self):
        filas = [{"source_url": "https://www.celebios.com/x", "destination_path": "", "status_code": "301"}]
        self.assertEqual(build.convertir_redirects_bulk(filas), [])

    def test_convierte_source_url_a_ruta(self):
        filas = [{"source_url": "https://www.celebios.com/nosotros", "destination_path": "/historia", "status_code": "301"}]
        resultado = build.convertir_redirects_bulk(filas)
        self.assertEqual(resultado, [{"source": "/nosotros", "destination": "/historia", "statusCode": 301}])

    def test_excluye_auto_redirect_raiz(self):
        filas = [{"source_url": "https://www.celebios.com/", "destination_path": "/", "status_code": "301"}]
        self.assertEqual(build.convertir_redirects_bulk(filas), [])

    def test_excluye_auto_redirect_de_ruta_no_raiz(self):
        filas = [{"source_url": "https://www.celebios.online/curso-lenguaje-felino", "destination_path": "/curso-lenguaje-felino", "status_code": "301"}]
        self.assertEqual(build.convertir_redirects_bulk(filas), [])

    def test_deduplica_filas_identicas(self):
        filas = [
            {"source_url": "https://www.celebios.com/nosotros", "destination_path": "/historia", "status_code": "301"},
            {"source_url": "https://www.celebios.online/nosotros", "destination_path": "/historia", "status_code": "301"},
        ]
        self.assertEqual(len(build.convertir_redirects_bulk(filas)), 1)

    def test_conflicto_mismo_origen_distinto_destino_revienta(self):
        filas = [
            {"source_url": "https://www.celebios.com/x", "destination_path": "/a", "status_code": "301"},
            {"source_url": "https://www.celebios.online/x", "destination_path": "/b", "status_code": "301"},
        ]
        with self.assertRaises(ValueError):
            build.convertir_redirects_bulk(filas)

    def test_redirects_csv_comiteado_convierte_sin_reventar(self):
        with (RAIZ / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        resultado = build.convertir_redirects_bulk(filas)
        self.assertTrue(resultado)
        # Los dos auto-redirects de raiz (celebios.com bare y celebios.online/)
        # y el de /curso-lenguaje-felino no deben sobrevivir.
        origenes = {f["source"] for f in resultado}
        self.assertNotIn("/curso-lenguaje-felino", origenes)
        for f in resultado:
            self.assertNotEqual(f["source"], f["destination"])
            self.assertEqual(f["statusCode"], 301)


class TestGA4(unittest.TestCase):
    def test_ausente_no_inyecta(self):
        html = "<html><head></head><body></body></html>"
        self.assertEqual(build.inyectar_ga4(html, None), html)

    def test_valido_inyecta_antes_de_head(self):
        html = "<html><head><title>x</title></head><body></body></html>"
        resultado = build.inyectar_ga4(html, "G-ABC123")
        self.assertIn("G-ABC123", resultado)
        self.assertIn("googletagmanager.com/gtag/js?id=G-ABC123", resultado)
        self.assertLess(resultado.index("gtag"), resultado.index("</head>"))

    def test_inyeccion_no_trae_datos_de_usuario(self):
        resultado = build.inyectar_ga4("<head></head>", "G-ABC123")
        for prohibido in ("user_id", "email", "phone"):
            self.assertNotIn(prohibido, resultado)

    def test_formato_invalido_revienta(self):
        for invalido in ("12345", "ga-abc123", "G-abc123", "<script>alert(1)</script>"):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ValueError):
                    build.validar_ga4(invalido)

    def test_ausente_no_revienta(self):
        build.validar_ga4(None)

    def test_formato_valido_no_revienta(self):
        build.validar_ga4("G-ABC123XYZ")


class TestConstruirArtefactos(unittest.TestCase):
    """Corre el build real una vez y audita los artefactos generados."""

    @classmethod
    def setUpClass(cls):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GA4_MEASUREMENT_ID", None)
            build.construir()

    def test_sitemap_existe_y_excluye_aula_y_404(self):
        xml = (build.OUT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/aula", xml)
        self.assertNotIn("/404", xml)
        self.assertIn("<loc>https://www.celebios.com/</loc>", xml)

    def test_robots_existe(self):
        texto = (build.OUT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap:", texto)

    def test_404_existe_y_tiene_contenido_real(self):
        html = (build.OUT / "404.html").read_text(encoding="utf-8")
        self.assertIn("<html", html.lower())
        self.assertGreater(len(html), 200)

    def test_vercel_json_referencia_bulk_redirects(self):
        config = json.loads((build.OUT / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["bulkRedirectsPath"], "migracion/redirects.csv")

    def test_redirects_csv_bulk_tiene_encabezado_exacto(self):
        with (build.OUT / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            lector = csv.reader(f)
            encabezado = next(lector)
        self.assertEqual(encabezado, ["source", "destination", "statusCode"])

    def test_sin_ga4_ninguna_pagina_tiene_gtag(self):
        for pagina in build.OUT.rglob("*.html"):
            if "aula" in pagina.parts:
                continue
            with self.subTest(pagina=str(pagina)):
                self.assertNotIn("gtag", pagina.read_text(encoding="utf-8"))

    def test_aula_se_copia_byte_a_byte(self):
        for origen in (RAIZ / "aula").rglob("*"):
            if origen.is_dir():
                continue
            relativo = origen.relative_to(RAIZ / "aula")
            destino = build.OUT / "aula" / relativo
            with self.subTest(archivo=str(relativo)):
                self.assertEqual(destino.read_bytes(), origen.read_bytes())

    def test_api_se_copia_byte_a_byte(self):
        for origen in (RAIZ / "api").rglob("*"):
            if origen.is_dir():
                continue
            relativo = origen.relative_to(RAIZ / "api")
            destino = build.OUT / "api" / relativo
            with self.subTest(archivo=str(relativo)):
                self.assertEqual(destino.read_bytes(), origen.read_bytes())


class TestConstruirConGA4(unittest.TestCase):
    """Aisla la corrida con GA4 en su propia clase y restaura el build sin
    GA4 al terminar, para no dejar site/ en un estado distinto al que deja
    `python build.py` (fuente de verdad del estado final)."""

    @classmethod
    def tearDownClass(cls):
        build.construir()

    def test_ga4_valido_se_inyecta_en_paginas_publicas(self):
        with mock.patch.dict(os.environ, {"GA4_MEASUREMENT_ID": "G-ABC123XYZ"}):
            build.construir()
        html = (build.OUT / "index.html").read_text(encoding="utf-8")
        self.assertIn("G-ABC123XYZ", html)

    def test_ga4_invalido_revienta_el_build(self):
        with mock.patch.dict(os.environ, {"GA4_MEASUREMENT_ID": "no-valido"}):
            with self.assertRaises(SystemExit):
                build.construir()


if __name__ == "__main__":
    unittest.main()
