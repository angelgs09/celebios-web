"""Pruebas del inventario SEO de migracion (Wix + Kajabi -> sitio nuevo).

Cubre: canonicalizacion de URLs, mapeos semanticos (incluye el curso vivo
"gatos" vs diplomados historicos, y las paginas de egresados que deben
preservar valor via /egresados en vez de 404), 404 solo para basura real del
editor, destinos de un solo salto contra la arquitectura FINAL planeada
(no el sitio actual), columnas del CSV, deteccion de duplicados, el parseo
de sitemap-index/urlset y los reintentos ante 429 -- todo con red simulada,
sin depender de que Wix/Kajabi respondan durante `python -m unittest`.

El conteo exacto del snapshot en vivo (371 Wix + 15 Kajabi) se verifica dos
veces: aqui, contra los CSV ya comiteados (TestCommittedCsvContract, sin
red); y en vivo por `main()` en scripts/sync_migration_inventory.py cada vez
que se corre el script (revienta si el conteo no cuadra).
"""
import csv
import io
import unittest
from pathlib import Path
from unittest import mock

import requests

from scripts.sync_migration_inventory import (
    CSV_FIELDS,
    DESTINOS_BASE_VALIDOS,
    build_inventory_rows,
    classify_source,
    fetch_sitemap_urls,
    normalize_source_url,
    write_csv,
)

RAIZ = Path(__file__).resolve().parent.parent
MIGRACION = RAIZ / "migracion"


class _RespuestaFalsa:
    """Simula un requests.Response: status_code, headers, .text y raise_for_status()."""

    def __init__(self, texto="", status_code=200, headers=None):
        self.text = texto
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{self.status_code} error", response=self
            )


class TestNormalizeSourceUrl(unittest.TestCase):
    def test_quita_www_y_normaliza_a_minusculas(self):
        self.assertEqual(
            normalize_source_url("https://WWW.celebios.com/Nosotros"),
            normalize_source_url("https://celebios.com/nosotros"),
        )

    def test_ignora_slash_final(self):
        self.assertEqual(
            normalize_source_url("https://www.celebios.com/cursos/"),
            normalize_source_url("https://www.celebios.com/cursos"),
        )

    def test_ignora_query_y_fragmento(self):
        self.assertEqual(
            normalize_source_url("https://www.celebios.com/nosotros?utm=x#seccion"),
            normalize_source_url("https://www.celebios.com/nosotros"),
        )

    def test_ignora_esquema_http_vs_https(self):
        self.assertEqual(
            normalize_source_url("http://www.celebios.com/cursos"),
            normalize_source_url("https://www.celebios.com/cursos"),
        )

    def test_raiz_normaliza_distinto_de_una_ruta(self):
        self.assertNotEqual(
            normalize_source_url("https://www.celebios.com/"),
            normalize_source_url("https://www.celebios.com/cursos"),
        )

    def test_decodifica_percent_encoding(self):
        self.assertEqual(
            normalize_source_url("https://www.celebios.com/gen%2Dtest"),
            normalize_source_url("https://www.celebios.com/gen-test"),
        )


