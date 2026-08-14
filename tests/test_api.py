"""pruebas del contrato http que consume el cliente.

fijan la forma de cada respuesta, porque static/app.js lee estas claves por
nombre y un cambio silencioso rompe la interfaz sin romper el backend.
"""

import pytest

from pathraguay.dominio import clases


def iniciar(cliente, clase="Pobre pero Honrado"):
    return cliente.post("/api/iniciar", json={"clase": clase})


class TestPaginaPrincipal:
    def test_la_pagina_se_sirve(self, cliente):
        respuesta = cliente.get("/")

        assert respuesta.status_code == 200
        assert "text/html" in respuesta.headers["Content-Type"]

    def test_la_pagina_carga_el_cliente_y_los_estilos(self, cliente):
        cuerpo = cliente.get("/").get_data(as_text=True)

        assert "/static/app.js" in cuerpo
        assert "/static/style.css" in cuerpo

    def test_los_estaticos_se_sirven(self, cliente):
        assert cliente.get("/static/app.js").status_code == 200
        assert cliente.get("/static/style.css").status_code == 200


class TestCatalogoDeClases:
    def test_devuelve_todas_las_clases(self, cliente):
        datos = cliente.get("/api/clases").get_json()

        assert set(datos) == set(clases.CLASES_DISPONIBLES)

    def test_cada_clase_expone_descripcion_y_stats(self, cliente):
        datos = cliente.get("/api/clases").get_json()

        for nombre, contenido in datos.items():
            assert set(contenido) == {"descripcion", "stats"}, nombre


class TestInicioDePartida:
    @pytest.mark.parametrize("nombre", list(clases.CLASES_DISPONIBLES))
    def test_iniciar_con_cada_clase(self, cliente, nombre):
        respuesta = iniciar(cliente, nombre)

        assert respuesta.status_code == 200
        assert respuesta.get_json() == {"status": "ok"}

    def test_las_stats_iniciales_son_las_de_la_clase(self, cliente):
        iniciar(cliente, "Heredero")

        stats = cliente.get("/api/estado").get_json()["stats"]

        for stat, valor in clases.CLASES_DISPONIBLES["Heredero"]["stats"].items():
            assert stats[stat] == valor

    def test_una_clase_desconocida_no_rompe_el_servidor(self, cliente):
        respuesta = iniciar(cliente, "clase_inventada")

        assert respuesta.status_code == 200
        stats = cliente.get("/api/estado").get_json()["stats"]
        esperado = clases.CLASES_DISPONIBLES[clases.CLASE_POR_DEFECTO]["stats"]
        assert stats["salud"] == esperado["salud"]

    def test_reiniciar_descarta_la_partida_anterior(self, cliente):
        iniciar(cliente, "Heredero")
        cliente.post("/api/decision", json={"eleccion": "izq"})

        iniciar(cliente, "Heredero")

        estado = cliente.get("/api/estado").get_json()
        assert estado["carta"]["id"] == clases.CARTA_INICIAL


class TestEstado:
    def test_sin_partida_iniciada_responde_fin(self, cliente):
        datos = cliente.get("/api/estado").get_json()

        assert datos["fin"] is True
        assert datos["carta"] is None
        assert datos["stats"] == {}

    def test_con_partida_iniciada_devuelve_la_carta_inicial(self, cliente):
        iniciar(cliente)

        datos = cliente.get("/api/estado").get_json()

        assert datos["fin"] is False
        assert datos["carta"]["id"] == clases.CARTA_INICIAL
        assert set(datos["carta"]) >= {"texto", "img", "opcion_izq", "opcion_der", "id"}

    def test_consultar_el_estado_no_avanza_el_turno(self, cliente):
        iniciar(cliente)

        primero = cliente.get("/api/estado").get_json()
        segundo = cliente.get("/api/estado").get_json()

        assert primero == segundo


class TestDecision:
    @pytest.mark.parametrize("eleccion", ["izq", "der"])
    def test_cada_decision_avanza_el_grafo(self, cliente, eleccion):
        iniciar(cliente)

        datos = cliente.post("/api/decision", json={"eleccion": eleccion}).get_json()

        assert datos["fin"] is False
        assert datos["carta"]["id"] != clases.CARTA_INICIAL
        assert set(datos["efectos"]) == set(clases.STATS_BASE)

    def test_la_respuesta_incluye_las_stats_actualizadas(self, cliente):
        iniciar(cliente)
        antes = cliente.get("/api/estado").get_json()["stats"]["salud"]

        datos = cliente.post("/api/decision", json={"eleccion": "izq"}).get_json()

        efecto = datos["efectos"]["salud"]
        assert datos["stats"]["salud"] == max(0, min(100, antes + efecto))

    def test_el_estado_persiste_entre_pedidos(self, cliente):
        iniciar(cliente)

        avance = cliente.post("/api/decision", json={"eleccion": "izq"}).get_json()
        estado = cliente.get("/api/estado").get_json()

        assert estado["carta"]["id"] == avance["carta"]["id"]
        assert estado["stats"] == avance["stats"]

    def test_recorrer_hasta_el_final_de_la_demo(self, cliente):
        iniciar(cliente, "Heredero")

        for _ in range(20):
            datos = cliente.post("/api/decision", json={"eleccion": "izq"}).get_json()
            if datos["fin"]:
                break
        else:
            pytest.fail("la partida no termino en 20 turnos")

        assert "mensaje" in datos


class TestImagenesServidas:
    def test_la_carta_inicial_trae_una_imagen_que_se_puede_pedir(self, cliente):
        iniciar(cliente)

        carta = cliente.get("/api/estado").get_json()["carta"]

        assert carta["img"].startswith("/static/img/")
        respuesta = cliente.get(carta["img"])
        assert respuesta.status_code == 200
        assert "image/" in respuesta.headers["Content-Type"]

    def test_toda_carta_alcanzada_sirve_su_imagen(self, cliente, cartas_reales):
        iniciar(cliente, "Heredero")
        vistas = set()

        for _ in range(20):
            datos = cliente.post("/api/decision", json={"eleccion": "der"}).get_json()
            if datos["fin"]:
                break
            vistas.add(datos["carta"]["img"])

        assert vistas, "el recorrido no devolvio ninguna carta"
        for url in vistas:
            assert cliente.get(url).status_code == 200, "%s no se sirve" % url

    def test_el_respaldo_del_cliente_existe(self, cliente):
        """app.js cae a esta ruta cuando una carta no declara imagen."""
        assert cliente.get("/static/img/predeterminado.webp").status_code == 200
