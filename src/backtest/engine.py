def run_backtest(
    data,
    initial_capital=10000,
    fee_rate=0.001,
    stop_loss=0.02,
    take_profit=0.04,
    risk_per_trade=0.01
):
    capital = initial_capital
    position = 0
    entry_price = 0
    entry_value = 0
    entry_fee = 0

    trades = []
    equity_curve = []

    for index, row in data.iterrows():
        price = float(row["Close"])
        signal = row["Signal"]

        # =========================
        # ENTRY
        # =========================

        if signal == "BUY" and position == 0:

            risk_amount = capital * risk_per_trade

            stop_distance = price * stop_loss

            if stop_distance > 0:
                position = risk_amount / stop_distance
            else:
                position = 0

            entry_value = position * price
            entry_fee = entry_value * fee_rate

            total_entry_cost = entry_value + entry_fee

            # اگر حجم معامله بیشتر از سرمایه باشد
            if total_entry_cost > capital:
                entry_value = capital / (1 + fee_rate)

                position = entry_value / price

                entry_fee = entry_value * fee_rate

                total_entry_cost = (
                    entry_value + entry_fee
                )

            capital -= total_entry_cost

            entry_price = price

            trades.append({
                "date": index,
                "type": "BUY",
                "price": price,
                "position": position,
                "value": entry_value,
                "fee": entry_fee
            })

        # =========================
        # POSITION MANAGEMENT
        # =========================

        elif position > 0:

            stop_price = (
                entry_price * (1 - stop_loss)
            )

            target_price = (
                entry_price * (1 + take_profit)
            )

            exit_reason = None

            if price <= stop_price:
                exit_reason = "STOP LOSS"

            elif price >= target_price:
                exit_reason = "TAKE PROFIT"

            elif signal == "SELL":
                exit_reason = "SELL"

            # =========================
            # EXIT
            # =========================

            if exit_reason:

                exit_value = position * price

                exit_fee = (
                    exit_value * fee_rate
                )

                capital_from_trade = (
                    exit_value - exit_fee
                )

                gross_profit = (
                    exit_value - entry_value
                )

                total_fees = (
                    entry_fee + exit_fee
                )

                net_profit = (
                    gross_profit - total_fees
                )

                return_percent = (
                    net_profit / entry_value
                ) * 100

                capital += capital_from_trade

                trades.append({
                    "date": index,
                    "type": exit_reason,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "position": position,
                    "entry_value": entry_value,
                    "exit_value": exit_value,
                    "entry_fee": entry_fee,
                    "exit_fee": exit_fee,
                    "total_fees": total_fees,
                    "gross_profit": gross_profit,
                    "net_profit": net_profit,
                    "return_percent": return_percent
                })

                position = 0
                entry_price = 0
                entry_value = 0
                entry_fee = 0

        # =========================
        # EQUITY
        # =========================

        if position > 0:

            current_position_value = (
                position * price
            )

            equity = (
                capital +
                current_position_value
            )

        else:
            equity = capital

        equity_curve.append({
            "date": index,
            "equity": equity
        })

    # =========================
    # FINAL EXIT
    # =========================

    if position > 0:

        final_price = float(
            data.iloc[-1]["Close"]
        )

        exit_value = (
            position * final_price
        )

        exit_fee = (
            exit_value * fee_rate
        )

        capital_from_trade = (
            exit_value - exit_fee
        )

        gross_profit = (
            exit_value - entry_value
        )

        total_fees = (
            entry_fee + exit_fee
        )

        net_profit = (
            gross_profit - total_fees
        )

        return_percent = (
            net_profit / entry_value
        ) * 100

        capital += capital_from_trade

        trades.append({
            "date": data.index[-1],
            "type": "FINAL EXIT",
            "entry_price": entry_price,
            "exit_price": final_price,
            "position": position,
            "entry_value": entry_value,
            "exit_value": exit_value,
            "entry_fee": entry_fee,
            "exit_fee": exit_fee,
            "total_fees": total_fees,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "return_percent": return_percent
        })

    return capital, trades, equity_curve


def calculate_statistics(
    initial_capital,
    final_capital,
    trades
):
    completed_trades = [
        trade
        for trade in trades
        if trade["type"] in [
            "SELL",
            "STOP LOSS",
            "TAKE PROFIT",
            "FINAL EXIT"
        ]
    ]

    total_trades = len(
        completed_trades
    )

    winning_trades = [
        trade
        for trade in completed_trades
        if trade["net_profit"] > 0
    ]

    losing_trades = [
        trade
        for trade in completed_trades
        if trade["net_profit"] <= 0
    ]

    total_profit = (
        final_capital - initial_capital
    )

    total_return = (
        total_profit / initial_capital
    ) * 100

    if total_trades > 0:

        win_rate = (
            len(winning_trades)
            / total_trades
        ) * 100

    else:
        win_rate = 0

    total_fees = sum(
        trade.get("total_fees", 0)
        for trade in completed_trades
    )

    return {
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        "total_profit": total_profit,
        "total_return": total_return,
        "total_trades": total_trades,
        "winning_trades": len(
            winning_trades
        ),
        "losing_trades": len(
            losing_trades
        ),
        "win_rate": win_rate,
        "total_fees": total_fees
    }


def calculate_max_drawdown(
    equity_curve
):
    if not equity_curve:
        return 0

    peak = equity_curve[0]["equity"]

    max_drawdown = 0

    for point in equity_curve:

        equity = point["equity"]

        if equity > peak:
            peak = equity

        drawdown = (
            (equity - peak) / peak
        ) * 100

        if drawdown < max_drawdown:
            max_drawdown = drawdown

    return max_drawdown
