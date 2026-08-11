def run_backtest(data, initial_capital=10000):
    capital = initial_capital
    position = 0
    entry_price = 0

    trades = []
    equity_curve = []

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

        # ارزش فعلی حساب
        if position > 0:
            equity = position * price
        else:
            equity = capital

        equity_curve.append({
            "date": index,
            "equity": equity
        })

    # بستن معامله باز در آخرین قیمت
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

    return capital, trades, equity_curve


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

    total_return = (
        total_profit / initial_capital
    ) * 100

    if total_trades > 0:
        win_rate = (
            len(winning_trades) / total_trades
        ) * 100
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


def calculate_max_drawdown(equity_curve):
    peak = equity_curve[0]["equity"]
    max_drawdown = 0

    for point in equity_curve:
        equity = point["equity"]

        if equity > peak:
            peak = equity

        drawdown = ((equity - peak) / peak) * 100

        if drawdown < max_drawdown:
            max_drawdown = drawdown

    return max_drawdown