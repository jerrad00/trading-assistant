def generate_signal(row):
    close = row["Close"]
    ema = row["EMA20"]
    rsi = row["RSI14"]

    if close > ema and rsi < 30:
        return "BUY"

    elif close < ema and rsi > 70:
        return "SELL"

    else:
        return "HOLD"