class TestClassifySourceSemantics(unittest.TestCase):
    def test_home_wix(self):
        categoria, tema, destino = classify_source("", "celebios.com")
        self.assertEqual((categoria, tema, destino), ("home", "home", "/"))

    def test_home_kajabi(self):
        categoria, tema, destino = classify_source("/", "celebios.online")
        self.assertEqual((categoria, tema, destino), ("home", "home", "/"))

    def test_curso_gatos_es_el_unico_disponible(self):
        categoria, _, destino = classify_source(
            "/lenguaje-y-comunicacion-de-los-gatos", "celebios.online"
        )
        self.assertEqual(categoria, "curso_disponible")
        self.assertEqual(destino, "/curso-lenguaje-felino")

    def test_diplomado_rehabilitacion_es_programa_historico_con_ancla(self):
        categoria, tema, destino = classify_source("/rehabilitacion-fauna-2024", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(tema, "rehabilitacion")
        self.assertEqual(destino, "/cursos#historico-rehabilitacion")

    def test_diplomado_felidos_no_se_confunde_con_el_curso_de_gatos(self):
        # "Felidos" fue un diplomado sobre felidos silvestres/domesticos,
        # distinto del curso vivo "Lenguaje y Comunicacion de los Gatos".
        categoria, tema, destino = classify_source("/felidos-torres-barraza", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertNotEqual(destino, "/curso-lenguaje-felino")
        self.assertEqual(destino, "/cursos#historico-felidos")

    def test_curso_historico_va_a_ancla_de_archivo_no_a_pagina_profunda(self):
        # Las paginas profundas de curso (/cursos/ortopedia-aves) existen
        # hoy pero Task 3 las reemplaza por un archivo historico en
        # /cursos: el redirect debe apuntar ahi directo, no a una pagina
        # que el rediseno va a borrar.
        categoria, tema, destino = classify_source("/ortopedia-aves", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(tema, "ortopedia-aves")
        self.assertEqual(destino, "/cursos#historico-ortopedia-aves")

    def test_aula_virtual_preserva_el_aula(self):
        _, _, destino = classify_source("/aula-virtual", "celebios.com")
        self.assertEqual(destino, "/aula")

    def test_generacion_con_anio_va_a_egresados_con_cohorte(self):
        categoria, tema, destino = classify_source("/gen2016fauna", "celebios.com")
        self.assertEqual(categoria, "egresado")
        self.assertEqual(tema, "cohorte-2016")
        self.assertEqual(destino, "/egresados#cohorte-2016")

    def test_cohortes_de_sig_con_anio_no_caen_en_404(self):
        # \bsig\b no matcheaba "sig2018": el limite de palabra no ocurre
        # entre "g" y un digito. Hallado en auditoria semantica.
        for ruta in ("/sig2018", "/sig2019", "/sig2020", "/copia-de-sig2020"):
            with self.subTest(ruta=ruta):
                categoria, tema, destino = classify_source(ruta, "celebios.com")
                self.assertEqual(categoria, "curso_historico")
                self.assertEqual(tema, "sig-cartografia")
                self.assertEqual(destino, "/cursos#historico-sig-cartografia")

    def test_formato_ingreso_es_alias_de_admision(self):
        categoria, _, destino = classify_source("/formato-ingreso", "celebios.com")
        self.assertEqual(destino, "/admisiones")

    def test_inscripcion_generica_es_alias_de_admision(self):
        categoria, _, destino = classify_source("/inscripcion", "celebios.com")
        self.assertEqual(destino, "/admisiones")

    def test_convocatoria_es_alias_de_admision(self):
        _, _, destino = classify_source("/convoc-anestesia-fauna", "celebios.com")
        self.assertEqual(destino, "/admisiones")

    def test_programacion_no_es_pagina_de_egresado(self):
        categoria, _, destino = classify_source("/programacion", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(destino, "/cursos")

    def test_nosotros_es_alias_de_historia(self):
        _, _, destino = classify_source("/nosotros", "celebios.com")
        self.assertEqual(destino, "/historia")

    def test_contacto_es_alias_de_contacto(self):
        _, _, destino = classify_source("/contacto", "celebios.com")
        self.assertEqual(destino, "/contacto")

    def test_contact_kajabi_no_se_degrada_a_nosotros(self):
        # Bug encontrado en revision: /contact caia en /nosotros pese a que
        # /contacto SI existe en la arquitectura final.
        _, _, destino = classify_source("/contact", "celebios.online")
        self.assertEqual(destino, "/contacto")

    def test_docente_es_alias_de_docentes(self):
        _, _, destino = classify_source("/nuestros-docentes", "celebios.com")
        self.assertEqual(destino, "/docentes")

    def test_practicas_de_campo_es_alias_propio(self):
        _, _, destino = classify_source("/practica-de-campo-2020", "celebios.com")
        self.assertEqual(destino, "/practicas-de-campo")

    def test_host_desconocido_revienta(self):
        with self.assertRaises(ValueError):
            classify_source("/algo", "otro-dominio.com")

    def test_aviso_de_privacidad_preserva_su_destino(self):
        categoria, _, destino = classify_source("/aviso-de-privacidad", "celebios.com")
        self.assertEqual(categoria, "institucional")
        self.assertEqual(destino, "/aviso-de-privacidad")


class TestClassifySourceEgresados(unittest.TestCase):
    """El fallback residual y el prefijo egresados*/gen<anio> preservan
    valor via /egresados en vez de descartar la pagina: son trafico real de
    exalumnos, no basura del editor."""

    def test_pagina_de_egresado_individual_va_a_egresados(self):
        categoria, _, destino = classify_source("/lopez-hernandez", "celebios.com")
        self.assertEqual(categoria, "egresado")
        self.assertEqual(destino, "/egresados")

    def test_egresado_con_anio_de_cohorte_reconocible(self):
        categoria, tema, destino = classify_source("/vazquez-santiago-2016", "celebios.com")
        self.assertEqual(categoria, "egresado")
        self.assertEqual(tema, "cohorte-2016")
        self.assertEqual(destino, "/egresados#cohorte-2016")

    def test_egresado_con_anio_prefijado_por_digito_extra(self):
        # "ortega-castelazo-12016": el "1" es un artefacto de slug, el anio
        # real (2016) sigue siendo detectable como subcadena.
        categoria, tema, destino = classify_source("/ortega-castelazo-12016", "celebios.com")
        self.assertEqual(tema, "cohorte-2016")
        self.assertEqual(destino, "/egresados#cohorte-2016")

    def test_prefijo_egresados_bare_preserva_egresados(self):
        # El caso mas obvio: la URL que se llama /egresados debe preservar
        # /egresados, no caer en el catalogo.
        categoria, tema, destino = classify_source("/egresados", "celebios.com")
        self.assertEqual(categoria, "egresado")
        self.assertEqual(tema, "")
        self.assertEqual(destino, "/egresados")

    def test_prefijo_egresados_con_tema_conocido_sin_anio(self):
        categoria, tema, destino = classify_source("/egresadosbioetica", "celebios.com")
        self.assertEqual(categoria, "egresado")
        self.assertEqual(tema, "bioetica")
        self.assertEqual(destino, "/egresados#tema-bioetica")

    def test_prefijo_egresados_con_anio_prioriza_cohorte_sobre_tema(self):
        categoria, tema, destino = classify_source("/egresadosfauna2020", "celebios.com")
        self.assertEqual(categoria, "egresado")
        self.assertEqual(tema, "cohorte-2020")
        self.assertEqual(destino, "/egresados#cohorte-2020")

    def test_nombre_concatenado_sin_curso_va_a_egresados(self):
        categoria, _, _ = classify_source("/alejandrajosefinacrespogarza", "celebios.com")
        self.assertEqual(categoria, "egresado")

    def test_no_deja_topic_or_cohort_con_nombre_propio(self):
        # No se recolecta contenido personal: el tema nunca es el nombre de
        # la persona egresada, solo "" o un anio/tema inferido.
        _, tema, _ = classify_source("/lopez-hernandez", "celebios.com")
        self.assertEqual(tema, "")
        _, tema, _ = classify_source("/vazquez-santiago-2016", "celebios.com")
        self.assertNotIn("vazquez", tema)
        self.assertNotIn("santiago", tema)


class TestClassifySource404Junk(unittest.TestCase):
    def test_paginas_de_constructor_wix_son_404(self):
        for ruta in ("/blank", "/copia-de-copia-de-copia-de-copia-de-18", "/keeper", "/galeria-1"):
            with self.subTest(ruta=ruta):
                categoria, _, destino = classify_source(ruta, "celebios.com")
                self.assertEqual(categoria, "sin_equivalente")
                self.assertEqual(destino, "")


class TestOneHopDestinations(unittest.TestCase):
    MUESTRA_WIX = [
        "", "/cursos", "/nosotros", "/contacto", "/aviso-de-privacidad",
        "/aula-virtual", "/rehabilitacion-fauna-2024", "/rehabilitacion-fauna-2025",
        "/felidos", "/felidos-torres-barraza", "/ortopedia-aves",
        "/ortopedia-tirado-perez", "/anestesia-fauna-2020", "/nutricionfauna",
        "/nutricion2019", "/manejo-conductual-fauna", "/manejo-conductual-2022",
        "/reptiles", "/felidos-domesticos-silvestres-2020",
        "/medicina-interna", "/medicina-preventiva", "/bioetica", "/sig2018",
        "/cartografia-web", "/manejo-datos", "/impacto-ambiental",
        "/egresados", "/egresadosfauna2020", "/inscripcion",
        "/inscripcion-rehabilitacion", "/gen2016fauna", "/lopez-hernandez",
        "/blank", "/formato-ingreso", "/nuestros-docentes",
        "/practica-de-campo-2020",
    ]
    MUESTRA_KAJABI = [
        "/", "/home", "/cursos", "/store", "/nosotros", "/about", "/contact",
        "/test", "/nutricionfauna", "/lenguaje-y-comunicacion-de-los-gatos",
        "/curso-lenguaje-felino", "/diplomado-rescate-rehabilitacion-fauna",
        "/curso-anestesia",
    ]

    def test_todos_los_destinos_son_bases_validas_o_vacios(self):
        for ruta in self.MUESTRA_WIX:
            _, _, destino = classify_source(ruta, "celebios.com")
            base = destino.split("#", 1)[0]
            with self.subTest(host="wix", ruta=ruta):
                self.assertIn(base, DESTINOS_BASE_VALIDOS | {""})
        for ruta in self.MUESTRA_KAJABI:
            _, _, destino = classify_source(ruta, "celebios.online")
            base = destino.split("#", 1)[0]
            with self.subTest(host="kajabi", ruta=ruta):
                self.assertIn(base, DESTINOS_BASE_VALIDOS | {""})

    def test_solo_home_puede_destinar_a_la_raiz(self):
        for ruta in self.MUESTRA_WIX:
            categoria, _, destino = classify_source(ruta, "celebios.com")
            if destino == "/":
                with self.subTest(ruta=ruta):
                    self.assertEqual(categoria, "home")


class TestCsvFields(unittest.TestCase):
    def test_fila_trae_todas_las_columnas_y_metricas_vacias(self):
        filas = build_inventory_rows(["https://www.celebios.com/nosotros"])
        self.assertEqual(len(filas), 1)
        fila = filas[0]
        self.assertEqual(set(fila.keys()), set(CSV_FIELDS))
        for campo in ("clicks", "impressions", "position", "backlinks"):
            self.assertEqual(fila[campo], "")

    def test_status_code_301_o_404(self):
        filas = build_inventory_rows([
            "https://www.celebios.com/nosotros",
            "https://www.celebios.com/blank",
        ])
        codigos = {f["source_url"]: f["status_code"] for f in filas}
        self.assertEqual(codigos["https://www.celebios.com/nosotros"], 301)
        self.assertEqual(codigos["https://www.celebios.com/blank"], 404)

    def test_write_csv_produce_encabezado_exacto(self):
        filas = build_inventory_rows(["https://www.celebios.com/cursos"])
        buffer = io.StringIO()
        write_csv(buffer, filas)
        lector = csv.reader(io.StringIO(buffer.getvalue()))
        encabezado = next(lector)
        self.assertEqual(encabezado, CSV_FIELDS)

    def test_aviso_de_privacidad_sin_revision_manual(self):
        filas = build_inventory_rows(["https://www.celebios.com/aviso-de-privacidad"])
        self.assertEqual(filas[0]["manual_review"], "false")
        self.assertEqual(filas[0]["status_code"], 301)
        self.assertEqual(filas[0]["destination_path"], "/aviso-de-privacidad")

    def test_egresado_sin_evidencia_queda_marcado_para_revision(self):
        # Confianza baja (sin anio ni tema inferible) => revision manual,
        # a diferencia de la basura del editor (confianza alta, curada).
        filas = build_inventory_rows(["https://www.celebios.com/lopez-hernandez"])
        self.assertEqual(filas[0]["confidence"], "baja")
        self.assertEqual(filas[0]["manual_review"], "true")

    def test_basura_de_editor_no_requiere_revision_manual(self):
        filas = build_inventory_rows(["https://www.celebios.com/blank"])
        self.assertEqual(filas[0]["confidence"], "alta")
        self.assertEqual(filas[0]["manual_review"], "false")


class TestDuplicateDetection(unittest.TestCase):
    def test_variantes_de_la_misma_url_se_colapsan_a_una_fila(self):
        filas = build_inventory_rows([
            "https://www.celebios.com/cursos",
            "https://www.celebios.com/cursos/",
            "https://celebios.com/CURSOS",
        ])
        self.assertEqual(len(filas), 1)

    def test_urls_distintas_no_se_colapsan(self):
        filas = build_inventory_rows([
            "https://www.celebios.com/cursos",
            "https://www.celebios.com/nosotros",
        ])
        self.assertEqual(len(filas), 2)


class TestFetchSitemapUrls(unittest.TestCase):
    """Red simulada: verifica el parseo, no depende de Wix/Kajabi en vivo."""

    def test_sigue_sitemap_index_hasta_las_urls_reales(self):
        indice = (
            '<?xml version="1.0"?>'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<sitemap><loc>https://example.com/pages-sitemap.xml</loc></sitemap>"
            "</sitemapindex>"
        )
        hijo = (
            '<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://example.com/a</loc></url>"
            "<url><loc>https://example.com/b</loc></url>"
            "</urlset>"
        )
        cuerpos = {
            "https://example.com/sitemap.xml": indice,
            "https://example.com/pages-sitemap.xml": hijo,
        }

        def get_falso(url, headers=None, timeout=None):
            return _RespuestaFalsa(cuerpos[url])

        with mock.patch("scripts.sync_migration_inventory.requests.get", side_effect=get_falso):
            urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        self.assertEqual(urls, ["https://example.com/a", "https://example.com/b"])

    def test_urlset_plano_no_necesita_seguir_indice(self):
        plano = (
            '<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://example.com/x</loc></url>"
            "</urlset>"
        )

        with mock.patch(
            "scripts.sync_migration_inventory.requests.get",
            return_value=_RespuestaFalsa(plano),
        ):
            urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        self.assertEqual(urls, ["https://example.com/x"])

    def test_reintenta_ante_429_y_despues_funciona(self):
        plano = (
            '<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://example.com/x</loc></url>"
            "</urlset>"
        )
        respuestas = [
            _RespuestaFalsa("", status_code=429),
            _RespuestaFalsa(plano),
        ]

        def get_falso(url, headers=None, timeout=None):
            return respuestas.pop(0)

        with mock.patch("scripts.sync_migration_inventory.requests.get", side_effect=get_falso), \
             mock.patch("scripts.sync_migration_inventory.time.sleep") as duerme:
            urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        self.assertEqual(urls, ["https://example.com/x"])
        duerme.assert_called_once()

    def test_retry_after_en_formato_fecha_http_no_revienta(self):
        # RFC 9110 permite Retry-After como fecha HTTP, no solo segundos.
        # int(Retry-After) reventaba con ValueError en ese caso.
        plano = (
            '<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://example.com/x</loc></url>"
            "</urlset>"
        )
        respuestas = [
            _RespuestaFalsa("", status_code=429, headers={"Retry-After": "Wed, 01 Jan 2030 00:00:00 GMT"}),
            _RespuestaFalsa(plano),
        ]

        def get_falso(url, headers=None, timeout=None):
            return respuestas.pop(0)

        with mock.patch("scripts.sync_migration_inventory.requests.get", side_effect=get_falso), \
             mock.patch("scripts.sync_migration_inventory.time.sleep") as duerme:
            urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        self.assertEqual(urls, ["https://example.com/x"])
        duerme.assert_called_once()

    def test_429_persistente_revienta_sin_reintentar_para_siempre(self):
        with mock.patch(
            "scripts.sync_migration_inventory.requests.get",
            return_value=_RespuestaFalsa("", status_code=429),
        ), mock.patch("scripts.sync_migration_inventory.time.sleep"):
            with self.assertRaises(requests.exceptions.HTTPError):
                fetch_sitemap_urls("https://example.com/sitemap.xml")


class TestCommittedCsvContract(unittest.TestCase):
    """Lee los tres CSV ya comiteados (no una muestra curada) y fija el
    contrato completo: conteos exactos, encabezado, sin duplicados, sin
    destinos fuera de la arquitectura final, sin regresiones en privacidad
    ni contacto, y confianza/revision apropiadas para los 404 deliberados."""

    @classmethod
    def setUpClass(cls):
        with (MIGRACION / "urls-wix.csv").open(encoding="utf-8") as f:
            cls.filas_wix = list(csv.DictReader(f))
        with (MIGRACION / "urls-kajabi.csv").open(encoding="utf-8") as f:
            cls.filas_kajabi = list(csv.DictReader(f))
        with (MIGRACION / "redirects.csv").open(encoding="utf-8") as f:
            cls.filas_redirects = list(csv.DictReader(f))

    def test_conteo_exacto_wix(self):
        self.assertEqual(len(self.filas_wix), 371)

    def test_conteo_exacto_kajabi(self):
        self.assertEqual(len(self.filas_kajabi), 15)

    def test_conteo_exacto_redirects(self):
        self.assertEqual(len(self.filas_redirects), 386)

    def test_encabezado_exacto_en_los_tres_csv(self):
        for filas in (self.filas_wix, self.filas_kajabi, self.filas_redirects):
            self.assertEqual(list(filas[0].keys()), CSV_FIELDS)

    def test_sin_urls_duplicadas(self):
        claves = [normalize_source_url(f["source_url"]) for f in self.filas_redirects]
        self.assertEqual(len(claves), len(set(claves)))

    def test_ninguna_base_de_destino_es_invalida(self):
        for fila in self.filas_redirects:
            destino = fila["destination_path"]
            if not destino:
                continue
            base = destino.split("#", 1)[0]
            with self.subTest(source_url=fila["source_url"]):
                self.assertIn(base, DESTINOS_BASE_VALIDOS)

    def test_solo_alias_reales_de_home_van_a_la_raiz(self):
        for fila in self.filas_redirects:
            if fila["destination_path"] == "/":
                with self.subTest(source_url=fila["source_url"]):
                    self.assertEqual(fila["category"], "home")

    def test_aviso_de_privacidad_sin_regresion(self):
        filas = [f for f in self.filas_redirects if f["source_url"].rstrip("/").endswith("aviso-de-privacidad")]
        self.assertEqual(len(filas), 1)
        fila = filas[0]
        self.assertEqual(fila["destination_path"], "/aviso-de-privacidad")
        self.assertEqual(fila["status_code"], "301")
        self.assertEqual(fila["manual_review"], "false")

    def test_contacto_sin_regresion(self):
        filas = [
            f for f in self.filas_redirects
            if f["source_url"].rstrip("/").endswith(("/contacto", "/contact"))
        ]
        self.assertTrue(filas)
        for fila in filas:
            with self.subTest(source_url=fila["source_url"]):
                self.assertEqual(fila["destination_path"], "/contacto")

    def test_404_deliberados_tienen_confianza_y_revision_apropiadas(self):
        filas_404 = [f for f in self.filas_redirects if f["status_code"] == "404"]
        self.assertTrue(filas_404)
        for fila in filas_404:
            with self.subTest(source_url=fila["source_url"]):
                self.assertEqual(fila["confidence"], "alta")
                self.assertEqual(fila["manual_review"], "false")

    def test_ningun_topic_or_cohort_de_egresado_expone_nombre_propio(self):
        temas_conocidos = {
            "", "gatos", "rehabilitacion", "anestesia", "conductual", "nutricion",
            "ortopedia-aves", "reptiles", "primeros-auxilios", "felidos",
            "medicina-interna", "medicina-preventiva", "bioetica",
            "imagenologia-caballos", "imagenologia", "sig-cartografia",
            "manejo-datos", "impacto-ambiental", "diagnostico-terapeutica",
        }
        for fila in self.filas_redirects:
            if fila["category"] != "egresado":
                continue
            tema = fila["topic_or_cohort"]
            with self.subTest(source_url=fila["source_url"]):
                es_cohorte = tema.startswith("cohorte-") and tema[len("cohorte-"):].isdigit()
                self.assertTrue(es_cohorte or tema in temas_conocidos)


if __name__ == "__main__":
    unittest.main()
