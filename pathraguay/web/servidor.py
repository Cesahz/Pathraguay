"""capa http: expone el motor como api json y sirve el cliente estatico."""

from flask import Flask, jsonify, render_template, request

from pathraguay.datos.repositorio_cartas import cargar_cartas
from pathraguay.dominio import clases, motor


def crear_app(ruta_cartas, carpeta_static, carpeta_templates):
    """armar la aplicacion flask con sus dependencias ya resueltas."""
    app = Flask(
        __name__,
        static_folder=str(carpeta_static),
        template_folder=str(carpeta_templates),
    )

    #el grafo se carga una sola vez al iniciar el servidor
    cartas = cargar_cartas(ruta_cartas)

    #el servidor sostiene una unica partida en memoria. dos clientes
    #simultaneos comparten el mismo estado, igual que en la version original
    partida = {"estado": {}}

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/clases", methods=["GET"])
    def get_clases():
        return jsonify(clases.obtener_clases())

    @app.route("/api/iniciar", methods=["POST"])
    def iniciar_partida():
        datos = request.json
        partida["estado"] = clases.crear_estado_inicial(datos.get("clase"))
        return jsonify({"status": "ok"})

    @app.route("/api/estado", methods=["GET"])
    def obtener_estado():
        return jsonify(motor.obtener_estado_actual(partida["estado"], cartas))

    @app.route("/api/decision", methods=["POST"])
    def procesar_decision():
        datos = request.json
        #eleccion llega como 'izq' o 'der'
        resultado = motor.procesar_turno(partida["estado"], cartas, datos.get("eleccion"))
        return jsonify(resultado)

    return app
