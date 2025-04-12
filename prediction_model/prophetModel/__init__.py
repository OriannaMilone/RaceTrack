from prediction_model.prophetModel.preprocessing import preprocess_dataframe
from prediction_model.prophetModel.prophet_model import train_prophet_for_driver, predict_with_prophet
from evaluation import evaluate_predictions
import pandas as pd
import matplotlib.pyplot as plt

 
df = pd.read_csv("../SPA_DATA/full_data_race/SPA_2022_full_H_data.csv")
df = preprocess_dataframe(df)

resultados = {}
predictions = {}
 
for driver in df["Driver"].unique():
    extra_cols = ["PitStopDuration", "GridPosition", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "IsPersonalBest"] + \
        [col for col in df.columns if col.startswith("Compound_")]
    
    columnas = ["ds", "y"] + extra_cols
    driver_data = df[df["Driver"] == driver][columnas].copy()

    if len(driver_data) < 2:
        print(f"{driver} tiene menos de 2 vueltas registradas. No se generarán predicciones.")
        continue

    model = train_prophet_for_driver(driver_data, extra_cols)
    forecast = predict_with_prophet(model, driver_data, extra_cols)
    
    predictions[driver] = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]    
    
    rmse, mae = evaluate_predictions(driver_data[["ds", "y"]], forecast)
    
    resultados[driver] = {"RMSE": rmse, "MAE": mae}


#Visualización de las predicciones
plt.figure(figsize=(10, 6))
for driver, forecast in predictions.items():
    actual_data = df[df["Driver"] == driver]
    plt.plot(actual_data["ds"], actual_data["y"], marker="o", linestyle="-", label=f"{driver} (Histórico)")
    plt.plot(forecast["ds"], forecast["yhat"], linestyle="--", label=f"{driver} (Predicción)")

    plt.gca().invert_yaxis() 
    plt.xlabel("Tiempo (minutos desde el inicio)")
    plt.ylabel("Posición")
    plt.title("Predicción de Posiciones con Prophet")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    
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
