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
    REGLAS = [
        {"source": "/viejo", "destination": "/nuevo", "statusCode": 301},
        {"source": "/otro", "destination": "/cursos#historico-felidos", "statusCode": 301},
    ]

    def setUp(self):
        self.config = json.loads(build.generar_vercel_json(self.REGLAS))

    def test_campos_obligatorios(self):
        self.assertEqual(self.config["$schema"], "https://openapi.vercel.sh/vercel.json")
        self.assertIs(self.config["cleanUrls"], True)
        self.assertIs(self.config["trailingSlash"], False)
        self.assertEqual(self.config["buildCommand"], "")

    def test_no_usa_bulk_redirects_que_es_de_pago(self):
        """Invierte a `test_no_usa_el_redirect_inline_viejo`, que fijaba lo
        contrario. Lo decidio un dato empirico, no una preferencia: el deploy
        del 2026-08-03 fallo con "Bulk redirects are not available for teams on
        the Hobby plan", asi que esa propiedad no publicaba ni una regla."""
        self.assertNotIn("bulkRedirectsPath", self.config)
        self.assertEqual(len(self.config["redirects"]), 2)

    def test_emite_301_y_no_el_308_de_permanent(self):
        for regla in self.config["redirects"]:
            with self.subTest(source=regla["source"]):
                self.assertEqual(regla["statusCode"], 301)
                self.assertNotIn("permanent", regla)

    def test_la_copia_de_revision_no_se_indexa_pero_el_sitio_real_si(self):
        """Angel quiere ensenar el sitio y que lo revisen ANTES de aprobarlo,
        asi que vive publico en celebios.vercel.app mientras celebios.com sigue
        en Wix. El riesgo es que Google indexe la copia de revision: los
        canonical apuntan a www.celebios.com/<ruta> y esas rutas hoy NO existen,
        y un canonical que apunta a un 404 lo ignora.

        La regla va condicionada al host, NO como noindex global ni como
        Disallow en robots.txt: esas dos hay que acordarse de quitarlas el dia
        del cutover, y nadie se acuerda. Asi deja de coincidir sola."""
        reglas = [h for h in self.config["headers"]
                  if any(x["key"] == "X-Robots-Tag" for x in h["headers"])]
        self.assertEqual(len(reglas), 1, "deberia haber exactamente una regla de noindex")
        regla = reglas[0]
        self.assertEqual(regla["source"], "/(.*)")
        self.assertIn("noindex", regla["headers"][0]["value"])
        # condicionada al host: sin esto el sitio real tampoco se indexaria
        self.assertEqual(regla["has"], [{"type": "host", "value": r"(.*)\.vercel\.app"}])

    def test_robots_no_bloquea_el_sitio_real(self):
        """El noindex de la copia de revision va por cabecera, no por robots.
        Si alguien lo "arregla" metiendo un Disallow global aqui, el dia del
        cutover el sitio real sale de Google sin que nadie lo note."""
        robots = build.generar_robots()
        self.assertIn("Allow: /", robots)
        self.assertNotIn("Disallow: /\n", robots)

    def test_conserva_el_fragmento_del_destino(self):
        destinos = [r["destination"] for r in self.config["redirects"]]
        self.assertIn("/cursos#historico-felidos", destinos)

    def test_revienta_si_se_pasa_del_tope_del_esquema(self):
        # maxItems de `redirects` en openapi.vercel.sh/vercel.json. Pasarse
        # sin avisar dejaria reglas fuera en silencio.
        muchas = [{"source": f"/x{i}", "destination": "/", "statusCode": 301}
                  for i in range(build.MAX_REDIRECTS_INLINE + 1)]
        with self.assertRaises(SystemExit) as ctx:
            build.generar_vercel_json(muchas)
        self.assertIn(str(build.MAX_REDIRECTS_INLINE), str(ctx.exception))

    def test_el_tope_admite_el_inventario_actual(self):
        with build.REDIRECTS_CSV.open(encoding="utf-8") as f:
            activas, _ = build.convertir_redirects_bulk(
                list(csv.DictReader(f)), build.rutas_canonicas_fuente())
        self.assertLessEqual(len(activas), build.MAX_REDIRECTS_INLINE)

    def test_trae_headers_de_seguridad(self):
        headers_planos = [h for bloque in self.config["headers"] for h in bloque["headers"]]
        claves = {h["key"] for h in headers_planos}
        self.assertIn("X-Content-Type-Options", claves)
        self.assertIn("X-Frame-Options", claves)

    def test_media_se_cachea_pero_no_como_inmutable(self):
        """1.7 MB de imagenes se revalidaban en cada visita. Ahora se cachean,
        pero por la misma razon que /brand/ no van como `immutable`: los nombres
        no llevan hash de contenido, y reemplazar una imagen conservando el
        nombre pasa de verdad -- las 15 laminas de ambiente se re-generaron sin
        cambiar de nombre. Con `immutable` nadie habria visto la nueva."""
        bloque = next(b for b in self.config["headers"] if b["source"] == "/media/(.*)")
        valor = next(h["value"] for h in bloque["headers"] if h["key"] == "Cache-Control")
        self.assertNotIn("immutable", valor)
        self.assertIn("max-age=86400", valor)
        self.assertIn("stale-while-revalidate", valor)

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

    def test_ya_no_queda_ninguna_regla_diferida(self):
        """Sustituye a `test_hay_reglas_diferidas_conocidas_pre_task3`, que
        afirmaba lo contrario porque los destinos aun no existian. Al publicar
        /egresados, /contacto, /admisiones y /aviso-de-privacidad, y al resolver
        /nosotros y la ficha del diplomado, el diferimiento bajo de 251 a 0.
        Volver a diferir una regla es ahora una regresion, no un pendiente."""
        with (RAIZ / "migracion" / "redirects.csv").open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        _, diferidas = build.convertir_redirects_bulk(filas, build.rutas_canonicas_fuente())
        self.assertEqual(
            [(d["source"], d["destination"], "+".join(d["reasons"])) for d in diferidas], []
        )


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

    def test_vercel_json_publica_los_redirects_inline(self):
        config = json.loads((self.salida / "vercel.json").read_text(encoding="utf-8"))
        self.assertNotIn("bulkRedirectsPath", config)
        self.assertGreater(len(config["redirects"]), 300)
        self.assertEqual({r["statusCode"] for r in config["redirects"]}, {301})

    def test_los_redirects_que_se_publican_tienen_la_forma_exacta(self):
        """Vivian en site/migracion/redirects.csv, el insumo de
        bulkRedirectsPath. Esa propiedad publica CERO reglas en el plan Hobby
        (lo dijeron los logs del deploy del 2026-08-03), asi que el CSV no lo
        leia nadie y solo publicaba el mapa de la migracion. Las reglas viajan
        inline en vercel.json: ahi es donde hay que comprobarlas."""
        reglas = json.loads((self.salida / "vercel.json").read_text(encoding="utf-8"))["redirects"]
        self.assertTrue(reglas)
        for r in reglas:
            with self.subTest(source=r["source"]):
                self.assertEqual(set(r), {"source", "destination", "statusCode"})
                self.assertEqual(r["statusCode"], 301)

    def test_ningun_redirect_sombrea_una_pagina_publicada(self):
        rutas_publicadas = build.rutas_canonicas_fuente()
        reglas = json.loads((self.salida / "vercel.json").read_text(encoding="utf-8"))["redirects"]
        for r in reglas:
            with self.subTest(source=r["source"]):
                self.assertNotIn(r["source"], rutas_publicadas)

    def test_el_csv_de_migracion_ya_no_se_publica(self):
        """17 KB con el mapa completo de la migracion, incluidas rutas viejas
        que ya no queremos anunciar."""
        self.assertFalse((self.salida / "migracion").exists())

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
    def test_cutover_revienta_antes_de_escribir_si_queda_una_diferida(self):
        """Antes este test se apoyaba en que el repo real tenia diferidas. Ya
        no las tiene, asi que la regla que dispara el fallo se inyecta aqui:
        el mecanismo hay que seguir probandolo, y ahora aislado del estado."""
        with tempfile.TemporaryDirectory() as tmp:
            csv_falso = Path(tmp) / "redirects.csv"
            csv_falso.write_text(
                "source_url,destination_path,status_code\n"
                "https://www.celebios.com/lo-que-sea,/ruta-que-no-existe,301\n",
                encoding="utf-8",
            )
            salida = Path(tmp) / "site"
            with mock.patch.object(build, "REDIRECTS_CSV", csv_falso):
                with mock.patch.dict(os.environ, {}, clear=False):
                    os.environ.pop("GA4_MEASUREMENT_ID", None)
                    with self.assertRaises(SystemExit) as ctx:
                        build.construir(salida=salida, cutover=True)
            self.assertIn("cutover", str(ctx.exception).lower())
            self.assertFalse(salida.exists())

    def test_cutover_pasa_con_el_estado_real(self):
        """El invariante nuevo: el sitio esta en condiciones de corte. Si algo
        vuelve a diferir una regla o a dejar un ancla sin destino, esto avisa."""
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GA4_MEASUREMENT_ID", None)
                build.construir(salida=salida, cutover=True)
            self.assertTrue((salida / "vercel.json").exists())

    def test_preview_sin_cutover_tampoco_revienta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GA4_MEASUREMENT_ID", None)
                build.construir(salida=salida, cutover=False)
            self.assertTrue((salida / "vercel.json").exists())


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


