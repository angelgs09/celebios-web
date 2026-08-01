#!/usr/bin/env python3
"""Convierte quiz-gatos.txt (extraido del Quiz 1-11.docx de Drive) a JSON.

El .docx trae los examenes del curso "Lenguaje y Comunicacion de los Gatos":
11 modulos x 6 preguntas de opcion multiple. Este script los deja listos para
cargarlos a la base de datos sin transcribir nada a mano.

Uso:  python parse_quiz.py
"""
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FUENTE = AQUI / "quiz-gatos.txt"
DESTINO = AQUI / "quiz-gatos.json"

# "Módulo 3." y tambien "Múdulo 1." — el original trae ese dedazo en el primero.
MODULO = re.compile(r"^M[óú]dulo\s+(\d+)\.\s*$", re.M)
PREGUNTA = re.compile(r"^(\d+)\\?\.\s+(.*)$")
OPCION = re.compile(r"^([A-D])\)\s+(.*)$")
CORRECTA = re.compile(r"^Respuesta correcta:\s*([A-D])\s*$")


def parsear(texto):
    modulos = []
    # split con captura: [antes, "1", cuerpo, "2", cuerpo, ...]
    partes = MODULO.split(texto)
    for numero, cuerpo in zip(partes[1::2], partes[2::2]):
        modulos.append({"modulo": int(numero), "preguntas": parsear_preguntas(cuerpo)})
    return modulos


def parsear_preguntas(cuerpo):
    preguntas, actual = [], None
    for linea in (l.strip() for l in cuerpo.splitlines()):
        if not linea:
            continue
        if m := CORRECTA.match(linea):
            if actual is None:
                raise ValueError(f"respuesta sin pregunta: {linea}")
            actual["correcta"] = m.group(1)
            preguntas.append(actual)
            actual = None
        elif m := OPCION.match(linea):
            if actual is None:
                raise ValueError(f"opcion sin pregunta: {linea}")
            actual["opciones"][m.group(1)] = m.group(2)
        elif m := PREGUNTA.match(linea):
            actual = {"n": int(m.group(1)), "enunciado": m.group(2), "opciones": {}}
        elif actual is not None and not actual["opciones"]:
            # El enunciado a veces sigue en la linea de abajo.
            actual["enunciado"] += " " + linea
    if actual is not None:
        raise ValueError(f"pregunta {actual['n']} se quedo sin respuesta correcta")
    return preguntas


def verificar(modulos):
    """Si el .docx cambia y algo se rompe, que reviente aqui y no en produccion."""
    assert len(modulos) == 11, f"esperaba 11 modulos, hay {len(modulos)}"
    assert [m["modulo"] for m in modulos] == list(range(1, 12)), "modulos fuera de orden"
    total = 0
    for m in modulos:
        assert len(m["preguntas"]) == 6, f"modulo {m['modulo']}: {len(m['preguntas'])} preguntas"
        for p in m["preguntas"]:
            ubic = f"modulo {m['modulo']} pregunta {p['n']}"
            assert sorted(p["opciones"]) == list("ABCD"), f"{ubic}: opciones {sorted(p['opciones'])}"
            assert p["correcta"] in p["opciones"], f"{ubic}: correcta invalida"
            assert p["enunciado"].endswith("?"), f"{ubic}: enunciado truncado -> {p['enunciado']!r}"
            assert all(v.strip() for v in p["opciones"].values()), f"{ubic}: opcion vacia"
            total += 1
    assert total == 66, f"esperaba 66 preguntas, hay {total}"
    return total


if __name__ == "__main__":
    modulos = parsear(FUENTE.read_text(encoding="utf-8"))
    total = verificar(modulos)
    DESTINO.write_text(
        json.dumps(
            {
                "curso": "Lenguaje y Comunicacion de los Gatos",
                "fuente": "Quiz 1-11.docx (Drive, carpeta Modulos)",
                "modulos": modulos,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"ok: 11 modulos, {total} preguntas -> {DESTINO.name}")
