"""pruebas de las reglas de resolucion de turno.

se apoyan en grafos sinteticos para fijar el comportamiento del motor con
independencia de la narrativa que se publique.
"""

import copy

import pytest

from conftest import efectos
from pathraguay.dominio import motor

STATS_ACOTADAS = ["salud", "social", "intelecto", "laboral"]


class TestAplicacionDeEfectos:
    def test_sumar_efectos_al_estado(self, estado, grafo):
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(salud=10, social=-20, dinero=500)

        motor.procesar_turno(estado, grafo, "izq")

        assert estado["salud"] == 60
        assert estado["social"] == 30
        assert estado["dinero"] == 1500
        #las stats no mencionadas quedan intactas
        assert estado["intelecto"] == 50
        assert estado["laboral"] == 50

    @pytest.mark.parametrize("stat", STATS_ACOTADAS)
    def test_acotar_al_maximo(self, estado, grafo, stat):
        estado[stat] = 95
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(**{stat: 50})

        motor.procesar_turno(estado, grafo, "izq")

        assert estado[stat] == 100

    @pytest.mark.parametrize("stat", [s for s in STATS_ACOTADAS if s != "salud"])
    def test_acotar_al_minimo(self, estado, grafo, stat):
        estado[stat] = 5
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(**{stat: -50})

        motor.procesar_turno(estado, grafo, "izq")

        assert estado[stat] == 0

    def test_el_dinero_no_se_acota(self, estado, grafo):
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(dinero=5_000_000)

        motor.procesar_turno(estado, grafo, "izq")

        #el dinero queda libre, no lo limita el techo de 100 de las demas
        assert estado["dinero"] == 5_001_000


class TestCondicionesDeDerrota:
    def test_derrota_por_salud_en_cero(self, estado, grafo):
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(salud=-50)

        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert resultado["fin"] is True
        assert resultado["stat_fatal"] == "salud"
        assert resultado["mensaje"] == motor.MENSAJE_DERROTA_SALUD

    def test_derrota_por_dinero_negativo(self, estado, grafo):
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(dinero=-1001)

        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert resultado["fin"] is True
        assert resultado["stat_fatal"] == "dinero"
        assert resultado["mensaje"] == motor.MENSAJE_DERROTA_DINERO

    def test_dinero_exactamente_en_cero_no_es_derrota(self, estado, grafo):
        """el corte es dinero < 0, no <= 0: quedarse sin plata deja seguir."""
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(dinero=-1000)

        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert estado["dinero"] == 0
        assert resultado["fin"] is False

    def test_las_demas_stats_en_cero_no_terminan_la_partida(self, estado, grafo):
        """solo salud y dinero cortan la partida en esta version."""
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(social=-50, intelecto=-50, laboral=-50)

        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert estado["social"] == 0 and estado["intelecto"] == 0 and estado["laboral"] == 0
        assert resultado["fin"] is False

    def test_la_derrota_se_evalua_antes_de_avanzar(self, estado, grafo):
        """al perder, la partida queda parada en el nodo donde se perdio."""
        grafo["inicio"]["opcion_izq"]["efectos"] = efectos(salud=-50)

        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert estado["carta_actual_id"] == "inicio"
        assert "carta" not in resultado

    def test_la_derrota_informa_los_efectos_que_la_causaron(self, estado, grafo):
        golpe = efectos(salud=-50)
        grafo["inicio"]["opcion_izq"]["efectos"] = golpe

        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert resultado["efectos"] == golpe


class TestAvanceEnElGrafo:
    def test_avanzar_al_nodo_indicado(self, estado, grafo):
        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert estado["carta_actual_id"] == "segundo"
        assert resultado["fin"] is False
        assert resultado["carta"]["id"] == "segundo"

    def test_cada_opcion_lleva_a_su_propio_destino(self, estado, grafo):
        derecha = motor.procesar_turno(dict(estado), grafo, "der")
        izquierda = motor.procesar_turno(dict(estado), grafo, "izq")

        assert izquierda["carta"]["id"] == "segundo"
        #la derecha apunta fuera del grafo y cierra la rama
        assert derecha["fin"] is True

    def test_destino_fuera_del_grafo_cierra_la_rama(self, estado, grafo):
        resultado = motor.procesar_turno(estado, grafo, "der")

        assert resultado["fin"] is True
        assert resultado["mensaje"] == motor.MENSAJE_FIN_DE_RAMA
        assert "stat_fatal" not in resultado

    def test_la_carta_devuelta_incluye_su_id(self, estado, grafo):
        resultado = motor.procesar_turno(estado, grafo, "izq")

        assert resultado["carta"]["id"] == "segundo"
        assert resultado["carta"]["texto"] == grafo["segundo"]["texto"]


