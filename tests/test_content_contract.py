"""Pruebas del contrato de contenido (contenido/programas.json) y del contrato
de build estatico (sitemap, robots, 404, vercel.json, redirects bulk, GA4).

No son pruebas de grep sobre texto fuente: ejercitan las funciones de
validacion/generacion de build.py y, para el contrato de artefactos, el build
real (build.construir()) contra un directorio de salida temporal.
"""
import csv
import json
import os
import re
import tempfile
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
        "status": "historical",
        "category": "curso",
        "topic": "Tema de prueba",
        "summary": "Resumen de prueba.",
        "evidence": ["redesign-v1/CONTENIDO-REAL.md#L94-L96"],
        "interest_topic": "prueba",
    }
    base.update(overrides)
    return base


class TestCamposRequeridos(unittest.TestCase):
    def test_falta_slug_revienta_con_valueerror(self):
        p = _programa_base()
        del p["slug"]
        with self.assertRaises(ValueError):
            build.validar_programas([p], rutas_validas={"/cursos/prueba"})

    def test_falta_campo_requerido_revienta_con_mensaje_claro(self):
        for campo in ("title", "category", "topic", "summary", "evidence", "interest_topic"):
            with self.subTest(campo=campo):
                p = _programa_base()
                del p[campo]
                with self.assertRaises(ValueError) as ctx:
                    build.validar_programas([p], rutas_validas={"/cursos/prueba"})
                self.assertIn(campo, str(ctx.exception))

    def test_campo_no_permitido_revienta(self):
        p = _programa_base(campo_inventado="x")
        with self.assertRaises(ValueError):
            build.validar_programas([p], rutas_validas={"/cursos/prueba"})

    def test_todos_los_programas_reales_pasan_campos_requeridos(self):
        programas = _cargar_programas_reales()
        rutas = build.rutas_canonicas_fuente()
        build.validar_programas(programas, rutas_validas=rutas)


