# src/data_pull.py

import os
import yfinance as yf
from tickers import get_default_tickers


def pull_data(ticker: str):
    print(f"\nPulling {ticker}...")

    df = yf.download(ticker, period="max", interval="1d")

    if df.empty:
        print(f"No data for {ticker}")
        return

    # it forces the Date index into a real "Date" column
    df = df.reset_index()

    # (optional) clean column names
    df.columns = [str(c).strip() for c in df.columns]

    # save to project-root /data no matter where we run from
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    out_path = os.path.join(data_dir, f"{ticker}_daily.csv")

    df.to_csv(out_path, index=False)

    print(f"Saved {ticker}: {len(df)} rows -> {out_path}")


def main():
    tickers = get_default_tickers()

    print("Available tickers:")
    print(", ".join(tickers))

    for t in tickers:
        pull_data(t)


if __name__ == "__main__":
    main()