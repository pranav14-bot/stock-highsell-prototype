# src/select_tickers.py

import os
import pandas as pd

from predict import add_momentum_predictions
from strategy import add_entry_signal
from backtest import backtest_long_sl_tp

TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA"]

BUY_EDGE = 0.0375
STOP_LOSS = 0.03
TAKE_PROFIT = 0.04

TOP_K = 2


def load_data(path: str) -> pd.DataFrame:
    import ast

    df = pd.read_csv(path)

    # First column = Date / Index
    first_col = df.columns[0]
    df[first_col] = pd.to_datetime(df[first_col], errors="coerce")
    df = df.set_index(first_col)

    # ✅ Flatten weird tuple columns
    new_cols = []
    for c in df.columns:
        s = str(c)

        if s.startswith("("):
            try:
                tup = ast.literal_eval(s)
                new_cols.append(str(tup[0]))  # Keep "Close"
            except:
                new_cols.append(s)
        else:
            new_cols.append(s)

    df.columns = new_cols

    # Convert numerics
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Open", "High", "Low", "Close"])

    return df


def evaluate_ticker(ticker: str) -> dict:
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"{ticker}_daily.csv"
    )

    try:
        df = load_data(csv_path)

        df = add_momentum_predictions(df, lookback=20, vol_lookback=20)
        df = add_entry_signal(df, buy_edge=BUY_EDGE)

        result = backtest_long_sl_tp(
            df,
            stop_loss=STOP_LOSS,
            take_profit=TAKE_PROFIT
        )

        pnl = result["pnl"]
        trades = int(result["num_trades"])
        avg_pnl = pnl / trades if trades > 0 else 0

    # win_rate may not be provided by your backtest; default to NaN
        win_rate = float(result.get("win_rate", float("nan")))

        print(f"{ticker}: pnl={pnl:.2f} trades={trades} win_rate={win_rate:.2%}")

        return {
            "ticker": ticker,
            "pnl": pnl,
            "num_trades": trades,
            "win_rate": win_rate,
            "avg_pnl": avg_pnl
        }

    except Exception as e:
        print(f"{ticker}: FAILED ({e})")
        return None


def main():
    rows = []

    for ticker in TICKERS:
        stats = evaluate_ticker(ticker)
        if stats:
            rows.append(stats)

    results = pd.DataFrame(rows)

    if results.empty:
        print("\nNo valid tickers.")
        return

    # ✅ SELECTION FILTER (EDIT THIS LOGIC)
    results = results[
        (results["num_trades"] >= 200) &
        (results["pnl"] > 0)
    ].copy()

    # Ranking
    results = results.sort_values(["pnl", "win_rate"], ascending=False)

    selected = results.head(TOP_K)["ticker"].tolist()

    results.to_csv("ticker_ranking.csv", index=False)

    print("\n=== RANKED TICKERS ===")
    print(results)

    print(f"\n✅ SELECTED (top {TOP_K}): {selected}")


if __name__ == "__main__":
    main()