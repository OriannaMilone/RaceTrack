from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def evaluate_predictions(actual_df, forecast_df):
    merged = actual_df.merge(forecast_df, on="ds", how="inner")
    rmse = np.sqrt(mean_squared_error(merged["y"], merged["yhat"]))
    mae = mean_absolute_error(merged["y"], merged["yhat"])
    return rmse, mae
