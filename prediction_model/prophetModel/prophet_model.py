from prophet import Prophet

def train_prophet_for_driver(driver_data, extra_cols):
    model = Prophet()
    for col in extra_cols:
        model.add_regressor(col) # Añadir regresores
    model.fit(driver_data) 
    return model

def predict_with_prophet(model, driver_data, extra_cols, n_future=5):
    future = model.make_future_dataframe(periods=n_future, freq="min")
    future = future.merge(driver_data[["ds"] + extra_cols], on="ds", how="left")
    future[extra_cols] = future[extra_cols].fillna(0)
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
