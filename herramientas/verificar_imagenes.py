"""verificar que toda referencia a una imagen resuelva a un archivo real.

recorre las tres fuentes donde el proyecto nombra imagenes:

- data/cartas.json, el campo img de cada nodo del grafo
- static/app.js, rutas literales como la imagen de respaldo
- templates/index.html y static/style.css, atributos src y url()

para cada referencia comprueba que el archivo exista en disco con ese nombre
exacto, comparando contra el listado del directorio en vez de usar
os.path.exists: windows y macos ignoran mayusculas y dejarian pasar un
desfasaje que rompe recien al desplegar en linux.

reporta ademas los assets que estan en disco sin que nadie los referencie.
devuelve codigo 1 si alguna referencia quedo colgada.

uso:
    python herramientas/verificar_imagenes.py
"""

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_IMAGENES = RAIZ / "static" / "img"
PREFIJO_URL = "/static/img/"

#archivos donde pueden aparecer rutas de imagen escritas a mano
FUENTES_DE_TEXTO = (
    Path("static") / "app.js",
    Path("templates") / "index.html",
    Path("static") / "style.css",
)

#captura cualquier ruta que apunte a la carpeta de imagenes
PATRON_RUTA = re.compile(r"/static/img/([^\"'\s)>]+)")


def _referencias_del_grafo(errores):
    """extraer el campo img de cada nodo de cartas.json."""
    ruta = RAIZ / "data" / "cartas.json"
    cartas = json.loads(ruta.read_text(encoding="utf-8"))

    referencias = []
    for nodo, datos in cartas.items():
        valor = datos.get("img", "")
        origen = "data/cartas.json[%s]" % nodo

        if valor == "":
            #un nodo sin imagen cae al respaldo y se ve como una carta rota
            errores.append("%s: campo img vacio" % origen)
            continue

        if not valor.startswith(PREFIJO_URL):
            errores.append("%s: ruta fuera de %s -> %r" % (origen, PREFIJO_URL, valor))
            continue

        referencias.append((origen, valor[len(PREFIJO_URL):]))

    return referencias


def _referencias_del_codigo():
    """extraer rutas de imagen escritas directamente en el front."""
    referencias = []
    for relativa in FUENTES_DE_TEXTO:
        ruta = RAIZ / relativa
        if not ruta.exists():
            continue

        contenido = ruta.read_text(encoding="utf-8")
        for numero, linea in enumerate(contenido.splitlines(), start=1):
            for nombre in PATRON_RUTA.findall(linea):
                referencias.append(("%s:%d" % (relativa.as_posix(), numero), nombre))

    return referencias


def main():
    errores = []
    referencias = _referencias_del_grafo(errores) + _referencias_del_codigo()

    #listado real del directorio, para comparar respetando mayusculas
    en_disco = {p.name for p in CARPETA_IMAGENES.iterdir() if p.is_file()}

    print("referencias encontradas: %d" % len(referencias))
    print("archivos en %s: %d\n" % (CARPETA_IMAGENES.relative_to(RAIZ).as_posix(), len(en_disco)))

    usados = set()
    for origen, nombre in sorted(referencias):
        if nombre in en_disco:
            estado = "ok"
            usados.add(nombre)
        elif nombre.lower() in {n.lower() for n in en_disco}:
            estado = "ERROR mayusculas"
            errores.append("%s: %r difiere en mayusculas del archivo real" % (origen, nombre))
        else:
            estado = "ERROR no existe"
            errores.append("%s: %r no existe en disco" % (origen, nombre))

        print("  [%-15s] %-34s <- %s" % (estado, nombre, origen))

    huerfanos = sorted(en_disco - usados)
    if huerfanos:
        print("\nassets sin referencia (no rompen el juego):")
        for nombre in huerfanos:
            print("  %s" % nombre)

    if errores:
        print("\nFALLO: %d referencia(s) colgada(s)" % len(errores))
        for detalle in errores:
            print("  %s" % detalle)
        return 1

    print("\nOK: las %d referencias resuelven a un archivo existente" % len(referencias))
    return 0


if __name__ == "__main__":
    sys.exit(main())
