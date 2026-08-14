# Changelog

Registro de cambios de Pathraguay.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y
el versionado sigue [SemVer](https://semver.org/lang/es/).

## Criterio de versionado

El proyecto esta en la serie `0.x`. La version que gano la hackathon CodePRO
5.1 es un MVP funcional, no un producto terminado, y se registra como `0.1.0`.

`1.0.0` significa un juego terminado: jugable de principio a fin, balanceado,
probado con jugadores reales y con identidad propia. Falta lo siguiente.

**Contenido y narrativa**

- el grafo publicado son doce nodos, de un recorrido pensado mucho mas largo
- no hay finales escritos: el ultimo nodo apunta a un destino inexistente y la
  partida corta sin resolucion narrativa
- las tres clases jugables solo alteran las estadisticas iniciales. el
  recorrido no reacciona a la clase elegida, de modo que se juegan igual
- no hay variacion ni azar entre partidas, con lo cual la rejugabilidad es
  practicamente nula

**Balance**

- los efectos de cada opcion son valores sueltos, elegidos a mano y nunca
  ajustados. no existe una curva de dificultad
- las clases no estan equilibradas entre si. con Heredero, que arranca con
  cinco millones, la bancarrota es inalcanzable y el dinero deja de ser una
  amenaza durante toda la partida
- solo dos de las cinco estadisticas pueden terminar la partida. intelecto,
  laboral y social pueden llegar a cero sin consecuencia alguna
- ninguna decision se siente costosa porque los margenes iniciales son
  amplios frente a la magnitud de los efectos

**Testeo con jugadores**

- nadie jugo el recorrido de forma sistematica. no hay registro de partidas
  ni de donde se abandona
- no hay telemetria de que ramas se eligen, con lo cual no se sabe si alguna
  quedo muerta en la practica
- la dificultad percibida nunca se contrasto contra la intencion del diseño

**Identidad**

- las ilustraciones se generaron con IA y no comparten estilo, paleta ni
  autoria. el juego todavia no tiene una imagen propia
- no hay sonido ni musica

**Arquitectura y operacion**

- el servidor sostiene una sola partida en memoria, sin sesiones: dos
  jugadores simultaneos comparten el mismo estado
- no hay persistencia, de modo que reiniciar el proceso borra la partida
- no hay despliegue. el juego corre unicamente en local, sobre el servidor
  de desarrollo de Flask, que no es apto para produccion
- las pruebas no corren de forma automatica: no hay integracion continua

Hasta que esos puntos se resuelvan, la version menor sube con cada
incorporacion y la de parche con las correcciones.

---

## [0.2.0] - no publicado

Reordenamiento interno del proyecto. Las reglas del juego y el recorrido
narrativo no cambian respecto de `0.1.0`.

### Agregado

- Suite de 100 pruebas sobre pytest, que cubre las reglas del motor, el
  catalogo de clases, el contrato http, la integridad del grafo publicado y
  el mapeo de imagenes. Validada contra diez mutaciones deliberadas del
  codigo y de los datos, todas detectadas.
- `herramientas/verificar_imagenes.py`, que recorre las referencias a
  imagenes de `cartas.json` y del front y falla si alguna no resuelve a un
  archivo existente. Compara contra el listado del directorio para detectar
  desfasajes de mayusculas, invisibles en Windows y fatales en Linux.
- `static/img/predeterminado.webp`, respaldo real para la ruta a la que ya
  apuntaba el cliente.
- `pytest.ini` y `requirements-dev.txt`.
- Navegacion con las flechas del teclado, foco visible en todos los
  controles y traslado del foco al boton de reinicio al cerrar la partida.
- Marcado semantico, roles y etiquetas accesibles en los superpuestos, y
  regiones live para que los cambios de situacion y de atributos se anuncien.
- Respeto por la preferencia de movimiento reducido del sistema.
- La marca del juego sobre el titulo de la pantalla de inicio.

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
- Assets renombrados a nombres descriptivos: `oficina` a `oficina_dia`,
  `oficinahe` a `oficina_noche` y `home` a `dormitorio`.
- El `.gitignore` pasa de ocho reglas a una version completa por secciones,
  que cubre entornos virtuales, secretos, bases de datos, migraciones, tests,
  frontend, logs, editores y sistemas operativos.
- La hoja de estilos se reescribio con los colores, tipografias y espaciados
  extraidos a variables css, y el ancho del tablero pasa de fijo a fluido.
- Se eliminaron trece reglas de estilo que ningun archivo aplicaba y se
  agregaron las dos animaciones de estres que el cliente aplicaba sin que
  existieran.
- La interfaz se rediseño sobre un sistema tipografico unico. Se reemplazo la
  mezcla de IM Fell English con Share Tech Mono por la familia Archivo, que
  cubre los cuatro roles variando peso y ancho de una sola fuente variable.
- Paleta nueva sobre dos ejes, tinta y papel, con los cinco atributos
  llevados a una luminosidad comun y un acento unico usado con moderacion.
- Las once ilustraciones pasaron de PNG a WebP con tope de 1200 pixeles de
  ancho: de 9.25 MB a 873 KB, un decimo del peso original. Los originales
  quedan fuera del repositorio, en `assets_fuente/`.

### Corregido

- Las doce cartas mostraban un icono de imagen rota. Los nodos del grafo
  tenian el campo `img` vacio y caian a `/static/img/predeterminado.png`, que
  no existia en el repositorio. Se asigno su ilustracion a cada nodo y se
  sumaron los cinco assets que faltaban.
- `trabajosoñado` se renombro a `trabajo_sonado`: la eñe en el nombre del
  archivo rompe al servir la ruta segun el entorno.
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
