import pandas as pd
import numpy as np
np.random.seed(42)

TICKER = "AAPL"
CSV_PATH = "data/aapl_data.csv"

BUY_EDGE = 0.0375
STOP_LOSS = 0.03
TAKE_PROFIT = 0.04

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")



def fake_predict(row: pd.Series) -> dict:
    close = float(row["Close"])
    pred_high = close * (1 + np.random.uniform(0.0, 0.04))
    pred_low  = close * (1 - np.random.uniform(0.0, 0.04))
    pred_close = close * (1 + np.random.uniform(-0.02, 0.02))
    return {"pred_high": pred_high, "pred_low": pred_low, "pred_close": pred_close}

def backtest(df: pd.DataFrame) -> dict:
    position = 0
    entry_price = None
    cash = 0.0
    trades = []

    for date, row in df.iterrows():
        close = float(row["Close"])
        high = float(row["High"])
        low = float(row["Low"])

        preds = fake_predict(row)
        pred_high = preds["pred_high"]

        if position == 0 and pred_high >= close * (1 + BUY_EDGE):
            position = 1
            entry_price = close
            trades.append({"date": date, "action": "BUY", "price": close})
            continue

        if position == 1:
            if low <= entry_price * (1 - STOP_LOSS):
                exit_price = entry_price * (1 - STOP_LOSS)
                cash += (exit_price - entry_price)
                trades.append({"date": date, "action": "SELL_STOP", "price": exit_price})
                position = 0
                entry_price = None
                continue

            if high >= entry_price * (1 + TAKE_PROFIT):
                exit_price = entry_price * (1 + TAKE_PROFIT)
                cash += (exit_price - entry_price)
                trades.append({"date": date, "action": "SELL_TP", "price": exit_price})
                position = 0
                entry_price = None
                continue

    if position == 1 and entry_price is not None:
        last_close = float(df.iloc[-1]["Close"])
        cash += (last_close - entry_price)
        trades.append({"date": df.index[-1], "action": "SELL_END", "price": last_close})

    pnl = cash
    num_entries = sum(1 for t in trades if t["action"] == "BUY")
    return {"pnl": pnl, "trades": trades, "num_entries": num_entries}

def main():
    df = load_data(CSV_PATH).dropna()
    result = backtest(df)

    print(f"TICKER: {TICKER}")
    print(f"Entries: {result['num_entries']}")
    print(f"Total P&L (per 1 share): {result['pnl']:.2f}")
    print("\nLast actions:")
    for t in result["trades"][-10:]:
        print(t["date"].date(), t["action"], f"{t['price']:.2f}")

if __name__ == "__main__":
    main()
