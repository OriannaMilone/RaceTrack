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

def formatear_lap_time(td):
    if pd.isnull(td):
        return "00:00.000"
    if isinstance(td, str):
        td = pd.to_timedelta(td)
    total_seconds = td.total_seconds()
    minutos = int(total_seconds // 60)
    segundos = int(total_seconds % 60)
    milisegundos = int((total_seconds % 1) * 1000)
    return f"{minutos:02}:{segundos:02}.{milisegundos:03}"

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
            vuel = datos_vuelta[["Driver", "Position", "Team", "LapTime", "Compound", "IsPersonalBest"]].sort_values(by="Position")
            starting_values = datos_vuelta[["Driver", "GridPosition", "FinishingPosition", "FinalStatus"]]
            extra_values = datos_vuelta[["Driver", "Position", "Sector1Time","Sector2Time","Sector3Time","PitInTime","PitOutTime","PitStopDuration"]]
            vuel["Compound"] = vuel["Compound"].fillna("TBD")
            vuel["LapTime"] = vuel["LapTime"].apply(lambda x: pd.to_timedelta(x) if isinstance(x, str) else x)
            vuel["IsPersonalBest"] = vuel["IsPersonalBest"].replace({True: "Yes", False: "No"})
            
            if "LapTime" in vuel.columns:
                vuel["LapTime"] = vuel["LapTime"].apply(formatear_lap_time)
            
            vuel = vuel.fillna("N/A")
            print(vuel.to_string(index=False))
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
