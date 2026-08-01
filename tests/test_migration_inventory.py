"""Pruebas del inventario SEO de migracion (Wix + Kajabi -> sitio nuevo).

Cubre: canonicalizacion de URLs, mapeos semanticos (incluye el curso vivo
"gatos" vs diplomados historicos), 404 de paginas sin equivalente, destinos
de un solo salto, columnas del CSV, deteccion de duplicados, el parseo de
sitemap-index/urlset y los reintentos ante 429 -- todo con red simulada, sin
depender de que Wix/Kajabi respondan durante `python -m unittest`.

El conteo exacto del snapshot en vivo (371 Wix + 15 Kajabi) NO se verifica
aqui: eso es un chequeo de red real y lo hace `main()` en
scripts/sync_migration_inventory.py cada vez que se corre el script (revienta
si el conteo no cuadra). Correr `python scripts/sync_migration_inventory.py`
es el "live audit" explicito.
"""
import csv
import io
import unittest
from unittest import mock

import requests

from scripts.sync_migration_inventory import (
    CSV_FIELDS,
    build_inventory_rows,
    classify_source,
    fetch_sitemap_urls,
    normalize_source_url,
    write_csv,
)


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

# Rutas que hoy existen de verdad en el sitio nuevo (redesign-v2 -> site/).
# Ningun destino del inventario deberia caer fuera de este conjunto: si lo
# hiciera, el redirect apuntaria a una pagina que no existe (dos saltos).
DESTINOS_VIVOS = {
    "/",
    "/cursos",
    "/nosotros",
    "/aula",
    "/curso-lenguaje-felino",
    "/diplomado-rescate-rehabilitacion-fauna",
    "/cursos/anestesia-contencion-fauna",
    "/cursos/manejo-conductual-fauna",
    "/cursos/nutricion-fauna-cautiverio",
    "/cursos/ortopedia-aves",
    "/cursos/manejo-reptiles",
    "/cursos/primeros-auxilios-fauna",
}


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

    def test_diplomado_rehabilitacion_no_es_el_curso_disponible(self):
        categoria, _, destino = classify_source("/rehabilitacion-fauna-2024", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(destino, "/diplomado-rescate-rehabilitacion-fauna")

    def test_diplomado_felidos_no_se_confunde_con_el_curso_de_gatos(self):
        # "Felidos" fue un diplomado sobre felidos silvestres/domesticos,
        # distinto del curso vivo "Lenguaje y Comunicacion de los Gatos".
        categoria, tema, destino = classify_source("/felidos-torres-barraza", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertNotEqual(destino, "/curso-lenguaje-felino")
        self.assertEqual(destino, "/cursos")

    def test_curso_con_pagina_viva_va_directo_a_ella(self):
        categoria, _, destino = classify_source("/ortopedia-aves", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(destino, "/cursos/ortopedia-aves")

    def test_aula_virtual_preserva_el_aula(self):
        _, _, destino = classify_source("/aula-virtual", "celebios.com")
        self.assertEqual(destino, "/aula")

    def test_cohorte_generica_sin_curso_reconocible_va_al_catalogo(self):
        categoria, _, destino = classify_source("/gen2016fauna", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(destino, "/cursos")

    def test_cohortes_de_sig_con_anio_no_caen_en_404(self):
        # \bsig\b no matcheaba "sig2018": el limite de palabra no ocurre
        # entre "g" y un digito. Hallado en auditoria semantica.
        for ruta in ("/sig2018", "/sig2019", "/sig2020", "/copia-de-sig2020"):
            with self.subTest(ruta=ruta):
                categoria, _, destino = classify_source(ruta, "celebios.com")
                self.assertEqual(categoria, "curso_historico")
                self.assertEqual(destino, "/cursos")

    def test_formato_ingreso_sigue_la_misma_regla_que_inscripcion(self):
        categoria, _, destino = classify_source("/formato-ingreso", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(destino, "/cursos")

    def test_programacion_no_es_pagina_de_egresado(self):
        categoria, _, destino = classify_source("/programacion", "celebios.com")
        self.assertEqual(categoria, "curso_historico")
        self.assertEqual(destino, "/cursos")

    def test_host_desconocido_revienta(self):
        with self.assertRaises(ValueError):
            classify_source("/algo", "otro-dominio.com")

    def test_aviso_de_privacidad_no_fabrica_destino(self):
        categoria, _, destino = classify_source("/aviso-de-privacidad", "celebios.com")
        self.assertEqual(categoria, "institucional")
        self.assertEqual(destino, "")


class TestClassifySource404Junk(unittest.TestCase):
    def test_pagina_de_egresado_individual_es_404(self):
        categoria, _, destino = classify_source("/lopez-hernandez", "celebios.com")
        self.assertEqual(categoria, "sin_equivalente")
        self.assertEqual(destino, "")

    def test_nombre_concatenado_sin_curso_es_404(self):
        categoria, _, _ = classify_source("/alejandrajosefinacrespogarza", "celebios.com")
        self.assertEqual(categoria, "sin_equivalente")

    def test_paginas_de_constructor_wix_son_404(self):
        for ruta in ("/blank", "/copia-de-copia-de-copia-de-copia-de-18", "/keeper", "/galeria-1"):
            with self.subTest(ruta=ruta):
                categoria, _, destino = classify_source(ruta, "celebios.com")
                self.assertEqual(categoria, "sin_equivalente")
                self.assertEqual(destino, "")

    def test_no_deja_topic_or_cohort_con_nombre_propio(self):
        # No se recolecta contenido personal: el tema queda vacio, nunca el
        # nombre de la persona egresada.
        _, tema, _ = classify_source("/lopez-hernandez", "celebios.com")
        self.assertEqual(tema, "")


class TestOneHopDestinations(unittest.TestCase):
    MUESTRA_WIX = [
        "", "/cursos", "/nosotros", "/contacto", "/aviso-de-privacidad",
        "/aula-virtual", "/rehabilitacion-fauna-2024", "/rehabilitacion-fauna-2025",
        "/felidos", "/felidos-torres-barraza", "/ortopedia-aves",
        "/ortopedia-tirado-perez", "/anestesia-fauna-2020", "/nutricionfauna",
        "/nutricion2019", "/manejo-conductual-fauna", "/manejo-conductual-2022",
        "/reptiles" if False else "/felidos-domesticos-silvestres-2020",
        "/medicina-interna", "/medicina-preventiva", "/bioetica", "/sig2018",
        "/cartografia-web", "/manejo-datos", "/impacto-ambiental",
        "/egresados", "/egresadosfauna2020", "/inscripcion",
        "/inscripcion-rehabilitacion", "/gen2016fauna", "/lopez-hernandez",
        "/blank",
    ]
    MUESTRA_KAJABI = [
        "/", "/home", "/cursos", "/store", "/nosotros", "/about", "/contact",
        "/test", "/nutricionfauna", "/lenguaje-y-comunicacion-de-los-gatos",
        "/curso-lenguaje-felino", "/diplomado-rescate-rehabilitacion-fauna",
        "/curso-anestesia",
    ]

    def test_todos_los_destinos_son_paginas_vivas_o_vacios(self):
        for ruta in self.MUESTRA_WIX:
            categoria, _, destino = classify_source(ruta, "celebios.com")
            with self.subTest(host="wix", ruta=ruta):
                self.assertIn(destino, DESTINOS_VIVOS | {""})
        for ruta in self.MUESTRA_KAJABI:
            categoria, _, destino = classify_source(ruta, "celebios.online")
            with self.subTest(host="kajabi", ruta=ruta):
                self.assertIn(destino, DESTINOS_VIVOS | {""})

    def test_solo_home_puede_destinar_a_la_raiz(self):
        for ruta in self.MUESTRA_WIX:
            categoria, _, destino = classify_source(ruta, "celebios.com")
            if destino == "/":
                with self.subTest(ruta=ruta):
                    self.assertEqual(categoria, "home")


class TestCsvFields(unittest.TestCase):
    def test_columnas_exactas(self):
        self.assertEqual(
            CSV_FIELDS,
            [
                "source_url", "destination_path", "status_code", "category",
                "topic_or_cohort", "clicks", "impressions", "position",
                "backlinks", "priority", "confidence", "manual_review",
            ],
        )

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
            "https://www.celebios.com/lopez-hernandez",
        ])
        codigos = {f["source_url"]: f["status_code"] for f in filas}
        self.assertEqual(codigos["https://www.celebios.com/nosotros"], 301)
        self.assertEqual(codigos["https://www.celebios.com/lopez-hernandez"], 404)

    def test_write_csv_produce_encabezado_exacto(self):
        filas = build_inventory_rows(["https://www.celebios.com/cursos"])
        buffer = io.StringIO()
        write_csv(buffer, filas)
        lector = csv.reader(io.StringIO(buffer.getvalue()))
        encabezado = next(lector)
        self.assertEqual(encabezado, CSV_FIELDS)

    def test_manual_review_marca_aviso_de_privacidad(self):
        filas = build_inventory_rows(["https://www.celebios.com/aviso-de-privacidad"])
        self.assertEqual(filas[0]["manual_review"], "true")
        self.assertEqual(filas[0]["status_code"], 404)


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

    def test_429_persistente_revienta_sin_reintentar_para_siempre(self):
        with mock.patch(
            "scripts.sync_migration_inventory.requests.get",
            return_value=_RespuestaFalsa("", status_code=429),
        ), mock.patch("scripts.sync_migration_inventory.time.sleep"):
            with self.assertRaises(requests.exceptions.HTTPError):
                fetch_sitemap_urls("https://example.com/sitemap.xml")


if __name__ == "__main__":
    unittest.main()
