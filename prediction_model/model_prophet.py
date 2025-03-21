import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

def format_timedelta(td):
    """Convierte Timedelta a mm:ss.SSS"""
    if pd.isna(td):
        return None
    total_seconds = td.total_seconds()
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes):02}:{seconds:06.3f}"

def format_timedelta2(td):
    if pd.isna(td):
        return None  
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}"

# 📌 Cargar los datos
data = "../SPA_DATA/full_data_race/SPA_2022_full_H_data.csv"

df = pd.read_csv(data)

# 📌 Convertir LapNumber a una fecha ficticia para Prophet
df["ds"] = df["LapNumber"].apply(lambda x: datetime(2024, 1, 1) + timedelta(minutes=int(x)))
df["y"] = df["Position"].fillna(0).astype(int)  # Prophet espera una columna 'y' numérica
# df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").apply(format_timedelta)
# df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").apply(format_timedelta)
# df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").apply(format_timedelta)
df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").dt.total_seconds().fillna(0)
df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").dt.total_seconds().fillna(0)


df["PitInTime"] = pd.to_timedelta(df["PitInTime"], errors="coerce").apply(format_timedelta2)
df["PitOutTime"] = pd.to_timedelta(df["PitOutTime"], errors="coerce").apply(format_timedelta2)
# df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").apply(format_timedelta2)
# Convertir a timedelta y luego a segundos
df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)

# Manejo de valores nulos para columnas categóricas
df["Compound"] = df["Compound"].fillna("TBD")
df["RaceName"] = df["RaceName"].fillna("GP")  
df["Season"] = df["Season"].fillna(0).astype(int)  

df["LapNumber"] = df["LapNumber"].fillna(0).astype(int)
df["DriverNumber"] = df["DriverNumber"].fillna(0).astype(int)
df["FinishingPosition"] = df["FinishingPosition"].fillna(0).astype(int)
df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
# df["IsPersonalBest"] = df["IsPersonalBest"].apply(lambda x: bool(x) if pd.notna(x) else False)
df["IsPersonalBest"] = df["IsPersonalBest"].apply(lambda x: 1 if x else 0)

df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").dt.total_seconds().fillna(0)

df = pd.get_dummies(df, columns=["Compound"], prefix="Compound")
     
        
# 📌 Entrenar Prophet para cada piloto
predictions = {}

for driver in df["Driver"].unique():
    extra_cols = [
    "PitStopDuration", "GridPosition",
    "LapTime", "Sector1Time", "Sector2Time", "Sector3Time",
    "IsPersonalBest"
    ] + [col for col in df.columns if col.startswith("Compound_")]

    columns_needed = ["ds", "y"] + extra_cols
    driver_data = df[df["Driver"] == driver][columns_needed].copy()

    if len(driver_data) < 2:
        print(f"⚠️ {driver} tiene menos de 2 vueltas registradas. No se generarán predicciones.")
        continue

    # Crear y configurar el modelo Prophet
    model = Prophet()

    # Añadir regresores
    for reg in extra_cols:
        model.add_regressor(reg)

    # Ajustar modelo
    model.fit(driver_data)

    # Crear el dataframe de predicción (con vueltas futuras)
    future = model.make_future_dataframe(periods=5, freq="min")

    # Unir el future con los regresores disponibles
    future = future.merge(driver_data[["ds"] + extra_cols], on="ds", how="left")

    # Rellenar NaNs en vueltas futuras con 0
    future[extra_cols] = future[extra_cols].fillna(0)

    # Predecir
    forecast = model.predict(future)

    # Guardar predicciones
    predictions[driver] = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

# 📌 Calcular métricas de error (RMSE, MAE) para cada piloto
metrics = {}

for driver, forecast in predictions.items():
    # Obtener los datos reales
    actual_data = df[df["Driver"] == driver][["ds", "y"]]

    # Juntar predicciones con valores reales (inner join para asegurar coincidencia de vueltas)
    merged = actual_data.merge(forecast, on="ds", how="inner")

    if merged.empty:
        print(f"⚠️ No hay datos reales para evaluar a {driver}.")
        continue

    # Calcular métricas
    rmse = np.sqrt(mean_squared_error(merged["y"], merged["yhat"]))
    mae = mean_absolute_error(merged["y"], merged["yhat"])

    # Guardar métricas
    metrics[driver] = {"RMSE": rmse, "MAE": mae}

# 📌 Convertir a DataFrame y mostrar
metrics_df = pd.DataFrame.from_dict(metrics, orient="index")

# 📌 Mostrar resultados
print("\n📊 Métricas de Predicción (Prophet) por Piloto:")
print(metrics_df)

# 📌 Guardar en CSV si quieres analizarlo después
metrics_df.to_csv("prophet_metrics1_4.csv")
print("\n✅ Métricas guardadas en 'prophet_metrics.csv'")


# 📌 Visualizar las predicciones
plt.figure(figsize=(10, 6))

for driver, forecast in predictions.items():
    actual_data = df[df["Driver"] == driver]
    plt.plot(actual_data["ds"], actual_data["y"], marker="o", linestyle="-", label=f"{driver} (Histórico)")
    plt.plot(forecast["ds"], forecast["yhat"], linestyle="--", label=f"{driver} (Predicción)")

plt.gca().invert_yaxis()  # Invertimos el eje para que la posición 1 esté arriba
plt.xlabel("Tiempo (minutos desde el inicio)")
plt.ylabel("Posición")
plt.title("Predicción de Posiciones con Prophet")
plt.legend()
plt.grid(True)
plt.show()
