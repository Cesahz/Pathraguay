"""fixtures compartidas por la suite.

las pruebas de reglas usan grafos sinteticos para no atarse a la narrativa
concreta, y las de integridad usan el grafo real de data/cartas.json.
"""

import pytest

from app import RAIZ
from pathraguay.datos.repositorio_cartas import cargar_cartas
from pathraguay.web.servidor import crear_app

RUTA_CARTAS = RAIZ / "data" / "cartas.json"

#efectos neutros, para que cada prueba declare solo lo que le importa
SIN_EFECTOS = {"salud": 0, "social": 0, "intelecto": 0, "laboral": 0, "dinero": 0}


def efectos(**cambios):
    """construir un bloque de efectos partiendo de todo en cero."""
    valores = dict(SIN_EFECTOS)
    valores.update(cambios)
    return valores


def nodo(siguiente_izq="fin", siguiente_der="fin", efectos_izq=None, efectos_der=None):
    """construir un nodo del grafo con la forma que espera el motor."""
    return {
        "texto": "situacion de prueba",
        "img": "/static/img/predeterminado.png",
        "opcion_izq": {
            "texto": "opcion izquierda",
            "siguiente_id": siguiente_izq,
            "efectos": efectos_izq if efectos_izq is not None else dict(SIN_EFECTOS),
        },
        "opcion_der": {
            "texto": "opcion derecha",
            "siguiente_id": siguiente_der,
            "efectos": efectos_der if efectos_der is not None else dict(SIN_EFECTOS),
        },
    }


@pytest.fixture
def estado():
    """estado de partida neutro, con margen para subir y bajar cada stat."""
    return {
        "salud": 50,
        "social": 50,
        "intelecto": 50,
        "laboral": 50,
        "dinero": 1000,
        "carta_actual_id": "inicio",
    }


@pytest.fixture
def grafo():
    """grafo sintetico de dos nodos con una salida fuera del grafo."""
    return {
        "inicio": nodo(siguiente_izq="segundo", siguiente_der="fuera_del_grafo"),
        "segundo": nodo(siguiente_izq="inicio", siguiente_der="fuera_del_grafo"),
    }


@pytest.fixture(scope="session")
def cartas_reales():
    """grafo narrativo real que se publica con el juego."""
    return cargar_cartas(RUTA_CARTAS)


@pytest.fixture(scope="session")
def texto_cartas_reales():
    """contenido crudo de cartas.json, para comprobaciones de formato."""
    return RUTA_CARTAS.read_text(encoding="utf-8")


@pytest.fixture
def cliente():
    """cliente http sobre una aplicacion recien construida.

    el estado de partida vive en el closure de crear_app, asi que armar una
    aplicacion por prueba garantiza que ninguna herede la partida de otra.
    """
    aplicacion = crear_app(
        ruta_cartas=RUTA_CARTAS,
        carpeta_static=RAIZ / "static",
        carpeta_templates=RAIZ / "templates",
    )
    aplicacion.config.update(TESTING=True)
    return aplicacion.test_client()
