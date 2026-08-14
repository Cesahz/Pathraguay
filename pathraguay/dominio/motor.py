"""reglas de resolucion de turno sobre el grafo de cartas.

capa interna del proyecto: no conoce flask, ni el disco, ni el formato de
transporte. opera sobre dos diccionarios que recibe por parametro, el estado
de la partida y el grafo de cartas ya cargado.
"""

#todas las stats quedan acotadas al rango 0-100 salvo el dinero, que es libre
LIMITE_MINIMO = 0
LIMITE_MAXIMO = 100
STAT_SIN_LIMITE = "dinero"

#textos de cierre que viajan al cliente. se mantienen literales porque son
#contenido del juego, no mensajes internos
MENSAJE_GRAFO_VACIO = "Sobreviviste al MVP."
MENSAJE_FIN_DE_RAMA = "Lograste sobrevivir esta etapa."
MENSAJE_DERROTA_SALUD = "GAME OVER: colapso por burnout clínico."
MENSAJE_DERROTA_DINERO = "GAME OVER: bancarrota. el sistema te devoró."


def _clonar_carta(cartas, carta_id):
    """devolver una copia de la carta con su id embebido.

    se clona para que el cliente no pueda mutar el grafo en memoria, que vive
    durante toda la vida del proceso.
    """
    carta = cartas[carta_id].copy()
    carta["id"] = carta_id
    return carta


def obtener_estado_actual(estado, cartas):
    """describir la situacion actual sin avanzar el turno."""
    #fallback vacio para el caso de estado sin inicializar
    carta_id = estado.get("carta_actual_id", "")

    if carta_id in cartas:
        return {"stats": estado, "carta": _clonar_carta(cartas, carta_id), "fin": False}

    #id fuera del grafo: se resuelve como fin de recorrido
    return {"stats": estado, "carta": None, "fin": True, "mensaje": MENSAJE_GRAFO_VACIO}


def _aplicar_efectos(estado, efectos):
    """sumar los efectos de la opcion al estado y acotar las stats."""
    for stat, valor in efectos.items():
        estado[stat] += valor
        if stat != STAT_SIN_LIMITE:
            estado[stat] = max(LIMITE_MINIMO, min(LIMITE_MAXIMO, estado[stat]))


def _detectar_derrota(estado):
    """devolver la stat que termina la partida, o None si sigue en juego."""
    if estado["salud"] <= 0:
        return "salud", MENSAJE_DERROTA_SALUD
    if estado["dinero"] < 0:
        return "dinero", MENSAJE_DERROTA_DINERO
    return None, None


def procesar_turno(estado, cartas, eleccion):
    """aplicar una decision y avanzar al siguiente nodo del grafo."""
    carta = cartas[estado["carta_actual_id"]]
    opcion = carta["opcion_" + eleccion]
    efectos = opcion["efectos"]

    _aplicar_efectos(estado, efectos)

    #evaluar la derrota antes de avanzar de nodo
    stat_fatal, mensaje = _detectar_derrota(estado)
    if stat_fatal is not None:
        return {
            "stats": estado,
            "fin": True,
            "mensaje": mensaje,
            "stat_fatal": stat_fatal,
            "efectos": efectos,
        }

    siguiente_id = opcion.get("siguiente_id")
    estado["carta_actual_id"] = siguiente_id

    if siguiente_id in cartas:
        return {
            "stats": estado,
            "carta": _clonar_carta(cartas, siguiente_id),
            "fin": False,
            "efectos": efectos,
        }

    #el destino no existe como nodo: rama terminada
    return {"stats": estado, "fin": True, "mensaje": MENSAJE_FIN_DE_RAMA, "efectos": efectos}
