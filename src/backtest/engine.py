def run_backtest(data, initial_capital=10000):
    capital = initial_capital
    position = 0
    entry_price = 0

    trades = []

    for index, row in data.iterrows():
        price = float(row["Close"])
        signal = row["Signal"]

        if signal == "BUY" and position == 0:
            position = capital / price
            entry_price = price
            capital = 0

            trades.append({
                "date": index,
                "type": "BUY",
                "price": price
            })

        elif signal == "SELL" and position > 0:
            capital = position * price

            profit = (price - entry_price) * position

            trades.append({
                "date": index,
                "type": "SELL",
                "price": price,
                "profit": profit
            })

            position = 0

    if position > 0:
        final_price = float(data.iloc[-1]["Close"])
        capital = position * final_price

    return capital, trades