class TestAislamientoDelGrafo:
    def test_procesar_turno_no_muta_el_grafo(self, estado, grafo):
        original = copy.deepcopy(grafo)

        for _ in range(5):
            resultado = motor.procesar_turno(estado, grafo, "izq")
            if resultado["fin"]:
                break

        assert grafo == original

    def test_mutar_la_carta_devuelta_no_afecta_al_grafo(self, estado, grafo):
        resultado = motor.procesar_turno(estado, grafo, "izq")

        resultado["carta"]["texto"] = "texto pisado por el cliente"

        assert grafo["segundo"]["texto"] == "situacion de prueba"

    def test_obtener_estado_actual_tampoco_muta_el_grafo(self, estado, grafo):
        original = copy.deepcopy(grafo)

        devuelto = motor.obtener_estado_actual(estado, grafo)
        devuelto["carta"]["img"] = "/static/img/pisada.png"

        assert grafo == original


class TestLecturaDeEstado:
    def test_estado_en_un_nodo_valido(self, estado, grafo):
        resultado = motor.obtener_estado_actual(estado, grafo)

        assert resultado["fin"] is False
        assert resultado["carta"]["id"] == "inicio"
        assert resultado["stats"] is estado

    def test_estado_sin_partida_iniciada(self, grafo):
        resultado = motor.obtener_estado_actual({}, grafo)

        assert resultado["fin"] is True
        assert resultado["carta"] is None
        assert resultado["mensaje"] == motor.MENSAJE_GRAFO_VACIO

    def test_estado_apuntando_fuera_del_grafo(self, estado, grafo):
        estado["carta_actual_id"] = "nodo_que_no_existe"

        resultado = motor.obtener_estado_actual(estado, grafo)

        assert resultado["fin"] is True
        assert resultado["carta"] is None


class TestInvariantesSobreRecorridosExhaustivos:
    """recorrer todas las decisiones posibles y exigir invariantes en cada paso."""

    def _recorridos(self, estado_inicial, cartas, profundidad=8):
        pendientes = [(estado_inicial, [])]
        while pendientes:
            estado_actual, camino = pendientes.pop()
            if len(camino) >= profundidad:
                continue
            for eleccion in ("izq", "der"):
                siguiente = copy.deepcopy(estado_actual)
                resultado = motor.procesar_turno(siguiente, cartas, eleccion)
                yield camino + [eleccion], siguiente, resultado
                if not resultado["fin"]:
                    pendientes.append((siguiente, camino + [eleccion]))

    def test_las_stats_acotadas_nunca_salen_del_rango(self, cartas_reales):
        estado_inicial = {
            "salud": 90, "social": 40, "intelecto": 50,
            "laboral": 70, "dinero": 100000, "carta_actual_id": "inicio",
        }

        for camino, estado_final, _ in self._recorridos(estado_inicial, cartas_reales):
            for stat in STATS_ACOTADAS:
                assert 0 <= estado_final[stat] <= 100, "%s fuera de rango en %s" % (stat, camino)

    def test_toda_carta_devuelta_pertenece_al_grafo(self, cartas_reales):
        estado_inicial = {
            "salud": 90, "social": 40, "intelecto": 50,
            "laboral": 70, "dinero": 100000, "carta_actual_id": "inicio",
        }

        for camino, _, resultado in self._recorridos(estado_inicial, cartas_reales):
            if resultado["fin"]:
                continue
            assert resultado["carta"]["id"] in cartas_reales, "carta desconocida en %s" % camino

    def test_todo_recorrido_termina_con_fin_o_sigue_en_juego(self, cartas_reales):
        estado_inicial = {
            "salud": 90, "social": 40, "intelecto": 50,
            "laboral": 70, "dinero": 100000, "carta_actual_id": "inicio",
        }

        for camino, _, resultado in self._recorridos(estado_inicial, cartas_reales):
            assert isinstance(resultado["fin"], bool)
            if resultado["fin"]:
                assert "mensaje" in resultado, "cierre sin mensaje en %s" % camino
            else:
                assert resultado["carta"] is not None
