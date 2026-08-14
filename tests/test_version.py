"""pruebas de consistencia entre la version del paquete y el changelog."""

import re

import pytest

import pathraguay
from app import RAIZ

CHANGELOG = RAIZ / "CHANGELOG.md"

#encabezados del tipo "## [0.2.0] - no publicado"
PATRON_VERSION = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (.+)$", re.MULTILINE)


@pytest.fixture(scope="module")
def entradas():
    return PATRON_VERSION.findall(CHANGELOG.read_text(encoding="utf-8"))


class TestVersionDelPaquete:
    def test_la_version_sigue_semver(self):
        assert re.fullmatch(r"\d+\.\d+\.\d+", pathraguay.__version__)

    def test_la_version_coincide_con_la_primera_entrada(self, entradas):
        """la entrada de mas arriba del changelog es siempre la version en curso."""
        assert entradas[0][0] == pathraguay.__version__


class TestChangelog:
    def test_declara_al_menos_dos_versiones(self, entradas):
        assert len(entradas) >= 2

    def test_las_versiones_no_se_repiten(self, entradas):
        numeros = [numero for numero, _ in entradas]
        assert len(numeros) == len(set(numeros)), "versiones duplicadas: %s" % numeros

    def test_las_versiones_van_de_mayor_a_menor(self, entradas):
        numeros = [tuple(int(parte) for parte in numero.split(".")) for numero, _ in entradas]
        assert numeros == sorted(numeros, reverse=True), "el orden del changelog esta alterado"

    def test_toda_version_publicada_lleva_fecha(self, entradas):
        for numero, referencia in entradas:
            if referencia == "no publicado":
                continue
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", referencia), \
                "la version %s no declara una fecha valida: %r" % (numero, referencia)

    def test_solo_la_primera_entrada_puede_estar_sin_publicar(self, entradas):
        posteriores = [numero for numero, referencia in entradas[1:] if referencia == "no publicado"]
        assert not posteriores, "versiones sin publicar fuera del tope: %s" % posteriores
