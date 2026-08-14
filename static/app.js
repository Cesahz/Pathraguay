/* controlador principal del juego */
const ControladorVisual = {
    busy: false, // evita que el jugador haga dos acciones al mismo tiempo
    terminado: false, // bloquea la entrada una vez que la partida cerro
    cartaActual: null, // guarda la carta que esta en pantalla
    
    // textos e iconos para cuando te quedas en cero
    mensajesDerrota: {
        salud:     { icon: '🏥', title: 'internado en el ips',  msg: 'tu cuerpo aguantó todo lo que le pediste. un día simplemente no pudo más.' },
        intelecto: { icon: '📋', title: 'perdiste la beca',      msg: 'las materias se acumularon hasta que ya no hubo vuelta atrás.' },
        laboral:   { icon: '📦', title: 'te despidieron',        msg: 'te llamaron a una reunión corta. te dieron un sobre.' },
        social:    { icon: '🪟', title: 'depresión',             msg: 'hace semanas que no contestás mensajes. la gente dejó de enviarlos.' },
        dinero:    { icon: '🪙', title: 'te quedaste sin nada',  msg: 'la cuenta llegó a cero y los compromisos siguieron llegando.' }
    },

    // le da formato de moneda al texto del dinero
    fmt: function(n) { return '₲ ' + Math.abs(n).toLocaleString('es-PY'); },

    // pide los datos iniciales al servidor para empezar a jugar
    inicializar: function() {
        fetch('/api/estado')
            .then(res => res.json())
            .then(datos => {
                this.renderizarStats(datos.stats);
                if (!datos.fin) {
                    this.cartaActual = datos.carta;
                    this.renderizarCarta(this.cartaActual);
                }
                this.asignarEventos();
            });
    },

    // prepara la carta nueva en la pantalla
    renderizarCarta: function(carta) {
        // actualiza la imagen real de la carta
        const imgElement = document.getElementById('ui-card-img');

        // revisa si la carta tiene una imagen valida
        if (carta.img && carta.img !== "") {
            imgElement.src = carta.img; // carga la imagen de la base de datos
        } else {
            // imagen por defecto por seguridad si no hay ruta definida
            imgElement.src = "/static/img/predeterminado.png";
        }
        // la ilustracion acompaña al texto, no aporta informacion propia
        imgElement.alt = '';

        this.actualizarTextoCarta('base');
        document.getElementById('log').textContent = '';
    },

    // cambia el texto que lees dependiendo de si mueves la carta a la izquierda o derecha
    actualizarTextoCarta: function(modo) {
        if (!this.cartaActual) return;
        const st = document.getElementById('situation-text');
        if (modo === 'izq') {
            st.textContent = '« ' + this.cartaActual.opcion_izq.texto;
            st.style.color = '#8a8fa8';
        } else if (modo === 'der') {
            st.textContent = this.cartaActual.opcion_der.texto + ' »';
            st.style.color = '#8a8fa8';
        } else {
            st.textContent = this.cartaActual.texto;
            st.style.color = '#d0d2dc';
        }
    },

    // actualiza las barras de vida, estudio, trabajo, etc.
    renderizarStats: function(stats) {
        document.getElementById('ui-salud').style.width = stats.salud + '%';
        document.getElementById('ui-intelecto').style.width = stats.intelecto + '%';
        document.getElementById('ui-laboral').style.width = stats.laboral + '%';
        document.getElementById('ui-social').style.width = stats.social + '%';
        
        document.getElementById('val-salud').textContent = stats.salud + '%';
        document.getElementById('val-intelecto').textContent = stats.intelecto + '%';
        document.getElementById('val-laboral').textContent = stats.laboral + '%';
        document.getElementById('val-social').textContent = stats.social + '%';
        document.getElementById('ui-dinero').textContent = this.fmt(stats.dinero);
    },

    // hace aparecer los numeritos flotantes de daño o beneficio
    mostrarDeltas: function(efectos) {
        if (!efectos) return;
        ['salud', 'intelecto', 'laboral', 'social'].forEach(k => {
            const v = efectos[k] || 0;
            const b = document.getElementById('d-' + k);
            if (!b) return;
            b.classList.remove('show', 'up', 'down');
            if (v === 0) return;
            b.textContent = (v > 0 ? '+' : '') + v + '%';
            b.classList.add(v > 0 ? 'up' : 'down');
            requestAnimationFrame(() => requestAnimationFrame(() => b.classList.add('show')));
        });
        const db = document.getElementById('d-dinero');
        if (db && efectos.dinero && efectos.dinero !== 0) {
            db.classList.remove('show', 'up', 'down');
            db.textContent = (efectos.dinero > 0 ? '+' : '-') + this.fmt(efectos.dinero);
            db.classList.add(efectos.dinero > 0 ? 'up' : 'down');
            requestAnimationFrame(() => requestAnimationFrame(() => db.classList.add('show')));
        }
    },

    // esconde los numeritos flotantes
    ocultarDeltas: function() {
        ['salud', 'intelecto', 'laboral', 'social', 'dinero'].forEach(k => {
            const b = document.getElementById('d-' + k);
            if (b) b.classList.remove('show', 'up', 'down');
        });
    },

    // activa la pantalla de muerte
    ejecutarGameOver: function(statFatal, mensajeServidor) {
        this.ocultarDeltas();
        // el overlay tapa el mouse, pero el teclado sigue llegando: hay que cortarlo aca
        this.terminado = true;

        // si el servidor informa una stat que el cliente no conoce, se usa el cierre generico
        const derrota = statFatal ? this.mensajesDerrota[statFatal] : null;
        const title = derrota ? derrota.title : 'fin del trayecto';
        const msg = derrota ? derrota.msg : mensajeServidor;
        const icon = derrota ? derrota.icon : '⏳';

        document.getElementById('go-icon').textContent = icon;
        document.getElementById('go-title').textContent = title;
        document.getElementById('go-msg').textContent = msg;
        
        if (derrota) {
            const labels = { salud: 'salud · 0%', intelecto: 'intelecto · 0%', laboral: 'laboral · 0%', social: 'social · 0%', dinero: 'dinero · ₲ 0' };
            document.getElementById('go-stat-label').textContent = labels[statFatal];
            document.getElementById('row-' + statFatal).classList.add('bar-critical');
        } else {
            document.getElementById('go-stat-label').textContent = "equilibrio temporal";
        }

        const overlay = document.getElementById('gameover-overlay');
        setTimeout(() => {
            overlay.classList.add('active');
            overlay.setAttribute('aria-hidden', 'false');
            // lleva el foco al boton de reinicio para poder seguir sin mouse
            document.getElementById('go-restart').focus();
        }, 500);
    },

    // envia la decision al servidor y procesa lo que pasa despues
    ejecutarSwipe: function(dir) {
        if (this.busy || this.terminado || !this.cartaActual) return;
        this.busy = true; // bloquea controles
        
        const ci = document.getElementById('card-inner');
        const opcion = dir === 'izq' ? this.cartaActual.opcion_izq : this.cartaActual.opcion_der;

        document.getElementById('log').textContent = '› ' + opcion.texto;
        ci.classList.add(dir === 'izq' ? 'fly-l' : 'fly-r');

        // envia los datos
        fetch('/api/decision', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ eleccion: dir })
        })
        .then(res => res.json())
        .then(resultadoBackend => {
            setTimeout(() => {
                this.renderizarStats(resultadoBackend.stats);
                this.mostrarDeltas(resultadoBackend.efectos); 

                // animacion de parpadeo en las barras alteradas
                ['salud', 'intelecto', 'laboral', 'social'].forEach(k => {
                    if (!resultadoBackend.efectos || !resultadoBackend.efectos[k]) return;
                    const r = document.getElementById('row-' + k);
                    r.classList.remove('bar-changing');
                    void r.offsetWidth;
                    r.classList.add('bar-changing');
                    setTimeout(() => r.classList.remove('bar-changing'), 600);
                });

                // revisa si moriste
                if (resultadoBackend.fin) {
                    setTimeout(() => { this.ejecutarGameOver(resultadoBackend.stat_fatal, resultadoBackend.mensaje); this.busy = false; }, 700);
                    return; 
                }

                // si no mueres, evalua el trauma
                let demoraNarrativa = 600;

                if (resultadoBackend.alerta) {
                    demoraNarrativa = 4500; // pausa el juego unos segundos
                    const gameDiv = document.getElementById('game');
                    const panicOverlay = document.getElementById('panic-overlay');
                    const panicMsg = document.getElementById('panic-msg');
                    
                    // inyecta el texto del pensamiento intrusivo
                    panicMsg.textContent = resultadoBackend.alerta.mensaje;
                    
                    // activa la pantalla clonada
                    panicOverlay.classList.add('active');
                    panicOverlay.setAttribute('aria-hidden', 'false');
                    gameDiv.classList.add('stress-tremble', 'stress-vignette');

                    // la oculta despues de 4 segundos para seguir jugando
                    setTimeout(() => {
                        panicOverlay.classList.remove('active');
                        panicOverlay.setAttribute('aria-hidden', 'true');
                        gameDiv.classList.remove('stress-tremble', 'stress-vignette');
                    }, 4000);
                }

                // carga la proxima carta
                setTimeout(() => {
                    this.ocultarDeltas();
                    this.cartaActual = resultadoBackend.carta;
                    this.renderizarCarta(this.cartaActual);
                    ci.classList.remove('fly-l', 'fly-r', 'tilt-l', 'tilt-r');
                    void ci.offsetWidth;
                    ci.classList.add('entering');
                    setTimeout(() => { ci.classList.remove('entering'); this.busy = false; }, 350);
                }, demoraNarrativa);

            }, 880);
        });
    },

    // configura el mouse, la pantalla tactil y los botones
    asignarEventos: function() {
        let drag = false, sx = 0, cx = 0;
        const ci = document.getElementById('card-inner');

        // detecta cuando haces clic o tocas la carta
        const ds = (x) => { if (!this.busy && !this.terminado) { drag = true; sx = x; } };
        
        // detecta cuando arrastras la carta
        const dm = (x) => {
            if (!drag) return;
            cx = x - sx;
            ci.classList.remove('tilt-l', 'tilt-r');
            if (cx < -30) {
                ci.classList.add('tilt-l');
                this.actualizarTextoCarta('izq');
            } else if (cx > 30) {
                ci.classList.add('tilt-r');
                this.actualizarTextoCarta('der');
            } else {
                this.actualizarTextoCarta('base');
            }
        };
        
        // detecta cuando sueltas la carta
        const de = () => {
            if (!drag) return;
            drag = false;
            if (cx < -60) this.ejecutarSwipe('izq');
            else if (cx > 60) this.ejecutarSwipe('der');
            else {
                ci.classList.remove('tilt-l', 'tilt-r');
                this.actualizarTextoCarta('base');
            }
            cx = 0;
        };

        // enlaza los eventos de arrastre a la pantalla
        ci.addEventListener('mousedown', e => ds(e.clientX));
        window.addEventListener('mousemove', e => dm(e.clientX));
        window.addEventListener('mouseup', de);
        ci.addEventListener('touchstart', e => ds(e.touches[0].clientX), { passive: true });
        window.addEventListener('touchmove', e => dm(e.touches[0].clientX), { passive: true });
        window.addEventListener('touchend', de);

        // enlaza los clicks en los botones de accion
        document.getElementById('btn-izq').addEventListener('click', () => this.ejecutarSwipe('izq'));
        document.getElementById('btn-der').addEventListener('click', () => this.ejecutarSwipe('der'));
        
        // boton para reiniciar la pagina al perder
        document.getElementById('go-restart').addEventListener('click', () => {
            location.reload(); 
        });

        // efectos de pasar el mouse por los botones de accion
        const btnIzq = document.getElementById('btn-izq');
        const btnDer = document.getElementById('btn-der');
        
        btnIzq.addEventListener('mouseenter', () => { if(!this.busy) this.actualizarTextoCarta('izq'); });
        btnIzq.addEventListener('mouseleave', () => { if(!this.busy) this.actualizarTextoCarta('base'); });
        
        btnDer.addEventListener('mouseenter', () => { if(!this.busy) this.actualizarTextoCarta('der'); });
        btnDer.addEventListener('mouseleave', () => { if(!this.busy) this.actualizarTextoCarta('base'); });

        // permite jugar con el teclado, sin mouse ni pantalla tactil
        window.addEventListener('keydown', e => {
            if (e.key === 'ArrowLeft') this.ejecutarSwipe('izq');
            else if (e.key === 'ArrowRight') this.ejecutarSwipe('der');
        });
    }
};

