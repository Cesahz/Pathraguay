"""pruebas de integridad del grafo narrativo que se publica con el juego.

son las que atajan errores de autoria de contenido: un salto a un nodo que no
existe, un efecto mal tipeado o una rama que deja al jugador dando vueltas
sin poder terminar nunca.
"""

import json

import pytest

from pathraguay.dominio import clases, motor

OPCIONES = ("opcion_izq", "opcion_der")


def _destinos(carta):
    return [carta[opcion]["siguiente_id"] for opcion in OPCIONES]


class TestFormaDeLosNodos:
    def test_cada_nodo_tiene_los_campos_esperados(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            assert set(carta) == {"texto", "img", "opcion_izq", "opcion_der"}, identificador

    def test_cada_nodo_tiene_texto(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            assert carta["texto"].strip(), "%s sin texto" % identificador

    def test_cada_opcion_tiene_los_campos_esperados(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            for opcion in OPCIONES:
                assert set(carta[opcion]) == {"texto", "siguiente_id", "efectos"}, \
                    "%s.%s" % (identificador, opcion)

    def test_cada_opcion_tiene_texto_y_destino(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            for opcion in OPCIONES:
                assert carta[opcion]["texto"].strip(), "%s.%s sin texto" % (identificador, opcion)
                assert carta[opcion]["siguiente_id"].strip(), \
                    "%s.%s sin destino" % (identificador, opcion)

    def test_las_dos_opciones_de_un_nodo_se_distinguen(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            izquierda = carta["opcion_izq"]["texto"].strip()
            derecha = carta["opcion_der"]["texto"].strip()
            assert izquierda != derecha, "%s ofrece dos opciones con el mismo texto" % identificador


class TestEfectos:
    def test_los_efectos_declaran_todas_las_stats(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            for opcion in OPCIONES:
                efectos = carta[opcion]["efectos"]
                assert set(efectos) == set(clases.STATS_BASE), \
                    "%s.%s con stats faltantes o de mas" % (identificador, opcion)

    def test_los_efectos_son_enteros(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            for opcion in OPCIONES:
                for stat, valor in carta[opcion]["efectos"].items():
                    assert isinstance(valor, int) and not isinstance(valor, bool), \
                        "%s.%s.%s no es entero" % (identificador, opcion, stat)

    def test_ningun_efecto_supera_el_rango_util(self, cartas_reales):
        """un efecto mayor a 100 sobre una stat acotada delata un error de tipeo."""
        for identificador, carta in cartas_reales.items():
            for opcion in OPCIONES:
                for stat, valor in carta[opcion]["efectos"].items():
                    if stat == "dinero":
                        continue
                    assert abs(valor) <= 100, \
                        "%s.%s.%s vale %d" % (identificador, opcion, stat, valor)


class TestTopologia:
    def test_el_nodo_inicial_existe(self, cartas_reales):
        assert clases.CARTA_INICIAL in cartas_reales

    def test_todo_nodo_es_alcanzable_desde_el_inicio(self, cartas_reales):
        visitados = set()
        pendientes = [clases.CARTA_INICIAL]
        while pendientes:
            actual = pendientes.pop()
            if actual in visitados or actual not in cartas_reales:
                continue
            visitados.add(actual)
            pendientes.extend(_destinos(cartas_reales[actual]))

        huerfanos = set(cartas_reales) - visitados
        assert not huerfanos, "nodos inalcanzables desde el inicio: %s" % sorted(huerfanos)

    def test_ningun_nodo_salta_a_si_mismo(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            assert identificador not in _destinos(carta), "%s salta a si mismo" % identificador

    def test_los_destinos_colgados_cierran_la_partida(self, cartas_reales):
        """un destino fuera del grafo es un final valido, no un error."""
        colgados = {
            destino
            for carta in cartas_reales.values()
            for destino in _destinos(carta)
            if destino not in cartas_reales
        }

        for destino in colgados:
            estado = dict(clases.crear_estado_inicial(), carta_actual_id=destino)
            resultado = motor.obtener_estado_actual(estado, cartas_reales)
            assert resultado["fin"] is True, "%s no cierra la partida" % destino

    def test_desde_todo_nodo_se_puede_llegar_a_un_final(self, cartas_reales):
        """ninguna rama debe dejar al jugador girando en un ciclo sin salida."""
        #un nodo termina si alguna opcion sale del grafo o lleva a otro que termina
        terminan = set()
        cambio = True
        while cambio:
            cambio = False
            for identificador, carta in cartas_reales.items():
                if identificador in terminan:
                    continue
                for destino in _destinos(carta):
                    if destino not in cartas_reales or destino in terminan:
                        terminan.add(identificador)
                        cambio = True
                        break

        atrapados = set(cartas_reales) - terminan
        assert not atrapados, "nodos sin salida posible: %s" % sorted(atrapados)


class TestArchivoDeCartas:
    def test_ningun_objeto_tiene_claves_duplicadas(self, texto_cartas_reales):
        """json.load se queda con el ultimo duplicado y esconde el error.

        aplica tanto a los identificadores de nodo como a los campos de cada
        carta: dos "opcion_izq" en el mismo nodo perderian una en silencio.
        """
        problemas = []

        def registrar(pares):
            claves = [clave for clave, _ in pares]
            repetidas = sorted({clave for clave in claves if claves.count(clave) > 1})
            if repetidas:
                problemas.append(repetidas)
            return dict(pares)

        json.loads(texto_cartas_reales, object_pairs_hook=registrar)

        assert not problemas, "claves duplicadas en el archivo: %s" % problemas

    def test_el_archivo_es_json_valido_en_utf8(self, texto_cartas_reales):
        assert isinstance(json.loads(texto_cartas_reales), dict)
