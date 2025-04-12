import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# from prediction_model.randomFRegressorModel.feature_engineering import preparar_dataset_vuelta_a_vuelta
from feature_engineering import preparar_dataset_vuelta_a_vuelta

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
    df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)
    df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
    df["Position"] = df["Position"].fillna(0).astype(int)
    df["IsPersonalBest"] = df["IsPersonalBest"].fillna("No")
    return df

def entrenar_modelo_rf(df, save_path="./rf_model.pkl"):
    X = df.drop(columns=["Driver", "LapNumber", "Position_next"])
    y = df["Position_next"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE en test: {mae:.2f}")

    joblib.dump(modelo, save_path)
    print(f"Modelo guardado en {save_path}")

if __name__ == "__main__":
    filepath = "../../SPA_DATA/full_data_race/SPA_2018_full_H_data.csv"
    raw_df = load_and_clean_data(filepath)
    full_df = preparar_dataset_vuelta_a_vuelta(raw_df)
    entrenar_modelo_rf(full_df)
