from prediction_model.randomFRegressorModel.visualize_prediction import visualizar_orden_real_vs_predicho
import pandas as pd
import numpy as np
import joblib
import os

def load_model(path=None, circuit="SPA"):
    if path is None:
        # path = os.path.join(os.path.dirname(__file__), f"rf_model_{circuit.upper()}.pkl")
        path = os.path.join(os.path.dirname(__file__), "rf_model.pkl")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"⚠️ El modelo no se encontró en: {path}")
    
    return joblib.load(path)

def load_and_prepare_vuelta(df, lap_number):
    df_vuelta = df[df["LapNumber"] == lap_number].copy()

    df_vuelta["LapTime"] = pd.to_timedelta(df_vuelta["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
    df_vuelta["PitStopDuration"] = pd.to_timedelta(df_vuelta["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)
    df_vuelta["GridPosition"] = df_vuelta["GridPosition"].fillna(0).astype(int)
    df_vuelta["Position"] = df_vuelta["Position"].fillna(0).astype(int)
    df_vuelta["IsPersonalBest"] = df_vuelta["IsPersonalBest"].fillna("No")
    df_vuelta["IsPersonalBest"] = df_vuelta["IsPersonalBest"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

    df_vuelta = df_vuelta.rename(columns={
        "LapTime": "LapTime_curr",
        "Compound": "Compound_curr",
        "IsPersonalBest": "IsPersonalBest_curr",
        "Position": "Position_curr",
        "PitStopDuration": "PitStopDuration_curr",
        "GridPosition": "GridPosition_curr"
    })

    df_vuelta = pd.get_dummies(df_vuelta, columns=["Compound_curr"], prefix="Compound")

    return df_vuelta

def predecir_vuelta(modelo, df_vuelta):
    for col in modelo.feature_names_in_:
        if col not in df_vuelta.columns:
            df_vuelta[col] = 0

    df_features = df_vuelta[modelo.feature_names_in_]
    pred = modelo.predict(df_features)

    # df_vuelta["PredictedPosition"] = pred.round().astype(int)
    df_vuelta["PredictedPosition"] = pred
    # df_vuelta["PredictedPosition"] = np.floor(pred).astype(int)
    df_vuelta["PredictedRank"] = df_vuelta["PredictedPosition"].rank(method="first")
    return df_vuelta.sort_values("PredictedRank")


