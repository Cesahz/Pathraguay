"""pruebas del catalogo de clases y del estado inicial de partida."""

import copy

import pytest

from pathraguay.dominio import clases


class TestCatalogo:
    def test_toda_clase_declara_descripcion_y_stats(self):
        for nombre, datos in clases.CLASES_DISPONIBLES.items():
            assert datos["descripcion"].strip(), "%s sin descripcion" % nombre
            assert set(datos["stats"]) == set(clases.STATS_BASE), "%s con stats incompletas" % nombre

    def test_las_stats_iniciales_son_enteras(self):
        for nombre, datos in clases.CLASES_DISPONIBLES.items():
            for stat, valor in datos["stats"].items():
                assert isinstance(valor, int), "%s.%s no es entero" % (nombre, stat)

    def test_las_stats_acotadas_arrancan_dentro_del_rango(self):
        for nombre, datos in clases.CLASES_DISPONIBLES.items():
            for stat, valor in datos["stats"].items():
                if stat == "dinero":
                    continue
                assert 0 <= valor <= 100, "%s.%s arranca fuera de 0-100" % (nombre, stat)

    def test_ninguna_clase_arranca_ya_perdida(self):
        """una clase con salud en cero o dinero negativo seria injugable."""
        for nombre, datos in clases.CLASES_DISPONIBLES.items():
            assert datos["stats"]["salud"] > 0, "%s arranca sin salud" % nombre
            assert datos["stats"]["dinero"] >= 0, "%s arranca en bancarrota" % nombre

    def test_la_clase_por_defecto_existe(self):
        assert clases.CLASE_POR_DEFECTO in clases.CLASES_DISPONIBLES

    def test_obtener_clases_devuelve_el_catalogo(self):
        assert clases.obtener_clases() == clases.CLASES_DISPONIBLES


class TestEstadoInicial:
    @pytest.mark.parametrize("nombre", list(clases.CLASES_DISPONIBLES))
    def test_el_estado_refleja_las_stats_de_la_clase(self, nombre):
        estado = clases.crear_estado_inicial(nombre)

        for stat, valor in clases.CLASES_DISPONIBLES[nombre]["stats"].items():
            assert estado[stat] == valor

    def test_el_estado_arranca_en_la_carta_inicial(self):
        estado = clases.crear_estado_inicial("Heredero")

        assert estado["carta_actual_id"] == clases.CARTA_INICIAL

    def test_el_estado_no_trae_claves_de_mas(self):
        estado = clases.crear_estado_inicial("Heredero")

        assert set(estado) == set(clases.STATS_BASE) | {"carta_actual_id"}

    @pytest.mark.parametrize("entrada", [None, "", "clase_inexistente", 0, "heredero"])
    def test_una_clase_desconocida_cae_en_la_por_defecto(self, entrada):
        """incluida la variante en minuscula: el catalogo distingue mayusculas."""
        esperado = clases.CLASES_DISPONIBLES[clases.CLASE_POR_DEFECTO]["stats"]

        estado = clases.crear_estado_inicial(entrada)

        for stat, valor in esperado.items():
            assert estado[stat] == valor

    def test_sin_argumento_usa_la_clase_por_defecto(self):
        assert clases.crear_estado_inicial() == clases.crear_estado_inicial(clases.CLASE_POR_DEFECTO)

    def test_modificar_el_estado_no_contamina_el_catalogo(self):
        original = copy.deepcopy(clases.CLASES_DISPONIBLES)

        estado = clases.crear_estado_inicial("Heredero")
        estado["salud"] = -999
        estado["carta_actual_id"] = "pisado"

        assert clases.CLASES_DISPONIBLES == original

    def test_dos_partidas_no_comparten_estado(self):
        primera = clases.crear_estado_inicial("Heredero")
        segunda = clases.crear_estado_inicial("Heredero")

        primera["salud"] = 1

        assert segunda["salud"] == clases.CLASES_DISPONIBLES["Heredero"]["stats"]["salud"]
