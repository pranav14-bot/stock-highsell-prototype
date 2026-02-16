import yfinance as yf
import pandas as pd

ticker = "AAPL"

df = yf.download(ticker, start="2012-01-01", auto_adjust=False)

# Keep only these columns
df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

# Make Date a real column (not index) so CSV is simple
df = df.reset_index()

# Force simple column names (no multi-header)
df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

# Save clean CSV
out_path = "data/aapl_data.csv"
df.to_csv(out_path, index=False)

print(f"Saved clean CSV to {out_path}")
print(df.head())



