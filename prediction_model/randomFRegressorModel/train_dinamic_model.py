import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)

    # Conversiones de tiempo a segundos
    df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
    df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)
    df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").dt.total_seconds().fillna(0)
    df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").dt.total_seconds().fillna(0)
    df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").dt.total_seconds().fillna(0)

    # Limpieza de otras columnas
    df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
    df["Position"] = df["Position"].fillna(0).astype(int)
    df["IsPersonalBest"] = df["IsPersonalBest"].fillna("No")

    return df

def preparar_dataset_con_sectores(df):
    df = df.sort_values(by=["Driver", "LapNumber"]).copy()

    input_cols = [
        "Driver", "LapNumber", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time",
        "Compound", "IsPersonalBest", "Position", "PitStopDuration", "GridPosition"
    ]

    current_lap = df[input_cols].copy()
    current_lap.rename(columns=lambda x: x if x in ["Driver", "LapNumber"] else f"{x}_curr", inplace=True)

    next_lap = df[["Driver", "LapNumber", "Position"]].copy()
    next_lap["LapNumber"] -= 1
    next_lap.rename(columns={"Position": "Position_next"}, inplace=True)

    full = pd.merge(current_lap, next_lap, on=["Driver", "LapNumber"], how="inner")

    # Conversión de IsPersonalBest a binario
    full["IsPersonalBest_curr"] = full["IsPersonalBest_curr"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

    # One-hot encoding para Compound
    full = pd.get_dummies(full, columns=["Compound_curr"], prefix="Compound")

    return full.dropna()

def entrenar_modelo_rf(df, circuit, year):
    save_path= f"./rf_model_sectors{circuit}_{year}.pkl"
    X = df.drop(columns=["Driver", "LapNumber", "Position_next"])
    y = df["Position_next"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE en test (con sectores): {mae:.2f}")

    joblib.dump(modelo, save_path)
    print(f"Modelo guardado en {save_path}")

if __name__ == "__main__":
    for circuit in ["SPA", "MONACO", "SAOPAULO", "MONZA"]:
        for year in ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
            filepath = f"../../{circuit}_DATA/full_data_race/{circuit}_{year}_full_H_data.csv"
            raw_df = load_and_clean_data(filepath)
            full_df = preparar_dataset_con_sectores(raw_df)
            entrenar_modelo_rf(full_df, circuit, year)
        
