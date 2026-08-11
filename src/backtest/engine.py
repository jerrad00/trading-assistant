def run_backtest(
    data,
    initial_capital=10000,
    fee_rate=0.001,
    stop_loss=0.02,
    take_profit=0.04
):
    capital = initial_capital
    position = 0
    entry_price = 0

    trades = []
    equity_curve = []

    for index, row in data.iterrows():
        price = float(row["Close"])
        signal = row["Signal"]

        # ورود به معامله
        if signal == "BUY" and position == 0:
            entry_fee = capital * fee_rate
            capital_after_fee = capital - entry_fee

            position = capital_after_fee / price
            entry_price = price
            capital = 0

            trades.append({
                "date": index,
                "type": "BUY",
                "price": price,
                "fee": entry_fee
            })

        # بررسی Stop Loss و Take Profit
        elif position > 0:

            stop_price = entry_price * (1 - stop_loss)
            target_price = entry_price * (1 + take_profit)

            if price <= stop_price:
                exit_value = position * price
                exit_fee = exit_value * fee_rate
                capital = exit_value - exit_fee

                profit = capital - initial_capital

                trades.append({
                    "date": index,
                    "type": "STOP LOSS",
                    "price": price,
                    "fee": exit_fee,
                    "profit": profit
                })

                position = 0
                entry_price = 0

            elif price >= target_price:
                exit_value = position * price
                exit_fee = exit_value * fee_rate
                capital = exit_value - exit_fee

                profit = capital - initial_capital

                trades.append({
                    "date": index,
                    "type": "TAKE PROFIT",
                    "price": price,
                    "fee": exit_fee,
                    "profit": profit
                })

                position = 0
                entry_price = 0

            elif signal == "SELL":
                exit_value = position * price
                exit_fee = exit_value * fee_rate
                capital = exit_value - exit_fee

                profit = capital - initial_capital

                trades.append({
                    "date": index,
                    "type": "SELL",
                    "price": price,
                    "fee": exit_fee,
                    "profit": profit
                })

                position = 0
                entry_price = 0

        # محاسبه ارزش فعلی حساب
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

        exit_value = position * final_price
        exit_fee = exit_value * fee_rate

        capital = exit_value - exit_fee

        trades.append({
            "date": data.index[-1],
            "type": "FINAL EXIT",
            "price": final_price,
            "fee": exit_fee,
            "profit": capital - initial_capital
        })

    return capital, trades, equity_curve


def calculate_statistics(initial_capital, final_capital, trades):
    completed_trades = [
        trade for trade in trades
        if trade["type"] in [
            "SELL",
            "STOP LOSS",
            "TAKE PROFIT",
            "FINAL EXIT"
        ]
    ]

    total_trades = len(completed_trades)

    winning_trades = [
        trade for trade in completed_trades
        if trade["profit"] > 0
    ]

    losing_trades = [
        trade for trade in completed_trades
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

    total_fees = sum(
        trade.get("fee", 0)
        for trade in trades
    )

    return {
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        "total_profit": total_profit,
        "total_return": total_return,
        "total_trades": total_trades,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate": win_rate,
        "total_fees": total_fees
    }


def calculate_max_drawdown(equity_curve):
    if not equity_curve:
        return 0

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