class TestCargarProgramas(unittest.TestCase):
    def test_json_sin_clave_programas_revienta_con_valueerror(self):
        # ValueError, no KeyError: construir() solo atrapa ValueError, y con
        # KeyError el build escupe traceback crudo en vez de 'ERROR: ...'.
        with tempfile.TemporaryDirectory() as tmp:
            for contenido in ('{"otra_cosa": []}', '[]', '{}'):
                with self.subTest(contenido=contenido):
                    ruta = Path(tmp) / "programas.json"
                    ruta.write_text(contenido, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        build.cargar_programas(ruta)

    def test_json_real_carga(self):
        self.assertTrue(build.cargar_programas(CONTENIDO))


class TestValidarFlags(unittest.TestCase):
    def test_flags_soportadas_no_revientan(self):
        for argv in ([], ["--check"], ["--cutover"]):
            with self.subTest(argv=argv):
                self.assertEqual(build.validar_flags(argv), set(argv))

    def test_check_y_cutover_juntos_revientan(self):
        # --check no construye, asi que el gate de cutover nunca correria.
        with self.assertRaises(SystemExit):
            build.validar_flags(["--check", "--cutover"])

    def test_flag_desconocida_revienta(self):
        for argv in (["--cutver"], ["--cutover", "--x"], ["build"], ["-check"]):
            with self.subTest(argv=argv):
                with self.assertRaises(SystemExit):
                    build.validar_flags(argv)


class TestEstadoCerrado(unittest.TestCase):
    def test_estado_desconocido_revienta(self):
        programas = [_programa_base(status="en-desarrollo")]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_estado_en_espanol_ya_no_es_valido(self):
        for estado in ("disponible", "historico"):
            with self.subTest(estado=estado):
                programas = [_programa_base(status=estado)]
                with self.assertRaises(ValueError):
                    build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_estados_validos_no_revientan_por_si_solos(self):
        oferta = {
            "price_mxn": 1, "payment_type": "pago_unico",
            "hours": 1, "topics_count": 1, "access_months": 1,
        }
        # Con los dos estados presentes y exactamente 1 disponible, nada debe
        # reventar solo por el valor del enum en si.
        programas = [
            _programa_base(slug="/a", status="available", offer=oferta),
            _programa_base(slug="/b", status="historical"),
        ]
        build.validar_programas(programas, rutas_validas={"/a", "/b"})


class TestSoloUnDisponible(unittest.TestCase):
    def test_cero_disponibles_revienta(self):
        programas = [_programa_base(status="historical")]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_dos_disponibles_revienta(self):
        oferta = {
            "price_mxn": 1, "payment_type": "pago_unico",
            "hours": 1, "topics_count": 1, "access_months": 1,
        }
        programas = [
            _programa_base(slug="/a", status="available", offer=oferta),
            _programa_base(slug="/b", status="available", offer=oferta),
        ]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/a", "/b"})

    def test_un_disponible_es_valido(self):
        oferta = {
            "price_mxn": 1, "payment_type": "pago_unico",
            "hours": 1, "topics_count": 1, "access_months": 1,
        }
        programas = [
            _programa_base(slug="/a", status="available", offer=oferta),
            _programa_base(slug="/b", status="historical"),
        ]
        build.validar_programas(programas, rutas_validas={"/a", "/b"})

    def test_el_unico_disponible_en_los_datos_reales_es_el_curso_de_gatos(self):
        programas = _cargar_programas_reales()
        disponibles = [p for p in programas if p["status"] == "available"]
        self.assertEqual(len(disponibles), 1)
        self.assertEqual(disponibles[0]["slug"], "/curso-lenguaje-felino")


class TestCamposProhibidosEnHistorico(unittest.TestCase):
    def test_offer_en_historico_revienta(self):
        programas = [_programa_base(status="historical", offer={"price_mxn": 1})]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_campos_prohibidos_individuales_revientan(self):
        for campo in ("price", "enrollment_state", "opening_date", "availability", "teacher_affiliations"):
            with self.subTest(campo=campo):
                programas = [_programa_base(status="historical", **{campo: "x"})]
                with self.assertRaises(ValueError):
                    build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_ningun_programa_historico_real_trae_offer(self):
        programas = _cargar_programas_reales()
        for p in programas:
            if p["status"] == "historical":
                with self.subTest(slug=p["slug"]):
                    self.assertNotIn("offer", p)


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

    def test_disponible_sin_offer_revienta(self):
        p = _programa_base(status="available")
        with self.assertRaises(ValueError):
            build.validar_programas([p], rutas_validas={"/cursos/prueba"})

    def test_offer_con_campo_extra_revienta(self):
        oferta = {
            "price_mxn": 1, "payment_type": "pago_unico", "hours": 1,
            "topics_count": 1, "access_months": 1, "docente": "x",
        }
        p = _programa_base(status="available", offer=oferta)
        with self.assertRaises(ValueError):
            build.validar_programas([p], rutas_validas={"/cursos/prueba"})

    def test_offer_con_tipo_invalido_revienta(self):
        base = {
            "price_mxn": 1, "payment_type": "pago_unico",
            "hours": 1, "topics_count": 1, "access_months": 1,
        }
        # isinstance(True, int) es True: el booleano tiene que rebotar aparte.
        casos = [
            ("price_mxn", "1400"), ("price_mxn", True), ("price_mxn", 0),
            ("price_mxn", -1), ("price_mxn", 1400.0),
            ("hours", "12"), ("hours", None),
            ("topics_count", "11"), ("topics_count", 11.5),
            ("access_months", "5"), ("access_months", 0),
            ("payment_type", 1), ("payment_type", ""), ("payment_type", "  "),
        ]
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                oferta = dict(base, **{campo: valor})
                p = _programa_base(status="available", offer=oferta)
                with self.assertRaises(ValueError):
                    build.validar_programas([p], rutas_validas={"/cursos/prueba"})

    def test_offer_con_campo_faltante_revienta(self):
        oferta = {
            "price_mxn": 1, "payment_type": "pago_unico",
            "hours": 1, "topics_count": 1,
        }
        p = _programa_base(status="available", offer=oferta)
        with self.assertRaises(ValueError):
            build.validar_programas([p], rutas_validas={"/cursos/prueba"})


class TestEvidenceRequerida(unittest.TestCase):
    def test_evidence_vacia_revienta(self):
        programas = [_programa_base(evidence=[])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_evidence_con_archivo_inexistente_revienta(self):
        programas = [_programa_base(evidence=["no/existe.md#L1"])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_evidence_sin_ancla_de_linea_revienta(self):
        programas = [_programa_base(evidence=["redesign-v1/CONTENIDO-REAL.md"])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_evidence_con_rango_fuera_del_archivo_revienta(self):
        programas = [_programa_base(evidence=["redesign-v1/CONTENIDO-REAL.md#L9000"])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_evidence_con_rango_vacio_revienta(self):
        # La linea 2 de CONTENIDO-REAL.md esta en blanco.
        programas = [_programa_base(evidence=["redesign-v1/CONTENIDO-REAL.md#L2"])]
        with self.assertRaises(ValueError):
            build.validar_programas(programas, rutas_validas={"/cursos/prueba"})

    def test_evidence_con_salto_de_linea_final_revienta(self):
        # '$' casa antes de un '\n' final: sin fullmatch, esto se colaba.
        for fuente in ("https://www.celebios.com/algo\n",
                       "redesign-v1/CONTENIDO-REAL.md#L94-L96\n"):
            with self.subTest(fuente=fuente):
                with self.assertRaises(ValueError):
                    build._validar_evidencia("/cursos/prueba", fuente)

    def test_evidence_con_ancla_valida_no_revienta(self):
        build._validar_evidencia("/cursos/prueba", "redesign-v1/CONTENIDO-REAL.md#L94-L96")

    def test_todos_los_programas_reales_tienen_evidencia_con_ancla_valida(self):
        programas = _cargar_programas_reales()
        for p in programas:
            with self.subTest(slug=p["slug"]):
                self.assertTrue(p["evidence"])
                for fuente in p["evidence"]:
                    build._validar_evidencia(p["slug"], fuente)


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

    def test_escapa_ampersand_en_ruta(self):
        import xml.etree.ElementTree as ET

        xml_texto = build.generar_sitemap(["/recursos?a=1&b=2"])
        self.assertIn("&amp;", xml_texto)
        self.assertNotIn("&b=2</loc>", xml_texto)
        ET.fromstring(xml_texto)  # revienta si el XML sigue mal formado


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

    def test_brand_no_usa_cache_inmutable_de_un_anio(self):
        bloque = next(b for b in self.config["headers"] if b["source"] == "/brand/(.*)")
        valor = next(h["value"] for h in bloque["headers"] if h["key"] == "Cache-Control")
        self.assertNotIn("immutable", valor)
        self.assertNotIn("31536000", valor)
        self.assertIn("max-age=3600", valor)
        self.assertIn("stale-while-revalidate", valor)


class TestConvertirRedirectsBulk(unittest.TestCase):
    def test_filtra_filas_no_301(self):
        filas = [{"source_url": "https://www.celebios.com/x", "destination_path": "", "status_code": "404"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas=set())
        self.assertEqual(activas, [])
        self.assertEqual(diferidas, [])

    def test_excluye_destino_vacio_aunque_sea_301(self):
        filas = [{"source_url": "https://www.celebios.com/x", "destination_path": "", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas=set())
        self.assertEqual(activas, [])

    def test_convierte_source_url_a_ruta_cuando_destino_esta_publicado(self):
        filas = [{"source_url": "https://www.celebios.com/vieja", "destination_path": "/cursos", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas={"/cursos"})
        self.assertEqual(activas, [{"source": "/vieja", "destination": "/cursos", "statusCode": 301}])
        self.assertEqual(diferidas, [])

    def test_excluye_auto_redirect_raiz(self):
        filas = [{"source_url": "https://www.celebios.com/", "destination_path": "/", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas={"/"})
        self.assertEqual(activas, [])

    def test_excluye_auto_redirect_de_ruta_no_raiz(self):
        filas = [{"source_url": "https://www.celebios.online/curso-lenguaje-felino", "destination_path": "/curso-lenguaje-felino", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas={"/curso-lenguaje-felino"})
        self.assertEqual(activas, [])

    def test_deduplica_filas_identicas(self):
        filas = [
            {"source_url": "https://www.celebios.com/x", "destination_path": "/cursos", "status_code": "301"},
            {"source_url": "https://www.celebios.online/x", "destination_path": "/cursos", "status_code": "301"},
        ]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas={"/cursos"})
        self.assertEqual(len(activas), 1)

    def test_conflicto_mismo_origen_distinto_destino_revienta(self):
        filas = [
            {"source_url": "https://www.celebios.com/x", "destination_path": "/a", "status_code": "301"},
            {"source_url": "https://www.celebios.online/x", "destination_path": "/b", "status_code": "301"},
        ]
        with self.assertRaises(ValueError):
            build.convertir_redirects_bulk(filas, rutas_publicadas={"/a", "/b"})

    def test_diere_regla_cuyo_origen_es_pagina_publicada(self):
        filas = [{"source_url": "https://www.celebios.com/nosotros", "destination_path": "/historia", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas={"/nosotros"})
        self.assertEqual(activas, [])
        self.assertEqual(len(diferidas), 1)
        self.assertIn("source_shadows_published_page", diferidas[0]["reasons"])

    def test_diere_regla_cuyo_destino_no_esta_publicado(self):
        filas = [{"source_url": "https://www.celebios.com/x", "destination_path": "/egresados", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas=set())
        self.assertEqual(activas, [])
        self.assertEqual(len(diferidas), 1)
        self.assertIn("destination_not_published", diferidas[0]["reasons"])

    def test_destino_aula_es_excepcion_aunque_no_este_publicado(self):
        filas = [{"source_url": "https://www.celebios.com/aula-virtual", "destination_path": "/aula", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas=set())
        self.assertEqual(activas, [{"source": "/aula-virtual", "destination": "/aula", "statusCode": 301}])
        self.assertEqual(diferidas, [])

    def test_destino_con_ancla_valida_contra_su_ruta_base(self):
        filas = [{"source_url": "https://www.celebios.com/x", "destination_path": "/cursos#historico-y", "status_code": "301"}]
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas={"/cursos"})
        self.assertEqual(activas, [{"source": "/x", "destination": "/cursos#historico-y", "statusCode": 301}])

    def test_redirects_csv_comiteado_convierte_sin_reventar(self):
        with (RAIZ / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        rutas_publicadas = build.rutas_canonicas_fuente()
        activas, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas)
        self.assertTrue(activas)
        origenes = {f["source"] for f in activas}
        self.assertNotIn("/curso-lenguaje-felino", origenes)
        for f in activas:
            self.assertNotEqual(f["source"], f["destination"])
            self.assertEqual(f["statusCode"], 301)

    def test_reglas_activas_nunca_sombrean_paginas_publicadas(self):
        with (RAIZ / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        rutas_publicadas = build.rutas_canonicas_fuente()
        activas, _ = build.convertir_redirects_bulk(filas, rutas_publicadas)
        for regla in activas:
            with self.subTest(source=regla["source"]):
                self.assertNotIn(regla["source"], rutas_publicadas)

    def test_todo_destino_activo_existe_publicado_o_es_aula(self):
        with (RAIZ / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        rutas_publicadas = build.rutas_canonicas_fuente()
        activas, _ = build.convertir_redirects_bulk(filas, rutas_publicadas)
        for regla in activas:
            base = re.split(r"[#?]", regla["destination"], maxsplit=1)[0] or "/"
            with self.subTest(destination=regla["destination"]):
                self.assertTrue(base in rutas_publicadas or base == "/aula")

    def test_origen_con_mayusculas_o_slash_final_no_esquiva_el_check_de_sombra(self):
        for origen in ("https://www.celebios.com/Nosotros",
                       "https://www.celebios.com/nosotros/",
                       "https://www.celebios.com/NOSOTROS/"):
            with self.subTest(origen=origen):
                filas = [{"source_url": origen, "destination_path": "/cursos", "status_code": "301"}]
                activas, diferidas = build.convertir_redirects_bulk(
                    filas, rutas_publicadas={"/nosotros", "/cursos"}
                )
                self.assertEqual(activas, [])
                self.assertIn("source_shadows_published_page", diferidas[0]["reasons"])

    def test_mismo_origen_con_distinta_caja_es_el_mismo_origen(self):
        filas = [
            {"source_url": "https://www.celebios.com/x", "destination_path": "/a", "status_code": "301"},
            {"source_url": "https://www.celebios.online/X/", "destination_path": "/b", "status_code": "301"},
        ]
        with self.assertRaises(ValueError):
            build.convertir_redirects_bulk(filas, rutas_publicadas={"/a", "/b"})

    def test_csv_sin_columnas_requeridas_revienta_con_valueerror(self):
        # Encabezado incompleto: ValueError (mensaje limpio), no KeyError crudo.
        with self.assertRaises(ValueError):
            build.convertir_redirects_bulk(
                [{"source_url": "https://www.celebios.com/x"}], rutas_publicadas=set()
            )

    def test_hay_reglas_diferidas_conocidas_pre_task3(self):
        with (RAIZ / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        rutas_publicadas = build.rutas_canonicas_fuente()
        _, diferidas = build.convertir_redirects_bulk(filas, rutas_publicadas)
        origenes_diferidos = {d["source"] for d in diferidas}
        self.assertIn("/nosotros", origenes_diferidos)
        self.assertIn("/diplomado-rescate-rehabilitacion-fauna", origenes_diferidos)


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
        for invalido in ("12345", "ga-abc123", "G-abc123", "<script>alert(1)</script>", "G-ABC123\n"):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ValueError):
                    build.validar_ga4(invalido)

    def test_ausente_no_revienta(self):
        build.validar_ga4(None)

    def test_formato_valido_no_revienta(self):
        build.validar_ga4("G-ABC123XYZ")


class TestConstruirArtefactos(unittest.TestCase):
    """Corre el build real una vez, contra un directorio temporal aislado, y
    audita los artefactos generados."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.salida = Path(cls.tmp.name) / "site"
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GA4_MEASUREMENT_ID", None)
            build.construir(salida=cls.salida)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_sitemap_existe_y_excluye_aula_y_404(self):
        xml = (self.salida / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/aula", xml)
        self.assertNotIn("/404", xml)
        self.assertIn("<loc>https://www.celebios.com/</loc>", xml)

    def test_robots_existe(self):
        texto = (self.salida / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap:", texto)

    def test_404_existe_y_tiene_contenido_real(self):
        html = (self.salida / "404.html").read_text(encoding="utf-8")
        self.assertIn("<html", html.lower())
        self.assertGreater(len(html), 200)

    def test_vercel_json_referencia_bulk_redirects(self):
        config = json.loads((self.salida / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["bulkRedirectsPath"], "migracion/redirects.csv")

    def test_redirects_csv_bulk_tiene_encabezado_exacto(self):
        with (self.salida / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            lector = csv.reader(f)
            encabezado = next(lector)
        self.assertEqual(encabezado, ["source", "destination", "statusCode"])

    def test_redirects_csv_bulk_no_sombrea_paginas_publicadas(self):
        rutas_publicadas = build.rutas_canonicas_fuente()
        with (self.salida / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                with self.subTest(source=fila["source"]):
                    self.assertNotIn(fila["source"], rutas_publicadas)

    def test_sin_ga4_ninguna_pagina_tiene_gtag(self):
        for pagina in self.salida.rglob("*.html"):
            if "aula" in pagina.parts:
                continue
            with self.subTest(pagina=str(pagina)):
                self.assertNotIn("gtag", pagina.read_text(encoding="utf-8"))

    def test_aula_se_copia_byte_a_byte(self):
        for origen in (RAIZ / "aula").rglob("*"):
            if origen.is_dir():
                continue
            relativo = origen.relative_to(RAIZ / "aula")
            destino = self.salida / "aula" / relativo
            with self.subTest(archivo=str(relativo)):
                self.assertEqual(destino.read_bytes(), origen.read_bytes())

    def test_api_se_copia_byte_a_byte(self):
        for origen in (RAIZ / "api").rglob("*"):
            if origen.is_dir():
                continue
            relativo = origen.relative_to(RAIZ / "api")
            destino = self.salida / "api" / relativo
            with self.subTest(archivo=str(relativo)):
                self.assertEqual(destino.read_bytes(), origen.read_bytes())


class TestConstruirConGA4(unittest.TestCase):
    def test_ga4_valido_se_inyecta_en_paginas_publicas(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {"GA4_MEASUREMENT_ID": "G-ABC123XYZ"}):
                build.construir(salida=salida)
            html = (salida / "index.html").read_text(encoding="utf-8")
            self.assertIn("G-ABC123XYZ", html)

    def test_ga4_invalido_revienta_el_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {"GA4_MEASUREMENT_ID": "no-valido"}):
                with self.assertRaises(SystemExit):
                    build.construir(salida=salida)


class TestConstruirPreservaVercelDir(unittest.TestCase):
    def test_vercel_dir_sobrevive_al_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            salida.mkdir()
            marca = salida / ".vercel"
            marca.mkdir()
            (marca / "project.json").write_text("{}", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GA4_MEASUREMENT_ID", None)
                build.construir(salida=salida)
            self.assertTrue((salida / ".vercel" / "project.json").exists())


class TestCutover(unittest.TestCase):
    def test_cutover_revienta_antes_de_escribir_por_reglas_diferidas_pre_task3(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GA4_MEASUREMENT_ID", None)
                with self.assertRaises(SystemExit) as ctx:
                    build.construir(salida=salida, cutover=True)
            self.assertIn("cutover", str(ctx.exception).lower())
            self.assertFalse(salida.exists())

    def test_preview_sin_cutover_no_revienta_pese_a_diferidas(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GA4_MEASUREMENT_ID", None)
                build.construir(salida=salida, cutover=False)
            self.assertTrue((salida / "migracion" / "redirects.csv").exists())


class TestFrasesRechazadas(unittest.TestCase):
    """La tabla "Rechazadas" de INVESTIGACION.md no puede quedarse en prosa:
    si nada la hace cumplir, la siguiente reescritura de plantilla reintroduce
    las afirmaciones y llegan a produccion."""

    def _pagina(self, tmp, texto):
        f = Path(tmp) / "pagina.html"
        f.write_text(texto, encoding="utf-8")
        return f

    def test_detecta_las_afirmaciones_rechazadas(self):
        casos = [
            "<p>La única academia latinoamericana de fauna silvestre</p>",
            '"description": "La unica academia latinoamericana"',   # JSON-LD sin tildes
            "<strong>Diploma con validez oficial</strong>",
            "un diploma con Validez Oficial, emitido por",
            "<p>Claustro internacional · 12 especialistas de México</p>",
        ]
        for texto in casos:
            with self.subTest(texto=texto), tempfile.TemporaryDirectory() as tmp:
                hallados = build.buscar_frases_rechazadas([self._pagina(tmp, texto)])
                self.assertEqual(len(hallados), 1, f"no detecto: {texto!r}")
                arch, linea, encontrado, motivo = hallados[0]
                self.assertEqual(arch, "pagina.html")
                self.assertEqual(linea, 1)
                self.assertTrue(motivo)

    def test_no_marca_la_redaccion_corregida(self):
        """El reemplazo que prescribe INVESTIGACION.md no puede disparar la
        guarda, o el arreglo seria imposible de aplicar."""
        legitimos = [
            "<p>Academia latinoamericana de fauna silvestre avalada por CONCERVET</p>",
            "<strong>Diploma con valor curricular</strong>, avalado por CONCERVET",
            "<p>Claustro internacional de especialistas</p>",
            "<p>Con validez de constancia interna</p>",
        ]
        for texto in legitimos:
            with self.subTest(texto=texto), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(build.buscar_frases_rechazadas([self._pagina(tmp, texto)]), [])

    def test_reporta_archivo_y_linea_de_cada_ocurrencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self._pagina(tmp, "ok\n<p>validez oficial</p>\nok\n<p>única academia</p>\n")
            hallados = build.buscar_frases_rechazadas([f])
            self.assertEqual([(h[1], h[2]) for h in hallados],
                             [(2, "validez oficial"), (4, "única academia")])

    def test_construir_revienta_antes_de_escribir(self):
        """La guarda va cableada al build, no solo disponible como funcion."""
        falso = [("maqueta.html", 7, "validez oficial", "motivo de prueba")]
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.object(build, "buscar_frases_rechazadas", return_value=falso):
                with mock.patch.dict(os.environ, {}, clear=False):
                    os.environ.pop("GA4_MEASUREMENT_ID", None)
                    with self.assertRaises(SystemExit) as ctx:
                        build.construir(salida=salida)
            self.assertIn("maqueta.html:7", str(ctx.exception))
            self.assertFalse(salida.exists(), "no debe dejar un build a medias")

    def test_las_plantillas_publicables_estan_limpias(self):
        """Regresion sobre el contenido real: ninguna pagina con canonical
        (las que el build publica) trae una afirmacion rechazada."""
        publicables = [f for f in sorted(build.SRC.glob("*.html"))
                       if build.ruta_canonica(f.read_text(encoding="utf-8"))]
        hallados = build.buscar_frases_rechazadas(publicables)
        self.assertEqual(hallados, [], f"afirmaciones rechazadas aun publicadas: {hallados}")


class TestDisponibilidadFalsa(unittest.TestCase):
    """contenido/programas.json y el HTML son dos fuentes de verdad y ya
    divergieron una vez: el catalogo anunciaba disponibles, con precio, el
    diplomado de $19,500 y dos cursos que el contrato marca historicos."""

    PROGRAMAS = [
        {"slug": "/curso-lenguaje-felino", "status": "available"},
        {"slug": "/cursos/manejo-reptiles", "status": "historical"},
    ]

    def _paginas(self, tmp, **archivos):
        paginas = {}
        for nombre, (ruta, cuerpo) in archivos.items():
            f = Path(tmp) / nombre
            f.write_text(cuerpo, encoding="utf-8")
            paginas[f] = ruta
        return paginas

    def test_tarjeta_disponible_que_apunta_a_un_historico_es_violacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(
                tmp,
                **{
                    "catalogo.html": ("/cursos", '<article data-estado="disp">'
                                                 '<a href="curso-reptiles.html">Ver curso</a></article>'),
                    "curso-reptiles.html": ("/cursos/manejo-reptiles", "<p>x</p>"),
                },
            )
            hallados = build.buscar_disponibilidad_falsa(paginas, self.PROGRAMAS)
            self.assertEqual(len(hallados), 1)
            self.assertEqual(hallados[0][0], "catalogo.html")
            self.assertEqual(hallados[0][2], ["/cursos/manejo-reptiles"])

    def test_tarjeta_disponible_que_apunta_al_disponible_pasa(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(
                tmp,
                **{
                    "catalogo.html": ("/cursos", '<article data-estado="disp">'
                                                 '<a href="diplomado-rehab.html">Luego el diplomado</a>'
                                                 '<a href="curso-gatos.html">Inscribirme</a></article>'),
                    "curso-gatos.html": ("/curso-lenguaje-felino", "<p>x</p>"),
                    "diplomado-rehab.html": ("/cursos/manejo-reptiles", "<p>x</p>"),
                },
            )
            self.assertEqual(build.buscar_disponibilidad_falsa(paginas, self.PROGRAMAS), [])

    def test_falla_cerrado_si_el_enlace_no_se_puede_resolver(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(
                tmp,
                **{"catalogo.html": ("/cursos", '<article data-estado="disp">sin enlace</article>')},
            )
            self.assertEqual(len(build.buscar_disponibilidad_falsa(paginas, self.PROGRAMAS)), 1)

    def test_precio_en_una_tarjeta_historica_es_violacion_aunque_no_diga_disponible(self):
        """El precio es una afirmacion de oferta vigente, se marque 'disp' o no."""
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(
                tmp,
                **{
                    "catalogo.html": ("/cursos", '<article data-estado="hist">'
                                                 '<a href="curso-reptiles.html">Ver curso</a>'
                                                 '<span class="lam-price">$1,600 MXN</span></article>'),
                    "curso-reptiles.html": ("/cursos/manejo-reptiles", "<p>x</p>"),
                },
            )
            hallados = build.buscar_disponibilidad_falsa(paginas, self.PROGRAMAS)
            self.assertEqual(len(hallados), 1)
            self.assertEqual(hallados[0][2], ["/cursos/manejo-reptiles"])

    def test_precio_en_la_tarjeta_del_curso_disponible_pasa(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(
                tmp,
                **{
                    "catalogo.html": ("/cursos", '<article data-estado="disp">'
                                                 '<a href="curso-gatos.html">Inscribirme</a>'
                                                 '<span class="lam-price">$1,400 MXN</span></article>'),
                    "curso-gatos.html": ("/curso-lenguaje-felino", "<p>x</p>"),
                },
            )
            self.assertEqual(build.buscar_disponibilidad_falsa(paginas, self.PROGRAMAS), [])

    def test_construir_revienta_antes_de_escribir(self):
        falso = [("catalogo.html", 42, ["/cursos/manejo-reptiles"])]
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.object(build, "buscar_disponibilidad_falsa", return_value=falso):
                with mock.patch.dict(os.environ, {}, clear=False):
                    os.environ.pop("GA4_MEASUREMENT_ID", None)
                    with self.assertRaises(SystemExit) as ctx:
                        build.construir(salida=salida)
            self.assertIn("catalogo.html:42", str(ctx.exception))
            self.assertFalse(salida.exists())

    def test_el_catalogo_real_solo_anuncia_disponible_el_curso_de_gatos(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        hallados = build.buscar_disponibilidad_falsa(paginas, build.cargar_programas())
        self.assertEqual(hallados, [], f"tarjetas con disponibilidad falsa: {hallados}")


class TestEstadoPlanned(unittest.TestCase):
    """`planned` existe porque dos programas no eran ni `available` ni
    `historical`: nacieron como ejemplos de catalogo en junio, con precio
    placeholder, y no hay prueba de que se hayan impartido. Tiene las mismas
    restricciones que `historical`."""

    def test_un_planned_no_puede_traer_oferta(self):
        p = _programa_base(status="planned", offer={"price_mxn": 1000, "payment_type": "unico",
                                                    "hours": 8, "topics_count": 5, "access_months": 3})
        with self.assertRaises(ValueError) as ctx:
            build.validar_programas([p], rutas_validas={"/cursos/prueba"})
        self.assertIn("no permitidos", str(ctx.exception))

    def test_un_planned_no_cuenta_como_disponible(self):
        programas = _cargar_programas_reales()
        self.assertEqual(sum(1 for p in programas if p["status"] == "available"), 1)
        self.assertEqual(
            {p["slug"] for p in programas if p["status"] == "planned"},
            {"/cursos/primeros-auxilios-fauna", "/cursos/manejo-reptiles"},
        )

    def test_la_guarda_de_oferta_cubre_planned_igual_que_historical(self):
        programas = [
            {"slug": "/curso-lenguaje-felino", "status": "available",
             "offer": {"price_mxn": 1400, "payment_type": "unico", "hours": 12,
                       "topics_count": 11, "access_months": 5}},
            {"slug": "/cursos/x", "status": "planned"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "curso-x.html"
            f.write_text("<p>Desde $9,900 MXN</p>", encoding="utf-8")
            hallados = build.buscar_oferta_en_historicos({f: "/cursos/x"}, programas)
            self.assertTrue(any("precio propio" in m for _, m in hallados), hallados)


class TestEvidenciaCircular(unittest.TestCase):
    """Dos programas se sostenian citando la linea del canonical de la maqueta
    que este mismo redisenio escribio. Eso no es evidencia de nada."""

    def test_citar_una_maqueta_html_revienta(self):
        maqueta = next(build.SRC.glob("*.html"))
        with self.assertRaises(ValueError) as ctx:
            build._validar_evidencia("/x", f"redesign-v2/{maqueta.name}#L8")
        self.assertIn("circular", str(ctx.exception))

    def test_los_md_de_redesign_v2_si_valen(self):
        """El harvest de redes vive ahi y es registro de fuentes externas."""
        build._validar_evidencia("/x", "redesign-v2/DATOS-REALES-harvest.md#L46")

    def test_ninguna_evidencia_real_cita_una_maqueta(self):
        for p in build.cargar_programas():
            for fuente in p["evidence"]:
                build._validar_evidencia(p["slug"], fuente)


class TestOfertaEnHistoricos(unittest.TestCase):
    """La pagina del diplomado declaraba un Offer con availability InStock y
    precios 19500/26000 para un programa cuya edicion cerro. Structured data es
    lo que Google lee como producto comprable."""

    PROGRAMAS = [
        {"slug": "/curso-lenguaje-felino", "status": "available",
         "offer": {"price_mxn": 1400, "payment_type": "unico", "hours": 12,
                   "topics_count": 11, "access_months": 5}},
        {"slug": "/diplomado-x", "status": "historical"},
    ]

    def _pagina(self, tmp, cuerpo):
        f = Path(tmp) / "diplomado.html"
        f.write_text(cuerpo, encoding="utf-8")
        return {f: "/diplomado-x"}

    def test_offers_en_json_ld_de_un_historico_es_violacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, '<script type="application/ld+json">'
                                        '{"@type":"Course","offers":{"@type":"Offer","price":"19500"}}</script>')
            hallados = build.buscar_oferta_en_historicos(paginas, self.PROGRAMAS)
            self.assertTrue(any("offers" in m for _, m in hallados), hallados)

    def test_precio_propio_en_un_historico_es_violacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, "<p>Desde $19,500 MXN</p>")
            hallados = build.buscar_oferta_en_historicos(paginas, self.PROGRAMAS)
            self.assertTrue(any("precio propio" in m for _, m in hallados), hallados)

    def test_el_precio_del_curso_disponible_si_puede_cruzar_venderse(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, "<p>Empieza con el curso de gatos: $1,400 MXN</p>")
            self.assertEqual(build.buscar_oferta_en_historicos(paginas, self.PROGRAMAS), [])

    def test_las_paginas_historicas_reales_no_publican_oferta(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        hallados = build.buscar_oferta_en_historicos(paginas, build.cargar_programas())
        self.assertEqual(hallados, [], f"ofertas en programas historicos: {hallados}")


class TestFechaSinConfirmar(unittest.TestCase):
    """COWORK-GUIA-MONTAJE.md lista "fecha de la edicion 2026" entre los datos
    que Angel no ha dado, y fija "por confirmar" como la forma de publicarlo.
    Sin el marcador, la fecha se lee como compromiso firme."""

    def _pagina(self, tmp, cuerpo):
        f = Path(tmp) / "curso.html"
        f.write_text(cuerpo, encoding="utf-8")
        return {f: "/cursos/x"}

    def test_fecha_de_apertura_sin_marcador_es_violacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, '<span class="pill">Abre Sep 2026</span>')
            hallados = build.buscar_fecha_sin_confirmar(paginas)
            self.assertEqual([(a, t) for a, _, t in hallados], [("curso.html", "Abre Sep 2026")])

    def test_con_el_marcador_pasa(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, '<span class="pill">Abre Sep 2026 por confirmar</span>')
            self.assertEqual(build.buscar_fecha_sin_confirmar(paginas), [])

    def test_el_marcador_vale_aunque_lo_separe_el_cierre_de_un_span(self):
        # Es la forma real del catalogo: <span class="from">Inicia</span>Sep 2026...
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(
                tmp,
                '<span class="lam-price"><span class="from">Inicia</span>'
                'Sep 2026 <span class="tbd-mark">por confirmar</span></span>',
            )
            self.assertEqual(build.buscar_fecha_sin_confirmar(paginas), [])

    def test_una_fecha_historica_sin_verbo_no_se_toca(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, "<p>La 3a edicion cerro en jun 2025.</p>")
            self.assertEqual(build.buscar_fecha_sin_confirmar(paginas), [])

    def test_el_marcador_de_la_siguiente_celda_no_cuenta(self):
        # Sin tope de distancia, un "por confirmar" de otra tarjeta absolveria
        # a esta. El margen tiene que cubrir el cierre de spans, no media pagina.
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(
                tmp,
                "<span>Abre Sep 2026</span>" + "<td>relleno</td>" * 12 + "<span>por confirmar</span>",
            )
            self.assertEqual(len(build.buscar_fecha_sin_confirmar(paginas)), 1)

    def test_las_paginas_reales_no_prometen_fecha_firme(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        hallados = build.buscar_fecha_sin_confirmar(paginas)
        self.assertEqual(hallados, [], f"fechas sin marcador: {hallados}")


class TestAnclasSinDestino(unittest.TestCase):
    """113 de las 118 reglas activas apuntan a /cursos#historico-*. Si el id no
    existe, el 301 aterriza arriba de la pagina en vez de en su seccion."""

    # Vacio desde que las laminas 15-18 cubrieron los cuatro temas que
    # faltaban (medicina-preventiva, manejo-datos, imagenologia-caballos,
    # diagnostico-terapeutica). Se queda como constante, y no inline, para que
    # reabrir el hueco sea un cambio explicito y documentado en vez de un
    # borrado silencioso de tarjetas.
    SIN_TARJETA_TODAVIA = set()

    def _paginas(self, tmp, cuerpo_cursos):
        f = Path(tmp) / "catalogo.html"
        f.write_text(cuerpo_cursos, encoding="utf-8")
        return {f: "/cursos"}

    def test_detecta_el_ancla_que_no_existe(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(tmp, '<article id="historico-felidos"></article>')
            reglas = [{"source": "/x", "destination": "/cursos#historico-inventado", "statusCode": 301}]
            self.assertEqual(build.buscar_anclas_sin_destino(reglas, paginas),
                             [("/x", "/cursos#historico-inventado")])

    def test_no_marca_el_ancla_que_si_existe(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(tmp, '<article id="historico-felidos"></article>')
            reglas = [{"source": "/x", "destination": "/cursos#historico-felidos", "statusCode": 301}]
            self.assertEqual(build.buscar_anclas_sin_destino(reglas, paginas), [])

    def test_ignora_reglas_sin_fragmento_y_destinos_no_publicados(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(tmp, "<p>sin ids</p>")
            reglas = [
                {"source": "/a", "destination": "/cursos", "statusCode": 301},
                {"source": "/b", "destination": "/egresados#cohorte-2019", "statusCode": 301},
            ]
            self.assertEqual(build.buscar_anclas_sin_destino(reglas, paginas), [])

    def test_las_anclas_huerfanas_reales_son_solo_las_de_temas_sin_tarjeta(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        with build.REDIRECTS_CSV.open(encoding="utf-8") as f:
            activas, _ = build.convertir_redirects_bulk(list(csv.DictReader(f)), set(paginas.values()))
        huerfanas = {d.split("#", 1)[1] for _, d in build.buscar_anclas_sin_destino(activas, paginas)}
        self.assertEqual(
            huerfanas, self.SIN_TARJETA_TODAVIA,
            f"anclas huerfanas nuevas (alguien rompio o borro una tarjeta): "
            f"{huerfanas - self.SIN_TARJETA_TODAVIA}",
        )

    def test_cada_tema_sin_ficha_propia_no_promete_convocatoria(self):
        """Las laminas 15-18 existen solo porque hay 301 apuntando a ellas.
        La evidencia sostiene que el tema se impartio y nada mas: si alguna
        gana un precio, una fecha o un CTA de inscripcion, es una afirmacion
        que ninguna fuente respalda."""
        catalogo = build.SRC / "catalogo.html"
        texto = catalogo.read_text(encoding="utf-8")
        for ancla in ("historico-medicina-preventiva", "historico-diagnostico-terapeutica",
                      "historico-imagenologia-caballos", "historico-manejo-datos"):
            with self.subTest(ancla=ancla):
                inicio = texto.index(f'id="{ancla}"')
                tarjeta = texto[inicio:texto.index("</article>", inicio)]
                self.assertNotRegex(tarjeta, r"\$\s?[\d,]+")
                self.assertNotRegex(
                    tarjeta,
                    r"\b(?:Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\.?\s+20\d\d\b",
                )
                self.assertNotRegex(tarjeta, r"(?i)inscr|avisarme|matricul")


if __name__ == "__main__":
    unittest.main()
