import pandas as pd

def preparar_dataset_vuelta_a_vuelta(df):
    df = df.sort_values(by=["Driver", "LapNumber"]).copy()

    input_cols = ["Driver", "LapNumber", "LapTime", "Compound", "IsPersonalBest",
                  "Position", "PitStopDuration", "GridPosition"]

    current_lap = df[input_cols].copy()
    current_lap.rename(columns=lambda x: x if x in ["Driver", "LapNumber"] else f"{x}_curr", inplace=True)

    next_lap = df[["Driver", "LapNumber", "Position"]].copy()
    next_lap["LapNumber"] -= 1  # alineamos con la vuelta anterior
    next_lap.rename(columns={"Position": "Position_next"}, inplace=True)

    full = pd.merge(current_lap, next_lap, on=["Driver", "LapNumber"], how="inner")

    # Conversión de IsPersonalBest a binario
    full["IsPersonalBest_curr"] = full["IsPersonalBest_curr"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

    # One-hot encoding para Compound
    full = pd.get_dummies(full, columns=["Compound_curr"], prefix="Compound")

    return full.dropna()
