import json
import os

# nombre del archivo donde se guardará tu progreso local
ARCHIVO_LOCAL = "cartas.json"

def leer_numero(mensaje):
    while True:
        entrada = input(mensaje).strip()
        if not entrada: return 0
        try:
            return int(entrada)
        except ValueError:
            print("❌ Poné un número (o dejá vacío para 0)")

def creador_local():
    # cargar si ya existe algo para no borrar lo anterior
    if os.path.exists(ARCHIVO_LOCAL):
        with open(ARCHIVO_LOCAL, 'r', encoding='utf-8') as f:
            biblioteca = json.load(f)
    else:
        biblioteca = {}

    print("="*50)
    print("🛠️  TALLER LOCAL DE CARTAS - PATHRAGUAY")
    print("="*50)
    print(f"Cargando desde: {os.path.abspath(ARCHIVO_LOCAL)}")

    while True:
        print("\n" + "-"*30)
        id_nodo = input("🔑 ID ÚNICO (ej: bache_en_choferes): ").strip()
        img = input("Pega el link de la imagen aqui: ")
        if not id_nodo: continue
        
        texto = input("📝 SITUACIÓN: ")
        
        # función interna para no repetir código de opciones
        def crear_opcion(lado):
            print(f"\n--- ⚡ OPCIÓN {lado} ---")
            txt = input(f"   Texto del botón {lado}: ")
            prox = input(f"   ¿A qué ID salta?: ")
            print(f"   EFECTOS (Enter para 0):")
            return {
                "texto": txt,
                "siguiente_id": prox,
                "efectos": {
                    "salud": leer_numero("      ❤️ Salud: "),
                    "dinero": leer_numero("      💸 Dinero: "),
                    "intelecto": leer_numero("      📚 Intelecto: "),
                    "laboral": leer_numero("      💼 Laboral: "),
                    "social": leer_numero("      🗣 Social: ")
                }
            }

        biblioteca[id_nodo] = {
            "texto": texto,
            "img": img,
            "opcion_izq": crear_opcion("IZQUIERDA"),
            "opcion_der": crear_opcion("DERECHA")
        }

        # guardar inmediatamente
        with open(ARCHIVO_LOCAL, 'w', encoding='utf-8') as f:
            json.dump(biblioteca, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Carta '{id_nodo}' guardada localmente.")
        
        if input("\n¿Otra carta? (s/n): ").lower() != 's':
            break

    print("\n" + "="*50)
    print(f"¡LISTO! Ahora podés abrir '{ARCHIVO_LOCAL}',")
    print("copiar el contenido y pegarlo en tu cartas.json real.")
    print("="*50)

if __name__ == "__main__":
    creador_local()