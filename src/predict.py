import numpy as np
import pandas as pd

def add_momentum_predictions(df: pd.DataFrame, lookback: int = 20, vol_lookback: int = 20) -> pd.DataFrame:
    """
    Baseline predictor:
    - uses recent momentum to estimate next day's expected move
    - uses rolling volatility to size the prediction (and avoid crazy forecasts)
    Produces: pred_high, pred_low, pred_close
    """
    out = df.copy()

    close = out["Close"].astype(float)

    # daily returns
    ret = close.pct_change()

    # momentum = average return over lookback
    mom = ret.rolling(lookback).mean()

    # volatility = std dev of returns
    vol = ret.rolling(vol_lookback).std()

    # cap extreme values (keeps predictions sane)
    mom = mom.clip(-0.01, 0.01)          # +/-1% avg daily drift cap
    vol = vol.clip(0.002, 0.05)          # 0.2% to 5% daily vol cap

    # expected move magnitude (use vol)
    move = vol.fillna(vol.median())

    # predictions
    out["pred_close"] = close * (1 + mom.fillna(0))
    out["pred_high"]  = close * (1 + mom.fillna(0) + 1.0 * move)
    out["pred_low"]   = close * (1 + mom.fillna(0) - 1.0 * move)

    return out