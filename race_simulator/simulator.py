from prediction_model.predict_interface import predecir_siguiente_vuelta
from race_simulator.core.carrera_simulada import SimuladorDeCarrera
from prediction_model.predict_next_lap import load_model
from core.carrera import Carrera
from pathlib import Path
import pandas as pd
import socketio
import time
import sys

sio = socketio.Client()

@sio.event(namespace='/simulador')
def connect():
    print("Conectado al servidor Node.js (/simulador) [handler activado]")

@sio.event(namespace='/simulador')
def disconnect():
    print("Desconectado del servidor (/simulador) [handler activado]")

@sio.event(namespace='/simulador')
def connect_error(data):
    print("Error de conexión:", data)

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
    if len(sys.argv) < 2:
        print("Error: Debes proporcionar el nombre del archivo CSV como argumento.")
        print("Ejemplo: python -m race_simulator.simulator SPA_2018_full_H_data.csv [dinamico]")
        return

    archivo_csv = sys.argv[1]
    usar_modelo_dinamico = len(sys.argv) >= 3 and sys.argv[2].lower() == "dinamico"

    circuito = archivo_csv.split('_')[0].upper()

    circuit_folder_map = {
        "SPA": "race_data/SPA_DATA",
        "MONACO": "race_data/MONACO_DATA",
        "SAOPAULO": "race_data/SAOPAULO_DATA",
        "MONZA": "race_data/MONZA_DATA"
    }

    if circuito not in circuit_folder_map:
        print(f"Error: Circuito '{circuito}' no reconocido. Debes usar uno de: {', '.join(circuit_folder_map.keys())}")
        return

    carpeta_datos = circuit_folder_map[circuito]
    csv_path = Path(__file__).resolve().parent.parent / carpeta_datos / "full_data_race" / archivo_csv

    if not csv_path.exists():
        print(f"Error: El archivo {archivo_csv} no existe en la ruta: {csv_path}")
        return
    # RUTA SERVIDOR 
    # sio.connect('https://racetrackthesis.tech', namespaces=['/simulador'])
    # RUTA LCOAL 
    sio.connect('http://localhost:6101', namespaces=['/simulador'])
    
    df = pd.read_csv(csv_path)
    
    modelo, modeloUsado = load_model(dinamico=usar_modelo_dinamico, circuit=circuito, year=archivo_csv.split('_')[1])
    
    print(f"Modelo usado: {modeloUsado}")
    
    carrera = Carrera(df)
    simulador = SimuladorDeCarrera(carrera, tiempo_entre_vueltas=1)

    print(f"\nComienza la simulación de carrera para el circuito {circuito}...\n")

    try:
        while not simulador.esta_finalizada():
            datos_vuelta = simulador.simular_siguiente_vuelta()

            df_pred = predecir_siguiente_vuelta(datos_vuelta, modelo)
            if not df_pred.empty:
                df_pred["PredictedFinalPosition"] = df_pred["PredictedRank"].astype(int)


            vuelta = simulador.get_vuelta_actual()

            vuel = datos_vuelta[["Driver", "Position", "Team", "LapTime", "Compound", "IsPersonalBest"]].sort_values(by="Position")
            vuel["Compound"] = vuel["Compound"].fillna("TBD")
            vuel["LapTime"] = vuel["LapTime"].apply(lambda x: pd.to_timedelta(x) if isinstance(x, str) else x)
            vuel["IsPersonalBest"] = vuel["IsPersonalBest"].replace({True: "Yes", False: "No"})

            if "LapTime" in vuel.columns:
                vuel["LapTime"] = vuel["LapTime"].apply(formatear_lap_time)

            vuel = vuel.fillna("N/A")

            vuelta_completa = {
                "vuelta": vuelta,
                "pilotos": vuel.to_dict(orient="records")
            }
            time.sleep(1)
            sio.emit('nueva-vuelta', vuelta_completa, namespace='/simulador')

            print("Predicciones generadas por el modelo:")
            print(df_pred)

            if not df_pred.empty:
                prediccion_para_frontend = df_pred[["Driver", "PredictedFinalPosition"]].sort_values("PredictedFinalPosition")
                sio.emit('prediccion-vuelta', {
                    "vuelta": vuelta + 1,
                    "predicciones": prediccion_para_frontend.to_dict(orient="records")
                }, namespace='/simulador')

    except StopIteration as e:
        print(f"\nSimulación detenida: {e}")

    finally:
        sio.disconnect()
        print(f"Simulación finalizada.")

if __name__ == "__main__":
    main()