// se ejecuta cuando la pagina termina de cargar
document.addEventListener('DOMContentLoaded', () => {
    // pide las clases disponibles al servidor
    fetch('/api/clases')
        .then(res => res.json())
        .then(clases => {
            const container = document.getElementById('clases-container');
            container.innerHTML = ''; 
            
            // crea un boton por cada clase en el menu principal
            for (const [nombre, datos] of Object.entries(clases)) {
                const btn = document.createElement('button');
                btn.className = 'btn-clase';
                btn.type = 'button';
                btn.setAttribute('role', 'listitem');
                btn.onclick = () => elegirClase(nombre);

                // se arma con nodos de texto para no interpretar el contenido como html
                const titulo = document.createElement('span');
                titulo.className = 'clase-nombre';
                titulo.textContent = nombre;

                const descripcion = document.createElement('span');
                descripcion.className = 'clase-desc';
                descripcion.textContent = datos.descripcion;

                btn.append(titulo, descripcion);
                container.appendChild(btn);
            }
        });
});

// envia la clase elegida al servidor y quita el menu
function elegirClase(nombreClase) {
    fetch('/api/iniciar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clase: nombreClase })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'ok') {
            document.getElementById('start-screen').style.display = 'none';
            ControladorVisual.inicializar();
        }
    });
}