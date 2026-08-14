"""punto de entrada del servidor.

unico lugar del proyecto que conoce el layout en disco: resuelve las rutas y
se las inyecta a la capa web, que a su vez no sabe donde viven los archivos.
"""

from pathlib import Path

from pathraguay.web.servidor import crear_app

RAIZ = Path(__file__).resolve().parent

app = crear_app(
    ruta_cartas=RAIZ / "data" / "cartas.json",
    carpeta_static=RAIZ / "static",
    carpeta_templates=RAIZ / "templates",
)

if __name__ == "__main__":
    app.run(debug=True)
