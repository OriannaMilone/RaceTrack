import pandas as pd
from prediction_model.predict_next_lap import *

def predecir_siguiente_vuelta(df_vuelta: pd.DataFrame, modelo=None):
    """
    Recibe un DataFrame con los datos de una vuelta y devuelve el DataFrame con la predicción.
    """
    if modelo is None:
        modelo = load_model()

    df_preparado = load_and_prepare_vuelta(df_vuelta, df_vuelta["LapNumber"].iloc[0])
    if df_preparado.empty:
        print("⚠️ No se pudieron preparar los datos para esta vuelta.")
        return pd.DataFrame()

    return predecir_vuelta(modelo, df_preparado)
