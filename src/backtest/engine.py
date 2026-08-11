def run_backtest(data, initial_capital=10000):
    capital = initial_capital
    position = 0
    entry_price = 0

    trades = []

    for index, row in data.iterrows():
        price = float(row["Close"])
        signal = row["Signal"]

        # ورود به معامله
        if signal == "BUY" and position == 0:
            position = capital / price
            entry_price = price
            capital = 0

            trades.append({
                "date": index,
                "type": "BUY",
                "price": price
            })

        # خروج از معامله
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

    # اگر معامله هنوز باز باشد، در آخرین قیمت می‌بندیم
    if position > 0:
        final_price = float(data.iloc[-1]["Close"])
        capital = position * final_price

        profit = (final_price - entry_price) * position

        trades.append({
            "date": data.index[-1],
            "type": "SELL",
            "price": final_price,
            "profit": profit
        })

    return capital, trades


def calculate_statistics(initial_capital, final_capital, trades):
    sell_trades = [
        trade for trade in trades
        if trade["type"] == "SELL"
    ]

    total_trades = len(sell_trades)

    winning_trades = [
        trade for trade in sell_trades
        if trade["profit"] > 0
    ]

    losing_trades = [
        trade for trade in sell_trades
        if trade["profit"] <= 0
    ]

    total_profit = final_capital - initial_capital

    if initial_capital > 0:
        total_return = (total_profit / initial_capital) * 100
    else:
        total_return = 0

    if total_trades > 0:
        win_rate = (len(winning_trades) / total_trades) * 100
    else:
        win_rate = 0

    return {
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        "total_profit": total_profit,
        "total_return": total_return,
        "total_trades": total_trades,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate": win_rate
    }