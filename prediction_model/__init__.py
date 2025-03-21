from prediction_model.preprocessing import preprocess_dataframe
from prediction_model.prophet_model import train_prophet_for_driver, predict_with_prophet
from prediction_model.evaluation import evaluate_predictions

df = pd.read_csv("ruta/a/archivo.csv")
df = preprocess_dataframe(df)

resultados = {}

for driver in df["Driver"].unique():
    # preparar columnas
    extra_cols = ["PitStopDuration", "GridPosition", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "IsPersonalBest"] + \
        [col for col in df.columns if col.startswith("Compound_")]
    
    columnas = ["ds", "y"] + extra_cols
    driver_data = df[df["Driver"] == driver][columnas].copy()

    if len(driver_data) < 2:
        continue

    model = train_prophet_for_driver(driver_data, extra_cols)
    forecast = predict_with_prophet(model, driver_data, extra_cols)
    rmse, mae = evaluate_predictions(driver_data[["ds", "y"]], forecast)
    
    resultados[driver] = {"RMSE": rmse, "MAE": mae}
