#!/usr/bin/env python3
"""Convierte quiz-gatos.json en el seed SQL del curso de gatos.

Genera SQL idempotente: identifica todo por slug de curso y numero de leccion
o pregunta, sin manejar UUIDs, para poder correrlo varias veces sin duplicar.

Uso:  python quiz_to_sql.py   ->  ../supabase/seed/0002_curso_gatos.sql
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FUENTE = AQUI / "quiz-gatos.json"
DESTINO = AQUI.parent / "supabase" / "seed" / "0002_curso_gatos.sql"

SLUG = "curso-lenguaje-felino"
TITULO = "Lenguaje y Comunicación de los Gatos"
PRECIO_MXN = 1400  # confirmado en el sitio; no inventar si cambia


def sql(texto):
    """Literal de Postgres: la unica escapada que hace falta es la comilla."""
    return "'" + texto.replace("'", "''") + "'"


def generar(datos):
    out = [
        "-- Generado por contenido/quiz_to_sql.py — no editar a mano.",
        f"-- Fuente: {datos['fuente']}",
        "",
        "insert into cursos (slug, titulo, precio_mxn, publicado)",
        f"values ({sql(SLUG)}, {sql(TITULO)}, {PRECIO_MXN}, false)",
        "on conflict (slug) do nothing;",
        "",
    ]
    for m in datos["modulos"]:
        n = m["modulo"]
        # El titulo real de cada modulo esta solo en Kajabi. "Modulo N" es
        # marcador honesto, no dato inventado: se reemplaza al migrar.
        out += [
            f"-- ---- Modulo {n}",
            "insert into lecciones (curso_id, numero, titulo)",
            f"select id, {n}, {sql(f'Módulo {n}')} from cursos where slug = {sql(SLUG)}",
            "on conflict (curso_id, numero) do nothing;",
            "",
        ]
        for p in m["preguntas"]:
            out += [
                "insert into preguntas (leccion_id, numero, enunciado, opciones)",
                f"select l.id, {p['n']}, {sql(p['enunciado'])}, "
                f"{sql(json.dumps(p['opciones'], ensure_ascii=False))}::jsonb",
                "from lecciones l join cursos c on c.id = l.curso_id",
                f"where c.slug = {sql(SLUG)} and l.numero = {n}",
                "on conflict (leccion_id, numero) do nothing;",
                "",
                "insert into respuestas_correctas (pregunta_id, correcta)",
                f"select p.id, {sql(p['correcta'])} from preguntas p",
                "join lecciones l on l.id = p.leccion_id",
                "join cursos c on c.id = l.curso_id",
                f"where c.slug = {sql(SLUG)} and l.numero = {n} and p.numero = {p['n']}",
                "on conflict (pregunta_id) do update set correcta = excluded.correcta;",
                "",
            ]
    return "\n".join(out)


def verificar(texto, datos):
    """Que el SQL emitido tenga exactamente lo que trae el JSON."""
    esperadas = sum(len(m["preguntas"]) for m in datos["modulos"])
    cuenta = {
        "lecciones": texto.count("insert into lecciones"),
        "preguntas": texto.count("insert into preguntas"),
        "respuestas": texto.count("insert into respuestas_correctas"),
    }
    assert cuenta["lecciones"] == len(datos["modulos"]), cuenta
    assert cuenta["preguntas"] == esperadas, cuenta
    assert cuenta["respuestas"] == esperadas, cuenta
    # Una comilla suelta rompe todo el archivo: no debe quedar ninguna impar.
    for i, linea in enumerate(texto.splitlines(), 1):
        assert linea.count("'") % 2 == 0, f"comilla sin cerrar en la linea {i}: {linea}"
    return cuenta


if __name__ == "__main__":
    datos = json.loads(FUENTE.read_text(encoding="utf-8"))
    texto = generar(datos)
    cuenta = verificar(texto, datos)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(texto, encoding="utf-8")
    print(f"ok: {cuenta['lecciones']} lecciones, {cuenta['preguntas']} preguntas, "
          f"{cuenta['respuestas']} respuestas -> {DESTINO.name}")
