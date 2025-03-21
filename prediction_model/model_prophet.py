import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import plotly.graph_objects as go

# Cargar los datos
data = "../SPA_DATA/full_data_race/SPA_2022_full_H_data.csv"
df = pd.read_csv(data)


df["ds"] = df["LapNumber"].apply(lambda x: datetime(2024, 1, 1) + timedelta(minutes=int(x)))
df["y"] = df["Position"].fillna(0).astype(int)  # Prophet espera una columna 'y' numérica

df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").dt.total_seconds().fillna(0)
df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").dt.total_seconds().fillna(0)
df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").dt.total_seconds().fillna(0)

# df["PitInTime"] = pd.to_timedelta(df["PitInTime"], errors="coerce").apply(format_timedelta2)
# df["PitOutTime"] = pd.to_timedelta(df["PitOutTime"], errors="coerce").apply(format_timedelta2)
df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)

# df["RaceName"] = df["RaceName"].fillna("GP")  
# df["Season"] = df["Season"].fillna(0).astype(int)  

df["LapNumber"] = df["LapNumber"].fillna(0).astype(int)
# df["DriverNumber"] = df["DriverNumber"].fillna(0).astype(int)
# df["FinishingPosition"] = df["FinishingPosition"].fillna(0).astype(int)
df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
df["IsPersonalBest"] = df["IsPersonalBest"].apply(lambda x: 1 if x else 0)

df["Compound"] = df["Compound"].fillna("TBD")
df = pd.get_dummies(df, columns=["Compound"], prefix="Compound")
     
        
#  Entrenar Prophet para cada piloto
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

###################################
    # Crear y configurar el modelo Prophet
    model = Prophet()

    # Añadir regresores
    for reg in extra_cols:
        model.add_regressor(reg)
    model.fit(driver_data)
    future = model.make_future_dataframe(periods=5, freq="min")
    future = future.merge(driver_data[["ds"] + extra_cols], on="ds", how="left")
    future[extra_cols] = future[extra_cols].fillna(0)
    forecast = model.predict(future)
    predictions[driver] = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

#  Calcular métricas de error (RMSE, MAE) para cada piloto
# metrics = {}

# for driver, forecast in predictions.items():
#     actual_data = df[df["Driver"] == driver][["ds", "y"]]
#     merged = actual_data.merge(forecast, on="ds", how="inner")

#     if merged.empty:
#         print(f"No hay datos reales para evaluar a {driver}.")
#         continue
#     rmse = np.sqrt(mean_squared_error(merged["y"], merged["yhat"]))
#     mae = mean_absolute_error(merged["y"], merged["yhat"])

#     metrics[driver] = {"RMSE": rmse, "MAE": mae}

# metrics_df = pd.DataFrame.from_dict(metrics, orient="index")
# print("\n Métricas de Predicción (Prophet) por Piloto:")
# print(metrics_df)
# metrics_df.to_csv("prophet_metrics1_4.csv")
# print("\n Métricas guardadas en 'prophet_metrics.csv'")


# Visualizar las predicciones
# plt.figure(figsize=(10, 6))

# for driver, forecast in predictions.items():
#     actual_data = df[df["Driver"] == driver]
#     plt.plot(actual_data["ds"], actual_data["y"], marker="o", linestyle="-", label=f"{driver} (Histórico)")
#     plt.plot(forecast["ds"], forecast["yhat"], linestyle="--", label=f"{driver} (Predicción)")

# plt.gca().invert_yaxis()  # Invertimos el eje para que la posición 1 esté arriba
# plt.xlabel("Tiempo (minutos desde el inicio)")
# plt.ylabel("Posición")
# plt.title("Predicción de Posiciones con Prophet")
# plt.legend()
# plt.grid(True)
# plt.show()


# for driver, forecast in predictions.items():
#     actual = df[df["Driver"] == driver]
#     forecast = predictions[driver]

#     plt.figure(figsize=(10, 5))
#     plt.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], alpha=0.2, label="Rango de confianza")
#     plt.plot(actual["ds"], actual["y"], marker="o", label="Real", linewidth=2)
#     plt.plot(forecast["ds"], forecast["yhat"], linestyle="--", label="Predicción", linewidth=2)
#     plt.title(f"Predicción vs Real: {driver}")
#     plt.xlabel("Tiempo")
#     plt.ylabel("Posición")
#     plt.gca().invert_yaxis()
#     plt.legend()
#     plt.grid(True)
#     plt.show()


# for driver, forecast in predictions.items():
#     actual = df[df["Driver"] == driver]
#     forecast = predictions[driver]

#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=actual["ds"], y=actual["y"], mode='lines+markers', name='Real'))
#     fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], mode='lines', name='Predicción'))
#     fig.update_yaxes(autorange="reversed", title="Posición")
#     fig.update_layout(title=f"Predicción Interactiva - {driver}", xaxis_title="Vuelta/Tiempo")
#     fig.show()
