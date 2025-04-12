import argparse
import pandas as pd
from predict_next_lap import load_model, load_and_prepare_vuelta, predecir_vuelta
from visualize_prediction import visualizar_orden_real_vs_predicho

def main(lap_number):
    filepath = "../../SPA_DATA/full_data_race/SPA_2018_full_H_data.csv"
    
    df = pd.read_csv(filepath)
    modelo = load_model()
    
    df_vuelta = load_and_prepare_vuelta(df, lap_number)
    
    if df_vuelta.empty:
        print(f"No hay datos para la vuelta {lap_number}.")
        return

    df_pred = predecir_vuelta(modelo, df_vuelta)

    visualizar_orden_real_vs_predicho(df_pred)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predecir posiciones para la próxima vuelta.")
    parser.add_argument("--lap", type=int, required=True, help="Número de vuelta a utilizar como base para predecir la siguiente")
    args = parser.parse_args()

    main(args.lap)
