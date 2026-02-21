import pandas as pd

def backtest_long_sl_tp(df: pd.DataFrame, stop_loss: float, take_profit: float):
    close = df["Close"].astype(float).to_numpy()
    high  = df["High"].astype(float).to_numpy()
    low   = df["Low"].astype(float).to_numpy()
    dates = df.index.to_numpy()
    enter = df["enter_long"].to_numpy()

    position = 0
    entry_price = 0.0
    entry_date = None

    cash = 0.0
    trade_pnls = []
    trades = []  # completed trades only

    for i in range(len(df)):
        c = close[i]
        h = high[i]
        l = low[i]
        d = pd.Timestamp(dates[i])

        if position == 0:
            if enter[i]:
                position = 1
                entry_price = c
                entry_date = d
            continue

        # position == 1
        stop_price = entry_price * (1 - stop_loss)
        tp_price   = entry_price * (1 + take_profit)

        if l <= stop_price:
            exit_price = stop_price
            pnl = exit_price - entry_price
            cash += pnl
            trade_pnls.append(pnl)
            trades.append({
                "entry_date": entry_date, "entry_price": entry_price,
                "exit_date": d, "exit_price": exit_price,
                "exit_reason": "STOP", "pnl": pnl
            })
            position = 0
            entry_price = 0.0
            entry_date = None
            continue

        if h >= tp_price:
            exit_price = tp_price
            pnl = exit_price - entry_price
            cash += pnl
            trade_pnls.append(pnl)
            trades.append({
                "entry_date": entry_date, "entry_price": entry_price,
                "exit_date": d, "exit_price": exit_price,
                "exit_reason": "TP", "pnl": pnl
            })
            position = 0
            entry_price = 0.0
            entry_date = None
            continue

    # exit at end
    if position == 1:
        d = pd.Timestamp(dates[-1])
        exit_price = close[-1]
        pnl = exit_price - entry_price
        cash += pnl
        trade_pnls.append(pnl)
        trades.append({
            "entry_date": entry_date, "entry_price": entry_price,
            "exit_date": d, "exit_price": exit_price,
            "exit_reason": "END", "pnl": pnl
        })

    num_trades = len(trade_pnls)
    win_rate = (sum(1 for x in trade_pnls if x > 0) / num_trades) if num_trades else 0.0
    avg_pnl = (sum(trade_pnls) / num_trades) if num_trades else 0.0

    return {
        "pnl": cash,
        "num_trades": num_trades,
        "win_rate": win_rate,
        "avg_pnl": avg_pnl,
        "trades": trades
    }