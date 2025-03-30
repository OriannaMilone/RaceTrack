import socketio
import time
from core.carrera import Carrera
from race_simulator.core.carrera_simulada import SimuladorDeCarrera
from pathlib import Path
import pandas as pd

sio = socketio.Client()

@sio.event(namespace='/simulador')
def connect():
    print("✅ Conectado al servidor Node.js (/simulador) [handler activado]")

@sio.event(namespace='/simulador')
def disconnect():
    print("❌ Desconectado del servidor (/simulador) [handler activado]")
    
@sio.event(namespace='/simulador')
def connect_error(data):
    print("❌ Error de conexión:", data)


def main():
    # Conectar justo antes de simular
    sio.connect('http://localhost:3000', namespaces=['/simulador'])

    csv_path = Path(__file__).resolve().parent.parent / "SPA_DATA" / "full_data_race" / "SPA_2018_full_H_data.csv"
    df = pd.read_csv(csv_path)

    carrera = Carrera(df)
    simulador = SimuladorDeCarrera(carrera, tiempo_entre_vueltas=1)

    print("🏁 Comienza la simulación de carrera...\n")

    try:
        while not simulador.esta_finalizada():
            datos_vuelta = simulador.simular_siguiente_vuelta()
            vuelta = simulador.get_vuelta_actual()

            print(f"\nVuelta {vuelta}:")
            vuel = datos_vuelta[["Driver", "Position", "Compound", "FinishingPosition", "GridPosition"]].sort_values(by="Position")
            print(vuel.to_string(index=False))

            vuel = vuel.fillna("N/A")
            
            # Enviar vuelta completa
            vuelta_completa = {
                "vuelta": vuelta,
                "pilotos": vuel.to_dict(orient="records")
            }

            # Esperar un pequeño delay antes del primer envío (por seguridad)
            time.sleep(0.1)
            print(f"📤 Enviando vuelta {vuelta} al servidor...\n")
            sio.emit('nueva-vuelta', vuelta_completa, namespace='/simulador')


    except StopIteration as e:
        print(f"\n⛔ Simulación detenida: {e}")

    finally:
        simulador.exportar_resultado("carrera_simulada.csv")
        sio.disconnect()
        print("✅ Simulación finalizada. Datos exportados a carrera_simulada.csv")

if __name__ == "__main__":
    main()
