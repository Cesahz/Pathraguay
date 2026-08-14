"""acceso al archivo que define el grafo narrativo de cartas."""

import json


def cargar_cartas(ruta):
    """leer el grafo completo de cartas desde disco.

    el grafo se lee una sola vez al levantar el servidor y queda en memoria
    durante toda la vida del proceso.
    """
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)
