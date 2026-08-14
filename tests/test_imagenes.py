"""pruebas del mapeo entre el grafo y los archivos de imagen en disco.

replican en la suite lo que hace herramientas/verificar_imagenes.py, para que
un renombrado de asset rompa el build y no recien la pantalla del jugador.
"""

import re
import subprocess
import sys

from app import RAIZ

CARPETA_IMAGENES = RAIZ / "static" / "img"
PREFIJO = "/static/img/"
PATRON_RUTA = re.compile(r"/static/img/([^\"'\s)>]+)")

#archivos del front donde pueden aparecer rutas escritas a mano
FUENTES = ("static/app.js", "templates/index.html", "static/style.css")


def _archivos_en_disco():
    return {ruta.name for ruta in CARPETA_IMAGENES.iterdir() if ruta.is_file()}


class TestReferenciasDelGrafo:
    def test_ningun_nodo_queda_sin_imagen(self, cartas_reales):
        """un campo vacio manda la carta al respaldo y se ve como un error."""
        for identificador, carta in cartas_reales.items():
            assert carta["img"].strip(), "%s sin imagen" % identificador

    def test_toda_imagen_apunta_a_la_carpeta_de_assets(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            assert carta["img"].startswith(PREFIJO), \
                "%s apunta fuera de %s: %r" % (identificador, PREFIJO, carta["img"])

    def test_toda_imagen_existe_en_disco(self, cartas_reales):
        en_disco = _archivos_en_disco()

        for identificador, carta in cartas_reales.items():
            nombre = carta["img"][len(PREFIJO):]
            assert nombre in en_disco, "%s referencia %r, que no existe" % (identificador, nombre)

    def test_los_nombres_coinciden_en_mayusculas(self, cartas_reales):
        """windows ignora mayusculas y deja pasar lo que rompe en linux."""
        en_disco = _archivos_en_disco()
        sin_mayusculas = {nombre.lower(): nombre for nombre in en_disco}

        for identificador, carta in cartas_reales.items():
            nombre = carta["img"][len(PREFIJO):]
            equivalente = sin_mayusculas.get(nombre.lower())
            assert equivalente == nombre, \
                "%s referencia %r pero el archivo es %r" % (identificador, nombre, equivalente)

    def test_ningun_nombre_de_asset_usa_caracteres_conflictivos(self):
        """acentos, eñes y espacios rompen al servir la ruta segun el entorno."""
        for nombre in _archivos_en_disco():
            assert re.fullmatch(r"[a-z0-9_.-]+", nombre), "nombre problematico: %r" % nombre

    def test_ningun_nodo_usa_el_respaldo(self, cartas_reales):
        for identificador, carta in cartas_reales.items():
            assert not carta["img"].endswith("predeterminado.png"), \
                "%s quedo apuntando al respaldo" % identificador


class TestReferenciasDelFront:
    def test_las_rutas_escritas_en_el_front_existen(self):
        en_disco = _archivos_en_disco()
        encontradas = 0

        for relativa in FUENTES:
            contenido = (RAIZ / relativa).read_text(encoding="utf-8")
            for nombre in PATRON_RUTA.findall(contenido):
                encontradas += 1
                assert nombre in en_disco, "%s referencia %r, que no existe" % (relativa, nombre)

        assert encontradas, "no se encontro ninguna ruta de imagen en el front"


class TestHerramientaDeVerificacion:
    def test_la_herramienta_termina_sin_errores(self):
        resultado = subprocess.run(
            [sys.executable, "herramientas/verificar_imagenes.py"],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        )

        assert resultado.returncode == 0, resultado.stdout + resultado.stderr
