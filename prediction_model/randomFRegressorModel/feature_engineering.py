import pandas as pd

def preparar_dataset_vuelta_a_vuelta(df):
    df = df.sort_values(by=["Driver", "LapNumber"]).copy()

    # --- Mapeo de circuito para conservarlo al final ---
    if "Circuit" in df.columns:
        circuit_map = df[["Driver", "LapNumber", "Circuit"]].copy()
    else:
        circuit_map = None

    # --- Convertir columnas de tiempo a timedelta ---
    time_columns = ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "PitInTime", "PitOutTime", "PitStopDuration"]
    for col in time_columns:
        if col in df.columns:
            df[col] = pd.to_timedelta(df[col], errors="coerce")

    # --- Convertir a segundos ---
    df["LapTime_seconds"] = df["LapTime"].dt.total_seconds()
    df["PitStopDuration_seconds"] = df["PitStopDuration"].dt.total_seconds()
    df["PitInTime_seconds"] = df["PitInTime"].dt.total_seconds()
    df["PitOutTime_seconds"] = df["PitOutTime"].dt.total_seconds()

    # --- Feature 1: Promedio de tiempo de vuelta de todos los pilotos en esa vuelta ---
    df["AvgLapTime_all_currLap"] = df.groupby("LapNumber")["LapTime_seconds"].transform("mean")

    # --- Feature 2: Número de pilotos que pararon en boxes en esa vuelta ---
    df["PitInTime_flag"] = df["PitInTime"].notnull().astype(int)
    df["NumPitStops_currLap"] = df.groupby("LapNumber")["PitInTime_flag"].transform("sum")

    # --- Feature 3: Compuestos usados en esa vuelta ---
    compound_dummies = pd.get_dummies(df["Compound"])
    compound_counts = compound_dummies.copy()
    compound_counts["LapNumber"] = df["LapNumber"]
    compound_counts = compound_counts.groupby("LapNumber").transform("sum")
    compound_counts.columns = [f"Compound_count_curr_{col}" for col in compound_counts.columns]
    df = pd.concat([df, compound_counts], axis=1)

    # --- Feature 4: Delta de posición ---
    df["DeltaPosition"] = df.groupby("Driver")["Position"].diff()

    # --- Opcional: rolling mean de lap time (últimas 3 vueltas) ---
    df["RollingLapTime_3"] = (
        df.groupby("Driver")["LapTime_seconds"]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    # --- Selección de columnas de entrada ---
    input_cols = [
        "Driver", "LapNumber", "LapTime_seconds", "Compound", "IsPersonalBest",
        "Position", "PitStopDuration_seconds", "GridPosition",
        "AvgLapTime_all_currLap", "NumPitStops_currLap", "DeltaPosition", "RollingLapTime_3"
    ] + list(compound_counts.columns)

    current_lap = df[input_cols].copy()
    current_lap.rename(columns=lambda x: x if x in ["Driver", "LapNumber"] else f"{x}_curr", inplace=True)

    # --- Posición en la vuelta siguiente ---
    next_lap = df[["Driver", "LapNumber", "Position"]].copy()
    next_lap["LapNumber"] -= 1
    next_lap.rename(columns={"Position": "Position_next"}, inplace=True)

    # --- Merge de la vuelta actual con la siguiente ---
    full = pd.merge(current_lap, next_lap, on=["Driver", "LapNumber"], how="inner")

    # --- Binario para IsPersonalBest ---
    full["IsPersonalBest_curr"] = full["IsPersonalBest_curr"].apply(lambda x: 1 if str(x).lower() in ["yes", "true", "1"] else 0)

    # --- One-hot encoding del compuesto actual ---
    full = pd.get_dummies(full, columns=["Compound_curr"], prefix="Compound")

    # --- Reincorporar nombre del circuito ---
    if circuit_map is not None:
        full = pd.merge(full, circuit_map, on=["Driver", "LapNumber"], how="left")

    # --- Reincorporar contexto físico del circuito ---
    context_cols = ["TotalLaps", "IsStreetCircuit", "TrackLengthKm", "CornersCount", "PitLossSeconds"]
    if all(col in df.columns for col in context_cols):
        context_data = df[["Driver", "LapNumber"] + context_cols].drop_duplicates()
    full = pd.merge(full, context_data, on=["Driver", "LapNumber"], how="left")


    return full.dropna()
