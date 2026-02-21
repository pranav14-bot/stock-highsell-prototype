import pandas as pd

def add_entry_signal(df: pd.DataFrame, buy_edge: float) -> pd.DataFrame:
    df = df.copy()
    df["enter_long"] = df["pred_high"] >= df["Close"] * (1 + buy_edge)
    return df