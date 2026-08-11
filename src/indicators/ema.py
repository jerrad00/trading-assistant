def calculate_ema(data, period=20):
    return data["Close"].ewm(span=period, adjust=False).mean()