class TestPreciosFueraDeContrato(unittest.TestCase):
    """La guarda anterior solo miraba paginas de programa historico, y exigia el
    sufijo MXN pegado al importe. La tabla de /cursos no es la pagina de ningun
    programa y sus celdas llevan el importe pelado, con la moneda en el
    encabezado de columna: publico $1,200, $1,600, $19,500 y $26,000 durante un
    mes. Los dos primeros no tenian fuente en ningun archivo del repositorio."""

    PROGRAMAS = [
        {"slug": "/curso-lenguaje-felino", "status": "available",
         "offer": {"price_mxn": 1400, "payment_type": "unico", "hours": 12,
                   "topics_count": 11, "access_months": 5}},
        {"slug": "/diplomado-x", "status": "historical"},
    ]

    def _pagina(self, tmp, cuerpo, nombre="catalogo.html"):
        f = Path(tmp) / nombre
        f.write_text(cuerpo, encoding="utf-8")
        return {f: "/cursos"}

    def test_caza_el_importe_sin_sufijo_de_moneda(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, '<td class="pt-price">$19,500</td>')
            hallados = build.buscar_precios_fuera_de_contrato(paginas, self.PROGRAMAS)
            self.assertEqual(hallados, [("catalogo.html", ["$19,500"])])

    def test_el_precio_del_programa_disponible_pasa_en_sus_dos_formas(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, '<p>$1,400 MXN</p><td class="pt-price">$1,400</td>')
            self.assertEqual(build.buscar_precios_fuera_de_contrato(paginas, self.PROGRAMAS), [])

    def test_el_articulo_de_sueldos_puede_citar_rangos_salariales(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, "<p>de $7,600 a $17,000 MXN al mes</p>",
                                   nombre="recurso-cuanto-gana-veterinario.html")
            self.assertEqual(build.buscar_precios_fuera_de_contrato(paginas, self.PROGRAMAS), [])

    def test_el_sitio_real_no_publica_ni_un_importe_sin_contrato(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        hallados = build.buscar_precios_fuera_de_contrato(paginas, build.cargar_programas())
        self.assertEqual(hallados, [], f"importes sin respaldo del contrato: {hallados}")

    def test_solo_un_programa_del_contrato_lleva_precio(self):
        conprecio = [p["slug"] for p in build.cargar_programas()
                     if isinstance(p.get("offer"), dict) and p["offer"].get("price_mxn")]
        self.assertEqual(conprecio, ["/curso-lenguaje-felino"])


class TestAperturaAnunciada(unittest.TestCase):
    """Una fecha de apertura es una promesa aunque lleve marcador. El catalogo
    anunciaba "Abre Sep 2026 por confirmar" de dos programas que el contrato
    marca historicos: pasaba la guarda del marcador y aun asi prometia."""

    def _pagina(self, tmp, cuerpo):
        f = Path(tmp) / "catalogo.html"
        f.write_text(cuerpo, encoding="utf-8")
        return {f: "/cursos"}

    def test_la_fecha_marcada_por_confirmar_sigue_siendo_una_promesa(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, '<span class="pill">Abre Sep 2026 por confirmar</span>')
            hallados = build.buscar_apertura_anunciada(paginas)
            self.assertEqual([t for _, _, t in hallados], ["Abre Sep 2026"])

    def test_caza_las_otras_formas_de_anunciar_apertura(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, "<p>Inicia Oct 2026</p><p>Comienza enero 2027</p>")
            self.assertEqual(len(build.buscar_apertura_anunciada(paginas)), 2)

    def test_una_fecha_que_no_anuncia_apertura_no_es_violacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._pagina(tmp, "<p>La tercera edicion cerro en junio 2025.</p>")
            self.assertEqual(build.buscar_apertura_anunciada(paginas), [])

    def test_el_sitio_real_no_anuncia_ninguna_apertura(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        hallados = build.buscar_apertura_anunciada(paginas)
        self.assertEqual(hallados, [], f"aperturas anunciadas: {hallados}")


class TestPackageJsonDeSalida(unittest.TestCase):
    """Copiar el package.json de la raiz tal cual rompia el deploy: arrastra
    `"build": "python build.py"`, Vercel lo autodetectaba y trataba de
    reconstruir un sitio ya construido desde un directorio sin redesign-v2/.
    `npm run build` salia con codigo 2 y el despliegue moria."""

    def test_no_publica_scripts_de_construccion(self):
        salida = json.loads(build.package_json_de_salida())
        self.assertNotIn("scripts", salida)

    def test_conserva_lo_que_la_funcion_serverless_necesita(self):
        salida = json.loads(build.package_json_de_salida())
        fuente = json.loads((build.RAIZ / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(salida["dependencies"], fuente["dependencies"])
        self.assertEqual(salida["type"], fuente["type"])
        self.assertIn("@vercel/blob", salida["dependencies"])

    def test_el_vercel_json_declara_que_no_hay_build(self):
        self.assertEqual(json.loads(build.generar_vercel_json())["buildCommand"], "")

    def test_el_construido_no_trae_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "site"
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GA4_MEASUREMENT_ID", None)
                build.construir(salida=salida)
            pkg = json.loads((salida / "package.json").read_text(encoding="utf-8"))
            self.assertNotIn("scripts", pkg)
            self.assertTrue((salida / "api" / "video.js").exists())


class TestImagenesPublicadas(unittest.TestCase):
    """Angel: "imagenes polemicas nos pueden causar problemas". En un sitio de
    fauna silvestre una foto clinica sacada de contexto se lee como maltrato, y
    los rostros de alumnos son dato personal bajo la misma LFPDPPP que cita el
    aviso de privacidad. Por eso el conjunto publicado es una lista cerrada:
    anadir una imagen tiene que ser un cambio deliberado, no un descuido."""

    # Laminas de ambiente GENERADAS con IA (Higgsfield soul_location, 2026-08-03),
    # no fotografia de CELEBIOS. Ilustran los articulos, que salian a texto pelon.
    # Son paisaje deliberadamente: la audiencia son MVZ y un animal generado con la
    # anatomia mal lo cazan al instante. Un paisaje no tiene anatomia que desmentir.
    # El prefijo `ambiente-` es lo unico que impide que dentro de seis meses alguien
    # las confunda con archivo real, por eso hay un test que lo vigila.
    GENERADAS = {
        "ambiente-bosque-tarde", "ambiente-claro-luz", "ambiente-dosel-amanecer",
        "ambiente-dosel-contraluz", "ambiente-follaje-lluvia", "ambiente-hojarasca",
        "ambiente-humedal", "ambiente-matorral-seco", "ambiente-niebla-canada",
        "ambiente-ramas-cielo", "ambiente-rio-montana", "ambiente-selva-nublada",
        # los tres articulos de gatos: interior domestico, sin animal. El
        # primer intento pedia "no cats" y el modelo puso un gato en la mancha
        # de luz -- nombrar algo en negativo lo invoca. Se rehicieron sin
        # mencionar animales en absoluto.
        "ambiente-luz-interior", "ambiente-cortina-luz", "ambiente-rincon-anochecer",
    }

    PUBLICADAS = {
        # material propio de la escuela, sin personas
        "cartel-contencion-quimica-anestesia", "cartel-diagnostico-terapeutica",
        "cartel-medicina-preventiva-2017",
        "cartel-nutricion-2019",
        "fauna-cocodrilo-habitat", "fauna-grulla-coronada",
        "fauna-loro-alimentacion", "fauna-rapaz-alas-abiertas",
        # practicas reencuadradas en el animal, las manos o el instrumento: la
        # foto sigue siendo documental y real, pero ya no hay rostro que
        # identifique a nadie, asi que deja de ser dato personal.
        "practica-ecografo-consola", "practica-equino-auscultacion",
        "practica-lechuza-auscultacion", "practica-manejo-quelonio",
    } | GENERADAS
    # NINGUN nombre de archivo de esta lista es evidencia de lo que contiene:
    # vienen del scraping del Wix y cinco mentian descaradamente (un logo de la
    # UAEH se llamaba "cartel-anestesia-cirugia-2013", una foto de una persona
    # con un erizo se llamaba "cartel-curso-tarantulas-2014"). Ninguna prueba
    # automatica puede detectar eso. Las 13 se abrieron y se miraron una por una
    # el 2026-08-03; cualquier alta futura exige lo mismo.
    RETIRADAS = {
        # se leen mal fuera de su contexto clinico
        "practica-guacamaya-exploracion", "practica-perezoso-manejo",
        "practica-guacamaya-monitoreo", "practica-loro-manejo",
        # ademas: entra al campo un antebrazo desnudo sin guante a centimetros
        # de un perezoso silvestre. Para una escuela que ensena riesgo
        # zoonotico eso lo nota su propia audiencia.
        "practica-perezoso-auscultacion",
        # lo unico que aportaban era el grupo entero
        "practica-clinica-grupo", "practica-sesion-campo",
        "practica-equino-grupo", "practica-imagenologia-equipo",
        # no eran carteles: dos logos de terceros y una foto con rostro
        "cartel-anestesia-cirugia-2013", "cartel-nutricion-fauna-cautiverio",
        "cartel-curso-tarantulas-2014",
        # cartel real, pero sin edicion a la que pertenecer: anuncia
        # "inscripciones abiertas" de 2024 y trae ocho logos de alianzas cuyo
        # verbo exacto sigue sin fuente
        "cartel-ortopedia-aves-silvestres", "cartel-rescate-rehabilitacion-2024",
        # el escudo de la UATx ocupa la columna izquierda entera, en las mismas
        # filas que el titulo: no hay recorte que lo quite sin destruir el
        # cartel. Y ademas publica un contacto en Gmail, que contradice la
        # advertencia antifraude de /admisiones. Queda la ficha de texto, como
        # en las ediciones 01, 03, 04 y 08.
        "cartel-medicina-preventiva-2014",
    }
    # Cambiaron de nombre porque el nombre no describia el archivo.
    RENOMBRADAS = {
        "practica-ave-clinica-grupo", "practica-ecografo-alumnas",
        "cartel-rehabilitacion-fauna-2019",
    }

    def _en_disco(self):
        return {f.stem for f in (build.SRC / "media").glob("*.webp")}

    def test_el_conjunto_publicado_es_el_declarado(self):
        self.assertEqual(self._en_disco(), self.PUBLICADAS)

    def test_lo_generado_se_distingue_de_lo_documental(self):
        """La linea entre "foto real de una practica" y "paisaje generado" no
        puede depender de que alguien se acuerde. Vive en el prefijo."""
        for slug in self.GENERADAS:
            with self.subTest(slug=slug):
                self.assertTrue(slug.startswith("ambiente-"))
        for slug in self.PUBLICADAS - self.GENERADAS:
            with self.subTest(slug=slug):
                self.assertFalse(slug.startswith("ambiente-"))

    def test_la_banda_de_ambiente_nunca_lleva_texto_encima(self):
        """El primer intento puso la lamina DETRAS del titulo, a 32% de
        opacidad. Medido: el kicker cian (#2FA8C9) caia de 5.18:1 a menos de
        3:1 en las doce, y para devolverlo a 4.5:1 habia que bajar la opacidad
        a 0.05 -- invisible. Una foto detras de ese texto es incompatible con
        ese cian a cualquier opacidad util, asi que la banda va aparte y vacia.
        Si alguien vuelve a meterle contenido, vuelve el problema."""
        bandas = 0
        for f in sorted(build.SRC.glob("*.html")):
            texto = f.read_text(encoding="utf-8")
            with self.subTest(archivo=f.name):
                self.assertNotIn("art-fondo", texto)   # el enfoque descartado
            for m in re.finditer(r'<div class="art-banda"([^>]*)></div>', texto):
                bandas += 1
                with self.subTest(archivo=f.name):
                    self.assertIn('aria-hidden="true"', m.group(1))
            self.assertEqual(texto.count("art-banda") - texto.count(".art-banda{"),
                             len(re.findall(r'<div class="art-banda"[^>]*></div>', texto)),
                             f"{f.name}: alguna banda dejo de estar vacia")
        self.assertEqual(bandas, len(self.GENERADAS))

    def test_lo_generado_nunca_se_presenta_como_documental(self):
        """Una imagen generada no puede entrar como <img> con alt ni llevar pie
        de foto: eso la presentaria como registro de algo que paso. Va como
        capa de fondo decorativa y nada mas."""
        for f in sorted(build.SRC.glob("*.html")):
            texto = f.read_text(encoding="utf-8")
            for tag in re.findall(r"<img[^>]*>", texto):
                m = re.search(r"/media/([a-z0-9-]+)\.webp", tag)
                if m:
                    with self.subTest(archivo=f.name, imagen=m.group(1)):
                        self.assertNotIn(m.group(1), self.GENERADAS)

    def test_las_retiradas_no_vuelven(self):
        fuera = self.RETIRADAS | self.RENOMBRADAS
        self.assertEqual(self._en_disco() & fuera, set())
        referidas = set()
        for f in build.SRC.glob("*.html"):
            referidas |= set(re.findall(r"/media/([a-z0-9-]+)\.webp",
                                        f.read_text(encoding="utf-8")))
        self.assertEqual(referidas & fuera, set())

    def test_ninguna_imagen_queda_sin_usar(self):
        usadas = set()
        for f in build.SRC.glob("*.html"):
            usadas |= set(re.findall(r"/media/([a-z0-9-]+)\.webp", f.read_text(encoding="utf-8")))
        self.assertEqual(self._en_disco() - usadas, set())

    def test_toda_imagen_lleva_alt_y_dimensiones(self):
        """Sin width/height la pagina salta al cargar; sin alt no es accesible."""
        for f in sorted(build.SRC.glob("*.html")):
            for tag in re.findall(r"<img[^>]*>", f.read_text(encoding="utf-8")):
                if "/media/" not in tag:
                    continue
                with self.subTest(archivo=f.name, tag=tag[:60]):
                    self.assertRegex(tag, r'alt="[^"]+"')
                    self.assertRegex(tag, r'width="\d+"')
                    self.assertRegex(tag, r'height="\d+"')

    @staticmethod
    def _dims_webp(ruta):
        """Tamano real del WebP leyendo la cabecera. A mano y no con Pillow
        porque el repo no lo lista como dependencia y un test no deberia
        anadir una para medir dos enteros."""
        b = ruta.read_bytes()
        if b[12:16] == b"VP8X":                                    # extendido
            return (int.from_bytes(b[24:27], "little") + 1,
                    int.from_bytes(b[27:30], "little") + 1)
        if b[12:16] == b"VP8L":                                    # sin perdida
            n = int.from_bytes(b[21:25], "little")
            return (n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1
        return (int.from_bytes(b[26:28], "little") & 0x3FFF,       # con perdida
                int.from_bytes(b[28:30], "little") & 0x3FFF)

    def test_las_dimensiones_declaradas_son_las_reales(self):
        """Las laminas de fauna venian con width="1200" height="900" inventado
        sobre archivos de 843x385. Como la galeria usa height:auto, el navegador
        reserva la caja con esos numeros: maquetaba huecos que no existian y la
        pagina saltaba al cargar cada foto."""
        for f in sorted(build.SRC.glob("*.html")):
            for tag in re.findall(r"<img[^>]*>", f.read_text(encoding="utf-8")):
                m = re.search(r"/media/([a-z0-9-]+)\.webp", tag)
                if not m:
                    continue
                declarado = (int(re.search(r'width="(\d+)"', tag).group(1)),
                             int(re.search(r'height="(\d+)"', tag).group(1)))
                with self.subTest(archivo=f.name, imagen=m.group(1)):
                    self.assertEqual(
                        declarado,
                        self._dims_webp(build.SRC / "media" / f"{m.group(1)}.webp"))


class TestTarjetaSocial(unittest.TestCase):
    """Mientras el sitio vive en celebios.vercel.app para revision, un og:image
    absoluto a www.celebios.com da 404 -- ahi sigue el Wix viejo -- y quien
    comparta el link ve la vista previa rota. Comprobado en vivo: 404 en el
    dominio real, 200 en el de revision."""

    HTML = ('<meta property="og:image" content="https://www.celebios.com/brand/og-celebios.jpg">'
            '<meta name="twitter:image" content="https://www.celebios.com/brand/og-celebios.jpg">'
            '<link rel="canonical" href="https://www.celebios.com/galeria">')

    def test_en_revision_apunta_al_host_que_sirve(self):
        salida = build.apuntar_tarjeta_social(self.HTML, cutover=False)
        self.assertEqual(salida.count("https://celebios.vercel.app/brand/og-celebios.jpg"), 2)
        self.assertNotIn('content="https://www.celebios.com/brand/', salida)

    def test_en_cutover_vuelve_al_dominio_definitivo(self):
        """Sin esto habria que acordarse de revertirlo el dia del corte, y nadie
        se acuerda."""
        self.assertEqual(build.apuntar_tarjeta_social(self.HTML, cutover=True), self.HTML)

    def test_el_canonical_nunca_se_toca(self):
        """Debe seguir apuntando a celebios.com en los dos modos: es lo que hace
        que Google consolide ahi y que la copia de revision no compita."""
        for cutover in (False, True):
            with self.subTest(cutover=cutover):
                self.assertIn('rel="canonical" href="https://www.celebios.com/galeria"',
                              build.apuntar_tarjeta_social(self.HTML, cutover))

    def test_la_imagen_social_existe_en_disco(self):
        self.assertTrue((build.SRC / "brand" / "og-celebios.jpg").exists())


class TestJavaScriptPublicado(unittest.TestCase):
    """Al JS inline de las 33 paginas le faltaban TODOS los parentesis de
    invocacion. `(function{` era la punta visible: no compilaba. Lo peligroso
    era el resto, que compila y no hace nada -- `onScroll;`, un IIFE que se
    declara y no se llama, `getBoundingClientRect` sin `()`. Cero errores en
    consola y el menu movil, la barra de compra y los filtros del catalogo
    muertos desde el primer dia.

    Se descubrio abriendo un navegador de verdad. Ninguna prueba lo miraba."""

    def _guarda(self, js):
        p = Path(tempfile.mkdtemp()) / "x.html"
        p.write_text(f"<script>\n{js}\n</script>", encoding="utf-8")
        return build.buscar_javascript_roto([p])

    def test_el_sitio_publicado_no_tiene_llamadas_mutiladas(self):
        self.assertEqual(build.buscar_javascript_roto(list(build.SRC.glob("*.html"))), [])

    def test_caza_la_funcion_que_no_compila(self):
        self.assertTrue(self._guarda("(function{\n})();"))

    def test_caza_el_metodo_sin_parentesis(self):
        """Devuelve la funcion en vez de llamarla, y `.bottom` sale undefined
        sin lanzar: el sintoma es que no pasa nada."""
        self.assertTrue(self._guarda("(function(){\n var r = el.getBoundingClientRect.bottom;\n})();"))

    def test_caza_la_llamada_suelta(self):
        self.assertTrue(self._guarda("(function(){\n var f = function(){};\n f;\n})();"))

    def test_caza_el_iife_que_nunca_se_invoca(self):
        self.assertTrue(self._guarda("(function(){\n var x = 1;\n});"))

    def test_no_marca_codigo_correcto(self):
        self.assertEqual(self._guarda(
            "(function(){\n var f = function(){ el.getBoundingClientRect().top; };\n f();\n})();"), [])

    def test_el_json_ld_publicado_parsea(self):
        self.assertEqual(build.buscar_json_ld_malformado(list(build.SRC.glob("*.html"))), [])


class TestPromesasSinRespaldo(unittest.TestCase):
    """La portada anunciaba "Disponible" dos cursos que programas.json marca
    `planned` -- "nunca impartido" -- con duraciones de 10 h y 14 h que no salen
    de ninguna fuente. La guarda vieja no lo veia porque miraba `data-estado`, y
    la portada no tiene ni uno."""

    def test_ninguna_tarjeta_promete_lo_que_el_contrato_no_respalda(self):
        self.assertEqual(
            build.buscar_promesas_sin_respaldo(
                [p for p in build.SRC.glob("*.html") if "canonical" in p.read_text(encoding="utf-8")],
                build.cargar_programas()),
            [])

    def test_la_duracion_se_permite_en_los_historicos(self):
        """Las 170 h del diplomado son un hecho documentado, no una promesa: el
        programa si se impartio. Solo se prohibe inventar duracion de los que
        nunca existieron."""
        estados = {p["status"] for p in build.cargar_programas()}
        self.assertIn("historical", estados)
        self.assertIn("planned", estados)


class TestAvisoDePrivacidad(unittest.TestCase):
    """El aviso heredado de Wix citaba la Ley General ... en Posesion de
    SUJETOS OBLIGADOS, que rige a entes publicos. CELEBIOS es una S.C., o sea
    un particular: le aplica la LFPDPPP. Angel autorizo la correccion el
    2026-08-03. Estos tests existen para que no se revierta al re-migrar."""

    def _texto(self):
        return (build.SRC / "aviso-de-privacidad.html").read_text(encoding="utf-8")

    def test_no_cita_la_ley_de_sujetos_obligados(self):
        self.assertNotRegex(self._texto(), r"(?i)Sujetos\s+Obligados")

    def test_cita_la_ley_de_particulares(self):
        self.assertRegex(self._texto(), r"(?i)Posesi.n\s+de\s+los\s+Particulares")

    def test_declara_los_cuatro_derechos_arco(self):
        texto = self._texto()
        for derecho in ("Acceso", "Rectificación", "Cancelación", "Oposición"):
            with self.subTest(derecho=derecho):
                self.assertIn(derecho, texto)

    def test_no_niega_toda_transferencia_habiendo_pasarela_de_pago(self):
        """Cobrar por Stripe/PayPal implica que un tercero trate datos. Un
        aviso que afirma que NO hay ninguna transferencia deja de ser cierto
        en cuanto se conecta la pasarela."""
        texto = self._texto()
        self.assertNotIn("no se realizarán transferencias de datos personales", texto)
        self.assertIn("plataformas de pago externas", texto)

    def test_declara_cookies_y_almacenamiento(self):
        """El art. 30 del Reglamento obliga a informar los mecanismos que
        recaban datos de forma automatica. El aula guarda el testigo de sesion
        del alumno en el navegador, y GA4 esta a una variable de entorno de
        distancia: sin esta clausula, encenderlo publica 33 paginas que ponen
        cookies con un aviso que no las menciona."""
        self.assertRegex(self._texto(), r"(?i)cookies")

    def test_declara_el_comprobante_de_pago_como_dato_financiero(self):
        """El aviso afirmaba que CELEBIOS no guarda datos bancarios del
        pagador, mientras /admisiones pide que manden el comprobante de
        transferencia por correo. Un aviso que niega un tratamiento que si
        ocurre es peor que uno incompleto. Art. 8 parr. 3 LFPDPPP: los datos
        financieros exigen consentimiento expreso."""
        texto = self._texto()
        self.assertNotIn(
            "CELEBIOS no almacena números de tarjeta ni datos bancarios de la persona que paga",
            texto)
        self.assertRegex(texto, r"(?i)comprobante")
        self.assertRegex(texto, r"(?i)datos financieros")

    def test_el_aula_enlaza_el_aviso_donde_recaba(self):
        """El unico formulario del sitio que recaba datos personales es el que
        no mostraba el aviso. /aula esta en robots Disallow y ninguna pagina
        publica la enlaza: el alumno llega por liga directa y nunca pasaba por
        el aviso. Art. 17 fr. II LFPDPPP: a disposicion EN EL MOMENTO de la
        recabacion, no en otra pagina."""
        aula = (build.RAIZ / "aula" / "index.html").read_text(encoding="utf-8")
        self.assertIn("/aviso-de-privacidad", aula)


class TestGA4AtadoAlAviso(unittest.TestCase):
    """Encender GA4 es exportar una variable en Vercel: nadie toca codigo y
    ningun test se cae. gtag.js pone cookies _ga. El encendido queda atado a
    que el aviso las declare."""

    def test_ga4_sin_clausula_de_cookies_revienta(self):
        aviso = build.SRC / "aviso-de-privacidad.html"
        original = aviso.read_text(encoding="utf-8")
        sin_cookies = re.sub(r"(?i)cookies?", "galletas", original)
        try:
            aviso.write_text(sin_cookies, encoding="utf-8")
            with self.assertRaises(SystemExit):
                build.inyectar_ga4("<head></head>", "G-ABC123XYZ")
        finally:
            aviso.write_text(original, encoding="utf-8")

    def test_con_clausula_inyecta(self):
        self.assertIn("G-ABC123XYZ",
                      build.inyectar_ga4("<head></head>", "G-ABC123XYZ"))


class TestProgramasHistoricosNoSeAnuncianComoInéditos(unittest.TestCase):
    """El sitio se contradecia a si mismo: curso-nutricion decia "la primera
    edicion" mientras galeria.html publica el cartel de la 1a generacion de
    2019 y egresados.html lista 2019 y 2021. Quien compara las dos paginas
    concluye que una miente, y ambas estan publicadas."""

    def test_ninguna_pagina_de_curso_promete_una_primera_edicion(self):
        for pagina in sorted(build.SRC.glob("curso-*.html")):
            with self.subTest(pagina=pagina.name):
                texto = pagina.read_text(encoding="utf-8")
                self.assertNotRegex(texto, r"(?i)primera\s+edici[óo]n")


class TestPaginasHuerfanas(unittest.TestCase):
    """Una pagina huerfana esta en el sitemap pero no en el sitio: Google la
    ve sin contexto y un visitante no puede llegar navegando. /egresados nacio
    asi, siendo el destino de 234 reglas de redirect."""

    def _paginas(self, tmp, archivos):
        rutas = {}
        for nombre, (ruta, cuerpo) in archivos.items():
            f = Path(tmp) / nombre
            f.write_text(cuerpo, encoding="utf-8")
            rutas[f] = ruta
        return rutas

    def test_detecta_la_pagina_sin_enlaces_entrantes(self):
        # a y b se enlazan mutuamente para que la unica huerfana sea "sola";
        # si no, el par tambien saldria y el test no probaria lo que dice.
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(tmp, {
                "a.html": ("/a", '<a href="b.html">b</a><a href="c.html">c</a>'),
                "b.html": ("/b", '<a href="a.html">a</a><a href="c.html">c</a>'),
                "c.html": ("/c", '<a href="a.html">a</a><a href="b.html">b</a>'),
                "sola.html": ("/sola", "<p>nadie me enlaza</p>"),
            })
            self.assertEqual(build.buscar_paginas_huerfanas(paginas), ["/sola"])

    def test_un_solo_enlace_entrante_ya_es_senal(self):
        """El umbral es 2 y no 1 a proposito: nueve fichas de /recursos
        colgaban de un UNICO enlace, todas desde la misma pagina. Estaban a un
        enlace de ser huerfanas, y con n == 0 la guarda no decia nada."""
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(tmp, {
                "a.html": ("/a", '<a href="b.html">b</a>'),
                "b.html": ("/b", '<a href="a.html">a</a>'),
            })
            self.assertEqual(build.buscar_paginas_huerfanas(paginas), ["/a", "/b"])

    def test_dos_enlaces_entrantes_bastan(self):
        with tempfile.TemporaryDirectory() as tmp:
            paginas = self._paginas(tmp, {
                "a.html": ("/a", '<a href="b.html">b</a><a href="c.html">c</a>'),
                "b.html": ("/b", '<a href="a.html">a</a><a href="c.html">c</a>'),
                "c.html": ("/c", '<a href="a.html">a</a><a href="b.html">b</a>'),
            })
            self.assertEqual(build.buscar_paginas_huerfanas(paginas), [])

    def test_enlazarse_a_si_misma_no_cuenta(self):
        with tempfile.TemporaryDirectory() as tmp:
            enlaces = '<a href="a.html">a</a><a href="b.html">b</a><a href="d.html">d</a>'
            paginas = self._paginas(tmp, {
                "a.html": ("/a", enlaces),
                "b.html": ("/b", enlaces),
                "d.html": ("/d", enlaces),
                # c enlaza a las demas pero a ella solo se enlaza a si misma
                "c.html": ("/c", '<a href="c.html#seccion">yo misma</a>' + enlaces),
            })
            self.assertEqual(build.buscar_paginas_huerfanas(paginas), ["/c"])

    def test_el_sitio_real_no_tiene_huerfanas(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        self.assertEqual(build.buscar_paginas_huerfanas(paginas), [])


class TestScrollMarginEnDestinosDeAncla(unittest.TestCase):
    """`header.site` es position:sticky y mide 69px. Sin scroll-margin-top, un
    301 con fragmento deja su destino tapado bajo el header: medido en vivo,
    la tarjeta quedaba en top:0 con 69px comidos, justo el "Lam. NN" y el pill
    de estado. Afecta a las reglas activas con fragmento, que son la mayoria."""

    REGLA = re.compile(r"scroll-margin-top\s*:\s*[^;}]+")

    def test_toda_pagina_destino_de_un_ancla_declara_scroll_margin(self):
        paginas = {f: build.ruta_canonica(f.read_text(encoding="utf-8"))
                   for f in sorted(build.SRC.glob("*.html"))}
        paginas = {f: r for f, r in paginas.items() if r}
        with build.REDIRECTS_CSV.open(encoding="utf-8") as f:
            activas, _ = build.convertir_redirects_bulk(list(csv.DictReader(f)), set(paginas.values()))

        destinos = {r["destination"].split("#", 1)[0] or "/"
                    for r in activas if "#" in r["destination"]}
        self.assertTrue(destinos, "no hay reglas con fragmento, el test no prueba nada")

        sin_regla = sorted(
            f.name for f, ruta in paginas.items()
            if ruta in destinos and not self.REGLA.search(f.read_text(encoding="utf-8"))
        )
        self.assertEqual(sin_regla, [], f"aterrizarian bajo el header: {sin_regla}")

    def test_el_margen_cubre_el_header(self):
        # 5.5rem = 88px contra un header de 69px. Si alguien lo baja de 69,
        # el ancla vuelve a quedar tapada y el test deja de protegerte.
        texto = (build.SRC / "catalogo.html").read_text(encoding="utf-8")
        m = re.search(r"scroll-margin-top\s*:\s*([\d.]+)rem", texto)
        self.assertIsNotNone(m, "se esperaba el margen declarado en rem")
        self.assertGreaterEqual(float(m.group(1)) * 16, 69)


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


def _publicadas():
    """Las fuentes que SI se publican: las maquetas de redesign-v2 no llevan
    canonical y build.py las salta."""
    return [p for p in sorted(build.SRC.glob("*.html"))
            if "canonical" in p.read_text(encoding="utf-8")]


class TestAccesibilidadEstructural(unittest.TestCase):
    """Cuatro defectos que un lector de pantalla sufre y un navegador no
    reporta. Se congelan aqui porque son invisibles en revision visual: nadie
    los ve al mirar la pagina, y vuelven en la primera reescritura."""

    def test_toda_pagina_tiene_salto_al_contenido_con_destino_real(self):
        """Sin esto, quien navega con teclado recorre los 8 enlaces de la nav
        en CADA pagina antes de llegar al contenido."""
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                texto = p.read_text(encoding="utf-8")
                self.assertRegex(texto, r'<a class="saltar" href="#top">')
                self.assertIn('id="top"', texto)

    def test_ningun_salto_de_nivel_en_los_encabezados(self):
        """h2 -> h4 le dice al lector de pantalla que falta una seccion
        intermedia que no existe. Las 8 paginas de programa saltaban."""
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                niveles = [int(m.group(1))
                           for m in re.finditer(r"<h([1-6])\b", p.read_text(encoding="utf-8"))]
                saltos = [(a, b) for a, b in zip(niveles, niveles[1:]) if b > a + 1]
                self.assertEqual(saltos, [], f"saltos de jerarquia: {saltos}")

    def test_aria_current_page_solo_en_el_enlace_a_la_propia_pagina(self):
        """23 de 33 paginas marcaban "estas aqui" en un enlace que apunta a
        OTRA pagina (la de la seccion). El valor correcto para el padre de
        seccion es "true", no "page"."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            for m in re.finditer(r'<a[^>]*aria-current="page"[^>]*>', texto):
                href = re.search(r'href="([^"]+)"', m.group(0))
                href = href.group(1) if href else ""
                propia = href == p.name or (
                    p.name == "lamina-viva.html" and href in ("index.html", "./"))
                with self.subTest(pagina=p.name, href=href):
                    self.assertTrue(propia, f'aria-current="page" apunta a {href}')

    def test_todo_svg_con_aria_label_declara_role_img(self):
        """Un <svg> sin role no tiene rol implicito que acepte nombre
        accesible: la etiqueta puede no anunciarse nunca."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            sin_rol = [m.group(0)[:60]
                       for m in re.finditer(r'<svg\b[^>]*\baria-label="[^"]*"[^>]*>', texto)
                       if "role=" not in m.group(0)]
            with self.subTest(pagina=p.name):
                self.assertEqual(sin_rol, [])


class TestPagina404(unittest.TestCase):
    """El 404 recibe TODO enlace muerto de Wix y Kajabi que las 368 reglas no
    cubran. Era HTML pelon con un solo enlace."""

    def test_es_navegable_y_ofrece_salidas(self):
        html = build.generar_404()
        self.assertIn('name="viewport"', html)
        self.assertIn('content="noindex"', html)
        for salida in ('href="/cursos"', 'href="/"', 'href="/contacto"'):
            with self.subTest(salida=salida):
                self.assertIn(salida, html)

    def test_el_anillo_de_foco_es_visible_sobre_su_fondo(self):
        """No comparte el sistema de diseno, asi que su anillo se declara
        aparte y nadie lo revisa cuando cambian los tokens."""
        html = build.generar_404()
        self.assertRegex(html, r":focus-visible\{[^}]*outline:\s*3px solid")


class TestVerificar(unittest.TestCase):
    """verificar() es el UNICO gate de enlaces rotos y no tenia ni un test.
    Ademas eximia 99 enlaces por comparar `valor in canon` contra el tag
    canonical entero: '/cur' era substring de
    '<link rel="canonical" href=".../cursos">' y salia del scan."""

    def _sitio(self, tmp, cuerpo, canonical="/cursos"):
        salida = Path(tmp) / "site"
        salida.mkdir()
        (salida / "cursos.html").write_text(
            f'<link rel="canonical" href="{build.DOMINIO}{canonical}">{cuerpo}',
            encoding="utf-8")
        return salida

    def test_enlace_a_ruta_inexistente_revienta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(tmp, '<a href="/no-existe">x</a>')
            with self.assertRaises(SystemExit):
                build.verificar(salida)

    def test_substring_del_canonical_ya_no_exime(self):
        """El caso exacto que colaba: '/cur' no existe en el sitio, pero SI es
        substring del tag canonical. Antes pasaba limpio."""
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(tmp, '<a href="/cur">x</a>')
            with self.assertRaises(SystemExit):
                build.verificar(salida)

    def test_ruta_relativa_revienta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(tmp, '<a href="relativo.html">x</a>')
            with self.assertRaises(SystemExit):
                build.verificar(salida)

    def test_content_apuntando_a_un_asset_inexistente_revienta(self):
        """Asi viajo a produccion un og:image a un JPG que no existe: el regex
        solo miraba href y src."""
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(
                tmp, f'<meta property="og:image" content="{build.DOMINIO}/brand/no-existe.jpg">')
            with self.assertRaises(SystemExit):
                build.verificar(salida)

    def test_content_en_el_host_de_revision_tambien_se_comprueba(self):
        """En preview la tarjeta social apunta a celebios.vercel.app. Si solo
        se comprobara el dominio definitivo, el chequeo no correria nunca."""
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(
                tmp,
                f'<meta property="og:image" content="{build.HOST_REVISION}/brand/no-existe.jpg">')
            with self.assertRaises(SystemExit):
                build.verificar(salida)

    def test_content_que_no_es_una_url_no_estorba(self):
        """La mayoria de los content= son texto: descripciones, anchos, temas."""
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(
                tmp, '<meta name="description" content="Cursos de fauna"><meta name="theme-color" content="#14294F">')
            build.verificar(salida)

    def test_javascript_roto_revienta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(tmp, '<script type="module">const a = ;</script>')
            with self.assertRaises(SystemExit):
                build.verificar(salida)

    def test_sitio_sano_no_revienta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = self._sitio(
                tmp, '<a href="/cursos">x</a><a href="mailto:a@b.c">y</a><a href="#top">z</a>')
            build.verificar(salida)


class TestReescribir(unittest.TestCase):
    """reescribir() toca CADA href/src de las 33 paginas y hace malabares
    sacando y devolviendo el canonical con un centinela. Si su regex deja de
    casar, lo unico que lo atrapa es verificar()."""

    MAPA = {"curso-gatos.html": "/curso-lenguaje-felino"}

    def test_conserva_el_ancla(self):
        salida = build.reescribir('<a href="curso-gatos.html#temario">x</a>', self.MAPA)
        self.assertIn('href="/curso-lenguaje-felino#temario"', salida)

    def test_conserva_el_query(self):
        salida = build.reescribir('<a href="curso-gatos.html?ref=ig">x</a>', self.MAPA)
        self.assertIn('href="/curso-lenguaje-felino?ref=ig"', salida)

    def test_el_canonical_conserva_el_dominio_absoluto(self):
        """Es lo unico que NO debe volverse raiz-relativo: un canonical
        relativo le dice a Google que la pagina canonica es otra."""
        html = f'<link rel="canonical" href="{build.DOMINIO}/curso-lenguaje-felino"><a href="{build.DOMINIO}/cursos">x</a>'
        salida = build.reescribir(html, self.MAPA)
        self.assertIn(f'canonical" href="{build.DOMINIO}/curso-lenguaje-felino"', salida)
        self.assertIn('<a href="/cursos">', salida)

    def test_los_assets_relativos_se_vuelven_absolutos(self):
        salida = build.reescribir('<img src="brand/logo-white.webp">', {})
        self.assertIn('src="/brand/logo-white.webp"', salida)


class TestAula(unittest.TestCase):
    """Es la unica pagina con datos de alumno en memoria (el access_token de
    Supabase) y la unica que importa codigo de un tercero."""

    def _paginas(self):
        return sorted((build.RAIZ / "aula").glob("*.html"))

    def test_supabase_js_va_con_version_fija(self):
        """Con el rango @2, cualquier release del canal 2.x se ejecuta en la
        pagina que tiene el token del alumno, sin que nadie lo revise."""
        for p in self._paginas():
            with self.subTest(pagina=p.name):
                texto = p.read_text(encoding="utf-8")
                if "supabase-js" not in texto:
                    continue
                self.assertRegex(texto, r"supabase-js@\d+\.\d+\.\d+")
                self.assertNotRegex(texto, r"supabase-js@\d+['\"]")

    def test_no_pide_nada_a_un_tercer_origen_salvo_el_modulo(self):
        """El aviso declara que las tipografias salen del propio dominio. El
        aula seguia pidiendolas a Google, o sea mandandole la IP del ALUMNO."""
        for p in self._paginas():
            with self.subTest(pagina=p.name):
                texto = p.read_text(encoding="utf-8")
                self.assertNotIn("fonts.googleapis.com", texto)
                self.assertNotIn("fonts.gstatic.com", texto)
                self.assertIn("@font-face", texto)

    def test_la_csp_del_aula_se_publica_y_cubre_su_supabase(self):
        cabeceras = json.loads(build.generar_vercel_json())["headers"]
        aula = [h for h in cabeceras if h["source"].startswith("/aula")]
        self.assertTrue(aula, "sin cabeceras para /aula")
        for h in aula:
            with self.subTest(source=h["source"]):
                csp = next(x["value"] for x in h["headers"]
                           if x["key"] == "Content-Security-Policy")
                self.assertIn(build.SUPABASE_AULA, csp)
                self.assertIn("frame-ancestors 'none'", csp)

    def test_la_csp_apunta_al_mismo_proyecto_que_el_codigo(self):
        """Si alguien migra de proyecto de Supabase y no toca la CSP, el aula
        deja de conectar. Mejor que se caiga aqui."""
        codigo = (build.RAIZ / "aula" / "index.html").read_text(encoding="utf-8")
        self.assertIn(build.SUPABASE_AULA, codigo)


class TestPieLegal(unittest.TestCase):
    """Las tres paginas mas visitadas -- portada, /cursos y /diplomado -- eran
    justo las que no enlazaban el aviso, porque su pie es otro. Y /aula no
    tenia NI UN enlace entrante desde las 33 publicadas: el alumno solo llegaba
    por liga directa de correo."""

    def test_toda_pagina_enlaza_el_aviso_y_el_aula(self):
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                texto = p.read_text(encoding="utf-8")
                self.assertIn("aviso-de-privacidad.html", texto)
                self.assertIn('href="/aula"', texto)

    def test_sin_restos_de_la_pasada_sin_acentos(self):
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                self.assertNotRegex(p.read_text(encoding="utf-8"),
                                    r"16 an(?:ios|os|hos) en LATAM")


class TestElSitioNoSeContradice(unittest.TestCase):
    """Cada uno de estos empezo siendo dos paginas del mismo sitio afirmando
    cosas distintas. Quien compara concluye que una miente, y ambas estan
    publicadas."""

    def test_los_anios_de_trayectoria_son_los_mismos_en_todas(self):
        """La galeria decia "Quince" en su titular y "16 anios" en su propio
        pie, 265 lineas mas abajo."""
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                self.assertNotRegex(p.read_text(encoding="utf-8"),
                                    r"(?i)quince a[nñ]")

    def test_la_cifra_de_areas_coincide_con_las_tarjetas_del_catalogo(self):
        """Decia "14 areas" en una pagina donde el lector puede contar 18
        tarjetas. La cifra venia de "~14 temas" de la fuente, que es un conteo
        historico aproximado, publicado como cifra exacta de la oferta."""
        catalogo = build.SRC / "catalogo.html"
        texto = catalogo.read_text(encoding="utf-8")
        cuerpo = texto[texto.rfind("</style>"):]
        tarjetas = len(re.findall(r'<article[^>]*class="[^"]*lamina[^"]*"', cuerpo))
        for p in (catalogo, build.SRC / "lamina-viva.html"):
            with self.subTest(pagina=p.name):
                for n in re.findall(r"(\d+)\s+[áa]reas", p.read_text(encoding="utf-8")):
                    self.assertEqual(int(n), tarjetas)

    def test_el_curso_de_reptiles_tiene_un_solo_nombre(self):
        """"Medicina de reptiles" y "bienestar de reptiles" no son el mismo
        producto ante un MVZ: uno promete contenido clinico y el otro no."""
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                self.assertNotRegex(p.read_text(encoding="utf-8"),
                                    r"(?i)Manejo y Medicina de Reptiles")

    def test_los_meses_sin_intereses_se_niegan_igual_en_todas(self):
        """/admisiones y /nosotros lo negaban de plano; el catalogo lo dejaba
        "por confirmar". Es una condicion de pago, no un matiz."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            if "meses sin intereses" not in texto:
                continue
            with self.subTest(pagina=p.name):
                self.assertNotRegex(texto, r"meses sin intereses[^.]*por confirmar")

    def test_ninguna_figura_rotula_como_foto_un_dibujo(self):
        """Un pie decia "[ FOTO DOCUMENTAL ] · Panthera onca · Esc. 1:1" sobre
        un dibujo de linea en SVG, en la pagina del programa insignia."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            for fig in re.findall(r"<figure[^>]*>.*?</figure>", texto, re.S):
                cap = re.search(r"<figcaption[^>]*>([^<]+)", fig)
                if not cap or "FOTO" not in cap.group(1).upper():
                    continue
                with self.subTest(pagina=p.name, pie=cap.group(1)[:40]):
                    self.assertIn("<img", fig, "se anuncia foto y no hay ninguna")

    def test_el_aria_label_de_la_lamina_no_contradice_al_alt_de_su_imagen(self):
        """Tres etiquetas quedaron describiendo al animal ANTERIOR tras
        cambiar dibujos por fotos: la portada se presentaba como "especimen
        jaguar" sobre una lechuza."""
        especies = ("jaguar", "felino", "guacamaya", "lechuza", "grulla", "loro",
                    "cocodrilo", "rapaz", "quelonio", "tortuga")
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            for fig in re.findall(r'<figure[^>]*aria-label="([^"]+)"[^>]*>(.*?)</figure>',
                                  texto, re.S):
                etiqueta, cuerpo = fig
                alt = re.search(r'<img[^>]*alt="([^"]*)"', cuerpo)
                if not alt:
                    continue
                en_etiqueta = {e for e in especies if e in etiqueta.lower()}
                en_alt = {e for e in especies if e in alt.group(1).lower()}
                if not en_etiqueta or not en_alt:
                    continue
                with self.subTest(pagina=p.name, etiqueta=etiqueta[:40]):
                    self.assertTrue(en_etiqueta & en_alt,
                                    f"aria-label dice {en_etiqueta} y el alt {en_alt}")


class TestArticulosDeRecursos(unittest.TestCase):
    def test_todos_declaran_fecha_de_publicacion(self):
        """Sin datePublished, un articulo de 2026 puede salir en resultados sin
        fecha o con la que el rastreador se invente."""
        articulos = sorted(build.SRC.glob("recurso-*.html"))
        self.assertEqual(len(articulos), 16)
        for p in articulos:
            with self.subTest(articulo=p.name):
                texto = p.read_text(encoding="utf-8")
                self.assertRegex(texto, r'"datePublished":\s*"\d{4}-\d{2}-\d{2}"')
                self.assertRegex(texto, r'"dateModified":\s*"\d{4}-\d{2}-\d{2}"')

    def test_el_json_ld_no_deja_referencias_colgadas(self):
        """isPartOf apuntaba a la organizacion en vez de al sitio. Al
        reapuntarlo, el nodo WebSite tenia que existir en la MISMA pagina o la
        referencia queda al aire."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                     texto, re.S):
                datos = json.loads(bloque)
                nodos = datos.get("@graph", [datos]) if isinstance(datos, dict) else datos
                ids = {n.get("@id") for n in nodos if isinstance(n, dict)}
                for n in nodos:
                    if isinstance(n, dict) and isinstance(n.get("isPartOf"), dict):
                        with self.subTest(pagina=p.name):
                            self.assertIn(n["isPartOf"].get("@id"), ids)


class TestDegradadoSinBase(unittest.TestCase):
    """Un degradado con TODAS las paradas traslucidas no es un fondo: es un
    tinte sobre lo que haya debajo. `.cta-card` -- la unica llamada a la accion
    de los 16 articulos -- lo usaba con alfas de 12 a 30% dentro de una
    `section.surface-light`, y su titular en --hueso quedaba a 1.00:1. Texto
    blanco sobre papel blanco: invisible, medido en navegador."""

    def test_el_sitio_publicado_no_tiene_ninguno(self):
        self.assertEqual(build.buscar_degradado_sin_base(_publicadas()), [])

    def test_detecta_el_degradado_traslucido(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.html"
            f.write_text(
                ".cta-card{ background:linear-gradient(155deg, rgba(47,168,201,.16),"
                " rgba(11,43,46,.3)); color:var(--hueso); }", encoding="utf-8")
            self.assertTrue(build.buscar_degradado_sin_base([f]))

    def test_con_base_opaca_no_dispara(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.html"
            f.write_text(
                ".cta-card{ background:linear-gradient(155deg, rgba(47,168,201,.16),"
                " rgba(11,43,46,.3)), var(--charca); color:var(--hueso); }", encoding="utf-8")
            self.assertEqual(build.buscar_degradado_sin_base([f]), [])

    def test_no_se_conforma_con_el_parentesis_de_la_base(self):
        """La primera version usaba rfind(')') y se quedaba con el cierre de
        var(--charca), asi que daba por buena cualquier declaracion. Este es
        el caso que la desenmascara: parentesis anidados y SIN base."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.html"
            f.write_text(
                ".cta-card{ background:linear-gradient(155deg, rgba(47,168,201,.16),"
                " rgba(122,87,151,.12) 70%, rgba(11,43,46,.3)); }", encoding="utf-8")
            self.assertTrue(build.buscar_degradado_sin_base([f]))


class TestLaminaTipografica(unittest.TestCase):
    """Los 18 visores del catalogo llevaban dibujos de linea a mano, y seis
    eran el MISMO contorno de cuadrupedo con otra cabeza, rotulados Tapirus,
    Mazama, Leopardus, Puma, Panthera y Didelphis. Ante MVZ eso no se lee como
    estilo: se lee como material sin terminar."""

    def test_no_quedan_dibujos_de_especimen(self):
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                self.assertNotIn('class="specimen"', p.read_text(encoding="utf-8"))

    def test_cada_marco_lleva_su_rotulo(self):
        """Los dos contenedores que antes tenian dibujo: la tarjeta (.visor) y
        la placa ancla (.ap-rotulo). Ninguno puede quedarse sin etiqueta."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            cuerpo = texto[texto.rfind("</style>"):]
            marcos = (len(re.findall(r'<div class="visor(?: [^"]*)?"', cuerpo))
                      + len(re.findall(r'<div class="art ap-rotulo"', cuerpo)))
            rotulos = len(re.findall(r'<span class="esp-taxon">', cuerpo))
            with self.subTest(pagina=p.name):
                self.assertEqual(marcos, rotulos)

    def test_el_rotulo_no_se_repite_debajo_del_marco(self):
        """El kicker de debajo se mudo DENTRO del marco. Si vuelve a aparecer
        pegado al visor, es que alguien lo duplico."""
        for p in _publicadas():
            texto = p.read_text(encoding="utf-8")
            pegados = re.findall(
                r'<span class="esp-taxon">([^<]+)</span>.{0,400}?'
                r'<span class="kicker-sci[^"]*"[^>]*>([^<]*)</span>', texto, re.S)
            for taxon, kicker in pegados:
                with self.subTest(pagina=p.name, taxon=taxon):
                    self.assertNotIn(taxon.split()[0], kicker)


class TestNavegacionGlobal(unittest.TestCase):
    def test_el_cta_del_header_lleva_al_unico_programa_vendible(self):
        """Apuntaba al MISMO destino que el enlace "Cursos" de al lado -- el
        hueco mas visible de las 33 paginas, duplicado -- mientras el unico
        programa "available" del contrato no estaba en la nav global."""
        vendible = [p for p in build.cargar_programas() if p["status"] == "available"]
        self.assertEqual(len(vendible), 1)
        for p in _publicadas():
            with self.subTest(pagina=p.name):
                cta = re.search(r'<a class="nav-cta" href="([^"]+)"', p.read_text(encoding="utf-8"))
                self.assertIsNotNone(cta)
                self.assertNotEqual(cta.group(1), "catalogo.html")


if __name__ == "__main__":
    unittest.main()
