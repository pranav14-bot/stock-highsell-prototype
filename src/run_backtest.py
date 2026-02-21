import os
import pandas as pd

from predict import add_momentum_predictions
from strategy import add_entry_signal
from backtest import backtest_long_sl_tp

TICKER = "AAPL"

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "AAPL_daily.csv"
)

BUY_EDGE = 0.0375
STOP_LOSS = 0.03
TAKE_PROFIT = 0.04


def load_data(path: str) -> pd.DataFrame:
    import ast
    df = pd.read_csv(path)

    # first column is date-like, but header is weird
    first_col = df.columns[0]
    df[first_col] = pd.to_datetime(df[first_col], errors="coerce")
    df = df.set_index(first_col)

    # flatten columns: "('Close','AAPL')" -> Close
    new_cols = []
    for c in df.columns:
        s = str(c)
        s = s.replace('"', '').strip()
        if s.startswith("("):
            try:
                tup = ast.literal_eval(s.replace('"', ''))
                new_cols.append(str(tup[0]))
            except Exception:
                new_cols.append(s)
        else:
            new_cols.append(s)

    df.columns = new_cols

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    return df


def main():
    df = load_data(CSV_PATH)

    df = add_momentum_predictions(df, lookback=20, vol_lookback=20)
    df = add_entry_signal(df, buy_edge=BUY_EDGE)

    result = backtest_long_sl_tp(df, stop_loss=STOP_LOSS, take_profit=TAKE_PROFIT)

    print(f"TICKER: {TICKER}")
    print(f"Trades: {result['num_trades']}")
    print(f"Total P&L (per 1 share): {result['pnl']:.2f}")


if __name__ == "__main__":
    main()