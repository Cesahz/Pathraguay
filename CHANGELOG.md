# Changelog

Registro de cambios de Pathraguay.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y
el versionado sigue [SemVer](https://semver.org/lang/es/).

## Criterio de versionado

El proyecto esta en la serie `0.x`. La version que gano la hackathon CodePRO
5.1 es un MVP funcional, no un producto terminado, y se registra como `0.1.0`.

Lo que falta para llegar a `1.0.0`:

- la narrativa termina en un nodo inexistente que cierra la demo: el grafo
  publicado son doce nodos de un recorrido mucho mas largo
- el servidor sostiene una sola partida en memoria, sin sesiones: dos
  jugadores simultaneos comparten el mismo estado
- no hay persistencia, de modo que reiniciar el proceso borra la partida
- solo dos de las cinco stats terminan la partida

Hasta que esos puntos se resuelvan, la version menor sube con cada
incorporacion y la de parche con las correcciones.

---

## [0.2.0] - no publicado

Reordenamiento interno del proyecto. Las reglas del juego y el recorrido
narrativo no cambian respecto de `0.1.0`.

### Agregado

- Suite de 92 pruebas sobre pytest, que cubre las reglas del motor, el
  catalogo de clases, el contrato http, la integridad del grafo publicado y
  el mapeo de imagenes. Validada contra diez mutaciones deliberadas del
  codigo y de los datos, todas detectadas.
- `herramientas/verificar_imagenes.py`, que recorre las referencias a
  imagenes de `cartas.json` y del front y falla si alguna no resuelve a un
  archivo existente. Compara contra el listado del directorio para detectar
  desfasajes de mayusculas, invisibles en Windows y fatales en Linux.
- `static/img/predeterminado.png`, respaldo real para la ruta a la que ya
  apuntaba el cliente.
- `pytest.ini` y `requirements-dev.txt`.
- Navegacion con las flechas del teclado, foco visible en todos los
  controles y traslado del foco al boton de reinicio al cerrar la partida.
- Marcado semantico, roles y etiquetas accesibles en los superpuestos, y
  regiones live para que los cambios de situacion y de atributos se anuncien.
- Respeto por la preferencia de movimiento reducido del sistema.

### Cambiado

- El codigo se reorganizo en tres capas con las dependencias apuntando hacia
  adentro: `pathraguay/dominio` con las reglas del juego, `pathraguay/datos`
  con la lectura del grafo y `pathraguay/web` con el transporte http.
  `main.py` y `motor.py` quedaron disueltos ahi.
- `app.py` pasa a ser el punto de entrada y el unico modulo que conoce el
  layout en disco; le inyecta las rutas a la capa web.
- El motor dejo de operar sobre variables globales y recibe el estado y el
  grafo por parametro. El estado de partida unica se conserva, ahora alojado
  en la capa web.
- `generador_cartas.py` se movio a `herramientas/`, por ser una utilidad de
  autoria de contenido y no parte del servidor.
- Assets renombrados a nombres descriptivos: `oficina.png` a
  `oficina_dia.png`, `oficinahe.png` a `oficina_noche.png` y `home.png` a
  `dormitorio.png`.
- El `.gitignore` pasa de ocho reglas a una version completa por secciones,
  que cubre entornos virtuales, secretos, bases de datos, migraciones, tests,
  frontend, logs, editores y sistemas operativos.
- La hoja de estilos se reescribio con los colores, tipografias y espaciados
  extraidos a variables css, y el ancho del tablero pasa de fijo a fluido.
- Se eliminaron trece reglas de estilo que ningun archivo aplicaba y se
  agregaron las dos animaciones de estres que el cliente aplicaba sin que
  existieran.

### Corregido

- Las doce cartas mostraban un icono de imagen rota. Los nodos del grafo
  tenian el campo `img` vacio y caian a `/static/img/predeterminado.png`, que
  no existia en el repositorio. Se asigno su ilustracion a cada nodo y se
  sumaron los cinco assets que faltaban.
- `trabajosoñado.png` se renombro a `trabajo_sonado.png`: la eñe en el nombre
  del archivo rompe al servir la ruta segun el entorno.
- Los cinco assets que ya estaban en el repositorio no los referenciaba
  ningun archivo.
- El unico punto de corte del diseño estaba en 360px, de modo que entre
  361px y 500px la pagina se desbordaba horizontalmente.
- Las flechas de decision no alcanzaban el contraste minimo sobre su fondo.
- El catalogo de clases se insertaba con `innerHTML` interpolando texto
  devuelto por el servidor, que quedaba interpretado como marcado.
- La pantalla de cierre rompia si el servidor informaba un atributo que el
  cliente no tenia registrado, en lugar de usar el texto generico.
- Se quito una traza de depuracion que se emitia en cada decision.

---

## [0.1.0] - 2026-03-18

Version presentada en la hackathon CodePRO 5.1, desarrollada entre el 13 y el
18 de marzo de 2026.

### Agregado

- Motor de decisiones sobre un grafo dirigido de cartas, con avance por
  identificador de nodo y ramas que convergen.
- Cinco atributos de jugador: salud, social, intelecto, laboral y dinero. Los
  cuatro primeros acotados al rango 0-100, el dinero libre.
- Tres clases jugables con presets de stats distintos: Heredero, Pobre pero
  Honrado e Inteligente asocial.
- Dos condiciones de derrota, por salud agotada y por bancarrota, con
  pantalla de cierre y mensaje propio segun el atributo.
- Servidor Flask con cuatro endpoints: catalogo de clases, inicio de partida,
  consulta de estado y resolucion de decision.
- Cliente de una sola pagina con mecanica de swiping por arrastre, soporte
  tactil, botones de decision y vista previa del texto de cada opcion al
  pasar el mouse.
- HUD con barras de progreso animadas, indicadores flotantes de variacion por
  atributo y formato de moneda en guaranies.
- Doce nodos narrativos ambientados en Paraguay, con ilustraciones propias.
- `generador_cartas.py`, utilidad de linea de comandos para redactar cartas
  nuevas sin editar el JSON a mano.
