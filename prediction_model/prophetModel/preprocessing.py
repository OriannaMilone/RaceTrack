import pandas as pd
from datetime import datetime, timedelta


def preprocess_dataframe(df):
    # df["ds"] = pd.to_datetime(df["LapNumber"].apply(lambda x: f"2024-01-01 {int(x)}:00:00"))
    df["ds"] = df["LapNumber"].apply(lambda x: datetime(2024, 1, 1) + timedelta(minutes=int(x)))
    df["y"] = df["Position"].fillna(0).astype(int)
    
    for col in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "PitStopDuration"]:
        df[col] = pd.to_timedelta(df[col], errors="coerce").dt.total_seconds().fillna(0)

    df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
    df["IsPersonalBest"] = df["IsPersonalBest"].apply(lambda x: 1 if pd.notna(x) and x else 0)
    
    df["Compound"] = df["Compound"].fillna("TBD")
    df = pd.get_dummies(df, columns=["Compound"], prefix="Compound")

    return df
