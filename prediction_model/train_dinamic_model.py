from xgboost import XGBRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

import pandas as pd
import argparse
import joblib
import os

CIRCUIT_INFO = {
    "MONACO": {"TotalLaps": 78, "IsStreetCircuit": 1, "TrackLengthKm": 3.34, "CornersCount": 19, "PitLossSeconds": 20},
    "SPA": {"TotalLaps": 44, "IsStreetCircuit": 0, "TrackLengthKm": 7.00, "CornersCount": 20, "PitLossSeconds": 22},
    "MONZA": {"TotalLaps": 53, "IsStreetCircuit": 0, "TrackLengthKm": 5.79, "CornersCount": 11, "PitLossSeconds": 18},
    "SAOPAULO": {"TotalLaps": 71, "IsStreetCircuit": 0, "TrackLengthKm": 4.31, "CornersCount": 15, "PitLossSeconds": 21},
}

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
    df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)
    df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").dt.total_seconds().fillna(0)
    df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").dt.total_seconds().fillna(0)
    df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").dt.total_seconds().fillna(0)
    df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
    df["Position"] = df["Position"].fillna(0).astype(int)
    df["IsPersonalBest"] = df["IsPersonalBest"].fillna("No")
    return df

def preparar_dataset_con_sectores(df):
    df = df.sort_values(by=["Driver", "LapNumber"]).copy()
    input_cols = [
        "Driver", "LapNumber", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time",
        "Compound", "IsPersonalBest", "Position", "PitStopDuration", "GridPosition",
        "TotalLaps", "IsStreetCircuit", "TrackLengthKm", "CornersCount", "PitLossSeconds"
    ]
    current_lap = df[input_cols].copy()
    current_lap.rename(columns=lambda x: x if x in ["Driver", "LapNumber"] else f"{x}_curr", inplace=True)

    next_lap = df[["Driver", "LapNumber", "Position"]].copy()
    next_lap["LapNumber"] -= 1
    next_lap.rename(columns={"Position": "Position_next"}, inplace=True)

    full = pd.merge(current_lap, next_lap, on=["Driver", "LapNumber"], how="inner")
    full["IsPersonalBest_curr"] = full["IsPersonalBest_curr"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    full = pd.get_dummies(full, columns=["Compound_curr"], prefix="Compound")
    return full.dropna()

def cargar_datos_circuito_excluyendo_anio(circuit, anio_excluir):
    df_total = []
    for year in ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
        if year == anio_excluir:
            continue
        filepath = f"../{circuit}_DATA/full_data_race/{circuit}_{year}_full_H_data.csv"
        if not os.path.exists(filepath):
            print(f"Archivo no encontrado: {filepath}")
            continue
        df = load_and_clean_data(filepath)
        for key, value in CIRCUIT_INFO[circuit].items():
            df[key] = value
        df_total.append(df)
    if not df_total:
        raise ValueError(f"No se encontraron datos para el circuito {circuit} excluyendo el año {anio_excluir}.")
    return pd.concat(df_total, ignore_index=True)

def entrenar_modelo_xgb(df, circuit, anio_excluido):
    save_path = f"./xgboostModel/xgb_sectores_{circuit}_sin_{anio_excluido}.pkl"
    X = df.drop(columns=["Driver", "LapNumber", "Position_next"])
    y = df["Position_next"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective='reg:squarederror',
        random_state=42
    )
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"[{circuit} sin {anio_excluido}] MAE test (XGBoost con sectores): {mae:.2f}")

    joblib.dump(modelo, save_path)
    print(f"Modelo guardado en {save_path}")

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Entrenamiento modelo XGBoost por circuito excluyendo un año.")
    # parser.add_argument("--circuito", type=str, required=True, help="Nombre del circuito (ej: MONACO)")
    # parser.add_argument("--anio_excluir", type=str, required=True, help="Año a excluir del entrenamiento (ej: 2019)")
    
    # args = parser.parse_args()
    # circuito_objetivo = args.circuito.upper()
    # anio_a_excluir = args.anio_excluir
    circuito_objetivo = ["MONACO", "SPA", "MONZA", "SAOPAULO"]
    anio_a_excluir = ["2018", "2019", "2020", "2021", "2022", "2023"]
    for circuito in circuito_objetivo:
        for año in anio_a_excluir: 
            nombre_archivo = f"./trainingData/{circuito}_sin_{año}_sectores.csv"

            if os.path.exists(nombre_archivo):
                print(f"Archivo ya existe: {nombre_archivo}. Cargando directamente.")
                raw_df = pd.read_csv(nombre_archivo)
            else:
                print(f"Generando archivo: {nombre_archivo}")
                raw_df = cargar_datos_circuito_excluyendo_anio(circuito, año)
                raw_df.to_csv(nombre_archivo, index=False)

            full_df = preparar_dataset_con_sectores(raw_df)
            entrenar_modelo_xgb(full_df, circuito, año)
