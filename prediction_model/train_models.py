# from sklearn.ensemble import RandomForestRegressor
# from catboost import CatBoostRegressor, Pool
from xgboost import XGBRegressor

from feature_engineering import preparar_dataset_vuelta_a_vuelta

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pandas as pd
import joblib
import os


CIRCUIT_INFO = {
    "MONACO": {
        "TotalLaps": 78,
        "IsStreetCircuit": 1,
        "TrackLengthKm": 3.34,
        "CornersCount": 19,
        "PitLossSeconds": 20
    },
    "SPA": {
        "TotalLaps": 44,
        "IsStreetCircuit": 0,
        "TrackLengthKm": 7.00,
        "CornersCount": 20,
        "PitLossSeconds": 22
    },
    "MONZA": {
        "TotalLaps": 53,
        "IsStreetCircuit": 0,
        "TrackLengthKm": 5.79,
        "CornersCount": 11,
        "PitLossSeconds": 18
    },
    "SAOPAULO": {
        "TotalLaps": 71,
        "IsStreetCircuit": 0,
        "TrackLengthKm": 4.31,
        "CornersCount": 15,
        "PitLossSeconds": 21
    },
}


def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds().fillna(0)
    df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").dt.total_seconds().fillna(0)
    df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
    df["Position"] = df["Position"].fillna(0).astype(int)
    df["IsPersonalBest"] = df["IsPersonalBest"].fillna("No")
    return df

def cargar_datos_circuito_excluyendo_anio(circuit, anio_excluir):
    df_total = []

    for year in ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
        if year == anio_excluir:
            continue

        filepath = f"../{circuit}_DATA/full_data_race/{circuit}_{year}_full_H_data.csv"
        try:
            raw_df = load_and_clean_data(filepath)
            raw_df["Circuit"] = circuit

            circuit_features = CIRCUIT_INFO[circuit]
            for key, value in circuit_features.items():
                raw_df[key] = value

            df_total.append(raw_df)
        except FileNotFoundError:
            print(f"Archivo no encontrado: {filepath}")
            continue

    if not df_total:
        raise ValueError(f"No se encontraron datos para el circuito {circuit} excluyendo el año {anio_excluir}.")

    raw_df_combined = pd.concat(df_total, ignore_index=True)
    return raw_df_combined

# def entrenar_modelo_rf(df, circuit, year):
#     save_path= f"./rf_model{circuit}_{year}.pkl"
#     X = df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y = df["Position_next"]

#     # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     pilotos_unicos = df["Driver"].unique()
#     train_pilots, test_pilots = train_test_split(pilotos_unicos, test_size=0.2, random_state=42)

#     train_df = df[df["Driver"].isin(train_pilots)]
#     test_df = df[df["Driver"].isin(test_pilots)]

#     X_train = train_df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y_train = train_df["Position_next"]
#     X_test = test_df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y_test = test_df["Position_next"]

#     modelo = RandomForestRegressor(n_estimators=100, random_state=42)
#     modelo.fit(X_train, y_train)

#     y_pred = modelo.predict(X_test)
#     mae = mean_absolute_error(y_test, y_pred)
#     print(f"MAE en test: {mae:.2f}")

#     joblib.dump(modelo, save_path)
#     print(f"Modelo guardado en {save_path}")

# def entrenar_modelo_rf_global(df, nombre_modelo="GLOBAL"):
#     save_path = f"./rf_model_{nombre_modelo}.pkl"

#     # Muestreo para acelerar prueba (usar 1.0 para todo el dataset)
#     df_sample = df.sample(frac=0.3, random_state=42)

#     # Separación por piloto (para evitar data leakage)
#     pilotos_unicos = df_sample["Driver"].unique()
#     train_pilots, test_pilots = train_test_split(pilotos_unicos, test_size=0.2, random_state=42)

#     train_df = df_sample[df_sample["Driver"].isin(train_pilots)]
#     test_df = df_sample[df_sample["Driver"].isin(test_pilots)]

#     X_train = train_df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y_train = train_df["Position_next"]
#     X_test = test_df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y_test = test_df["Position_next"]

