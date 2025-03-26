import pandas as pd
import time

df_original = pd.read_csv("../SPA_DATA/full_data_race/SPA_2018_full_H_data.csv")

df_original = df_original.sort_values(by=["LapNumber", "DriverNumber"])

df_simulado = pd.DataFrame()

# 4. Obtener el número total de vueltas en la carrera
vueltas_totales = int(df_original["LapNumber"].max())

# 5. Iterar vuelta por vuelta
for vuelta in range(1, vueltas_totales + 1):
    print(f"Simulando vuelta {vuelta}...")

    datos_vuelta = df_original[df_original["LapNumber"] == vuelta]
    df_simulado = pd.concat([df_simulado, datos_vuelta], ignore_index=True)

    print("Datos de la vuelta:")
    print(df_simulado)
    print("Siguiente vuelta en 90 segundos...")
    time.sleep(10)

# 6. Guardar el resultado final en un CSV
df_simulado.to_csv("carrera_simulada.csv", index=False)
