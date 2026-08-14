"""catalogo de clases jugables y construccion del estado inicial de partida."""

#cada clase es un preset de arranque con un balance distinto de stats.
#agregar una clase nueva solo requiere sumar una entrada aca.
CLASES_DISPONIBLES = {
    "Heredero": {
        "descripcion": "hijo de empresario. dinero de sobra, poca resistencia al estres.",
        "stats": {"salud": 60, "social": 80, "intelecto": 40, "laboral": 30, "dinero": 5000000}
    },
    "Pobre pero Honrado": {
        "descripcion": "acostumbrado a la presion. poco dinero, alta resistencia.",
        "stats": {"salud": 90, "social": 40, "intelecto": 50, "laboral": 70, "dinero": 100000}
    },
    "Inteligente asocial": {
        "descripcion": "inteligencia pura, cero habilidades sociales.",
        "stats": {"salud": 50, "social": 10, "intelecto": 95, "laboral": 20, "dinero": 250000}
    }
}

#clase de respaldo cuando el cliente manda una clase inexistente
CLASE_POR_DEFECTO = "Pobre pero Honrado"

#nodo del grafo por el que arranca toda partida
CARTA_INICIAL = "inicio"

#stats numericas que componen el estado de partida
STATS_BASE = ("salud", "social", "intelecto", "laboral", "dinero")


def obtener_clases():
    """devolver el catalogo completo de clases para el cliente."""
    return CLASES_DISPONIBLES


def crear_estado_inicial(nombre_clase=CLASE_POR_DEFECTO):
    """construir el estado de partida a partir del preset elegido."""
    #si la clase no existe, caer a la por defecto por seguridad
    clase = CLASES_DISPONIBLES.get(nombre_clase, CLASES_DISPONIBLES[CLASE_POR_DEFECTO])
    stats = clase["stats"]

    estado = {nombre: stats[nombre] for nombre in STATS_BASE}
    estado["carta_actual_id"] = CARTA_INICIAL
    return estado