#     # Modelo optimizado para rendimiento
#     modelo = RandomForestRegressor(
#         n_estimators=50,        # menor cantidad de árboles
#         max_depth=12,           # control de profundidad
#         random_state=42,
#         n_jobs=-1               # usa todos los núcleos del procesador
#     )

#     modelo.fit(X_train, y_train)

#     y_pred = modelo.predict(X_test)
#     mae = mean_absolute_error(y_test, y_pred)
#     print(f"MAE en test (RandomForest Global - muestra 30%): {mae:.2f}")

#     joblib.dump(modelo, save_path)
#     print(f"Modelo guardado en {save_path}")

# def entrenar_modelo_catboost(df, nombre_modelo="CATBOOST_GLOBAL"):
#     save_path = f"./catboost_model_{nombre_modelo}.cbm"

#     # Separación por piloto para evitar data leakage
#     pilotos_unicos = df["Driver"].unique()
#     train_pilots, test_pilots = train_test_split(pilotos_unicos, test_size=0.2, random_state=42)

#     train_df = df[df["Driver"].isin(train_pilots)]
#     test_df = df[df["Driver"].isin(test_pilots)]

#     # Separar features y target
#     X_train = train_df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y_train = train_df["Position_next"]
#     X_test = test_df.drop(columns=["Driver", "LapNumber", "Position_next"])
#     y_test = test_df["Position_next"]

#     # Detectar columnas categóricas automáticamente
#     categorical_cols = [col for col in X_train.columns if X_train[col].dtype == "object"]

#     # Crear pools para CatBoost
#     train_pool = Pool(data=X_train, label=y_train, cat_features=categorical_cols)
#     test_pool = Pool(data=X_test, label=y_test, cat_features=categorical_cols)

#     # Entrenar modelo
#     modelo = CatBoostRegressor(
#         iterations=300,
#         depth=8,
#         learning_rate=0.1,
#         loss_function="MAE",
#         verbose=0,
#         random_seed=42
#     )

#     modelo.fit(train_pool)

#     y_pred = modelo.predict(X_test)
#     mae = mean_absolute_error(y_test, y_pred)
#     print(f"MAE en test (CatBoost): {mae:.2f}")

#     modelo.save_model(save_path)
#     print(f"Modelo guardado en {save_path}")
    
def entrenar_modelo_xgb(df, circuit, year):
    save_path = f"./xgboostModel/xgb_model_{circuit}_sin_{year}.pkl"

    pilotos_unicos = df["Driver"].unique()
    train_pilots, test_pilots = train_test_split(pilotos_unicos, test_size=0.2, random_state=42)

    train_df = df[df["Driver"].isin(train_pilots)]
    test_df = df[df["Driver"].isin(test_pilots)]

    X_train = train_df.drop(columns=["Driver", "LapNumber", "Position_next"])
    y_train = train_df["Position_next"]
    X_test = test_df.drop(columns=["Driver", "LapNumber", "Position_next"])
    y_test = test_df["Position_next"]

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
    print(f"MAE en test (XGBoost): {mae:.2f}")

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
    # anio_a_excluir = ["2018", "2019", "2020", "2021", "2022", "2023"]
    anio_a_excluir = ["2024"]
    for circuito in circuito_objetivo:
        for año in anio_a_excluir: 
            nombre_archivo = f"./trainingData/{circuito}_sin_{año}.csv"

            if os.path.exists(nombre_archivo):
                print(f"Archivo ya existe: {nombre_archivo}. Cargando directamente.")
                raw_df = pd.read_csv(nombre_archivo)
            else:
                print(f"Generando archivo: {nombre_archivo}")
                raw_df = cargar_datos_circuito_excluyendo_anio(circuito, año)
                raw_df.to_csv(nombre_archivo, index=False)

            full_df = preparar_dataset_vuelta_a_vuelta(raw_df)
            full_df = pd.get_dummies(full_df, columns=["Circuit"], prefix="Circuit")

            entrenar_modelo_xgb(full_df, circuito, año)


    # entrenar_modelo_rf(full_df, "ALL_CIRCUITS", 2000)
    # entrenar_modelo_rf_global(full_df, nombre_modelo="ALLCIRCUITS_OPTIMIZED")
    # entrenar_modelo_catboost(full_df, nombre_modelo="Monaco_CATBOOST")

