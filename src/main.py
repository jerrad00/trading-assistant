import csv
import matplotlib.pyplot as plt

from data.market_data import get_market_data
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from strategy.basic_strategy import generate_signal

from backtest.engine import (
    run_backtest,
    calculate_statistics,
    calculate_max_drawdown
)


def save_trades_to_csv(trades):
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

    if not completed_trades:
        return

    filename = "trades.csv"

    fields = [
        "date",
        "type",
        "entry_price",
        "exit_price",
        "position",
        "entry_value",
        "exit_value",
        "entry_fee",
        "exit_fee",
        "total_fees",
        "gross_profit",
        "net_profit",
        "return_percent"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(completed_trades)

    print(
        f"Trade history saved to: {filename}"
    )


def calculate_buy_and_hold(
    data,
    initial_capital,
    fee_rate
):
    first_price = float(
        data["Close"].iloc[0]
    )

    last_price = float(
        data["Close"].iloc[-1]
    )

    entry_fee = (
        initial_capital * fee_rate
    )

    capital_after_fee = (
        initial_capital - entry_fee
    )

    position = (
        capital_after_fee / first_price
    )

    final_value = (
        position * last_price
    )

    exit_fee = (
        final_value * fee_rate
    )

    final_capital = (
        final_value - exit_fee
    )

    total_fees = (
        entry_fee + exit_fee
    )

    profit = (
        final_capital - initial_capital
    )

    return_percent = (
        profit / initial_capital
    ) * 100

    return {
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        "profit": profit,
        "return_percent": return_percent,
        "total_fees": total_fees
    }


def build_trade_markers(
    data,
    trades
):
    buy_dates = []
    buy_prices = []

    sell_dates = []
    sell_prices = []

    stop_dates = []
    stop_prices = []

    target_dates = []
    target_prices = []

    for trade in trades:

        trade_type = trade["type"]

        date = trade["date"]

        if trade_type == "BUY":

            buy_dates.append(date)
            buy_prices.append(
                trade["price"]
            )

        elif trade_type == "SELL":

            sell_dates.append(date)
            sell_prices.append(
                trade["exit_price"]
            )

        elif trade_type == "STOP LOSS":

            stop_dates.append(date)
            stop_prices.append(
                trade["exit_price"]
            )

        elif trade_type == "TAKE PROFIT":

            target_dates.append(date)
            target_prices.append(
                trade["exit_price"]
            )

        elif trade_type == "FINAL EXIT":

            sell_dates.append(date)
            sell_prices.append(
                trade["exit_price"]
            )

    return (
        buy_dates,
        buy_prices,
        sell_dates,
        sell_prices,
        stop_dates,
        stop_prices,
        target_dates,
        target_prices
    )


def plot_price_chart(
    data,
    trades
):
    (
        buy_dates,
        buy_prices,
        sell_dates,
        sell_prices,
        stop_dates,
        stop_prices,
        target_dates,
        target_prices
    ) = build_trade_markers(
        data,
        trades
    )

    plt.figure(figsize=(14, 7))

    plt.plot(
        data.index,
        data["Close"],
        label="BTC Price"
    )

    plt.plot(
        data.index,
        data["EMA20"],
        label="EMA 20"
    )

    if buy_dates:

        plt.scatter(
            buy_dates,
            buy_prices,
            marker="^",
            s=100,
            label="BUY"
        )

    if sell_dates:

        plt.scatter(
            sell_dates,
            sell_prices,
            marker="v",
            s=100,
            label="SELL"
        )

    if stop_dates:

        plt.scatter(
            stop_dates,
            stop_prices,
            marker="x",
            s=100,
            label="STOP LOSS"
        )

    if target_dates:

        plt.scatter(
            target_dates,
            target_prices,
            marker="o",
            s=80,
            label="TAKE PROFIT"
        )

    plt.title(
        "BTC Trading Strategy"
    )

    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_equity_curve(
    equity_curve,
    buy_hold,
    initial_capital
):
    dates = [
        point["date"]
        for point in equity_curve
    ]

    strategy_values = [
        point["equity"]
        for point in equity_curve
    ]

    first_price = strategy_values[0]

    buy_hold_values = []

    for index in range(
        len(dates)
    ):

        price_ratio = (
            buy_hold["final_capital"]
            / initial_capital
        )

        if len(dates) > 1:

            progress = (
                index
                / (len(dates) - 1)
            )

            value = (
                initial_capital
                * (
                    1
                    + (
                        price_ratio - 1
                    )
                    * progress
                )
            )

        else:

            value = initial_capital

        buy_hold_values.append(
            value
        )

    plt.figure(figsize=(14, 7))

    plt.plot(
        dates,
        strategy_values,
        label="Strategy"
    )

    plt.plot(
        dates,
        buy_hold_values,
        label="Buy & Hold"
    )

    plt.title(
        "Strategy vs Buy & Hold"
    )

    plt.xlabel("Date")
    plt.ylabel(
        "Portfolio Value ($)"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def main():

    initial_capital = 10000

    fee_rate = 0.001
    stop_loss = 0.02
    take_profit = 0.04
    risk_per_trade = 0.01

    # =========================
    # MARKET DATA
    # =========================

    btc = get_market_data(
        "BTC-USD",
        period="1y"
    )

    # =========================
    # INDICATORS
    # =========================

    btc["EMA20"] = calculate_ema(
        btc,
        20
    )

    btc["RSI14"] = calculate_rsi(
        btc,
        14
    )

    # =========================
    # SIGNALS
    # =========================

    btc["Signal"] = btc.apply(
        generate_signal,
        axis=1
    )

    btc = btc.dropna(
        subset=[
            "EMA20",
            "RSI14"
        ]
    )

    # =========================
    # BACKTEST
    # =========================

    (
        final_capital,
        trades,
        equity_curve
    ) = run_backtest(
        btc,
        initial_capital=initial_capital,
        fee_rate=fee_rate,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_per_trade=risk_per_trade
    )

    statistics = calculate_statistics(
        initial_capital,
        final_capital,
        trades
    )

    max_drawdown = calculate_max_drawdown(
        equity_curve
    )

    # =========================
    # BUY & HOLD
    # =========================

    buy_hold = calculate_buy_and_hold(
        btc,
        initial_capital,
        fee_rate
    )

    # =========================
    # REPORT
    # =========================

    print(
        "\n========== STRATEGY REPORT ==========\n"
    )

    print(
        f"Initial Capital : "
        f"${statistics['initial_capital']:,.2f}"
    )

    print(
        f"Final Capital   : "
        f"${statistics['final_capital']:,.2f}"
    )

    print(
        f"Total Profit    : "
        f"${statistics['total_profit']:,.2f}"
    )

    print(
        f"Total Return    : "
        f"{statistics['total_return']:.2f}%"
    )

    print()

    print(
        f"Total Trades    : "
        f"{statistics['total_trades']}"
    )

    print(
        f"Winning Trades  : "
        f"{statistics['winning_trades']}"
    )

    print(
        f"Losing Trades   : "
        f"{statistics['losing_trades']}"
    )

    print(
        f"Win Rate        : "
        f"{statistics['win_rate']:.2f}%"
    )

    print(
        f"Max Drawdown    : "
        f"{max_drawdown:.2f}%"
    )

    print(
        f"Total Fees      : "
        f"${statistics['total_fees']:,.2f}"
    )

    print(
        "\n=====================================\n"
    )

    print(
        "\n========== BUY & HOLD ==============\n"
    )

    print(
        f"Final Capital   : "
        f"${buy_hold['final_capital']:,.2f}"
    )

    print(
        f"Total Profit    : "
        f"${buy_hold['profit']:,.2f}"
    )

    print(
        f"Total Return    : "
        f"{buy_hold['return_percent']:.2f}%"
    )

    print(
        f"Total Fees      : "
        f"${buy_hold['total_fees']:,.2f}"
    )

    print(
        "\n=====================================\n"
    )

    difference = (
        statistics["total_return"]
        - buy_hold["return_percent"]
    )

    print(
        "\n========== COMPARISON ===============\n"
    )

    print(
        f"Strategy Return : "
        f"{statistics['total_return']:.2f}%"
    )

    print(
        f"Buy & Hold      : "
        f"{buy_hold['return_percent']:.2f}%"
    )

    print(
        f"Difference      : "
        f"{difference:.2f}%"
    )

    if difference > 0:

        print(
            "Result          : "
            "Strategy performed better"
        )

    elif difference < 0:

        print(
            "Result          : "
            "Buy & Hold performed better"
        )

    else:

        print(
            "Result          : "
            "Both performed equally"
        )

    print(
        "\n=====================================\n"
    )

    # =========================
    # SAVE TRADES
    # =========================

    save_trades_to_csv(
        trades
    )

    # =========================
    # PRICE CHART
    # =========================

    plot_price_chart(
        btc,
        trades
    )

    # =========================
    # EQUITY CHART
    # =========================

    plot_equity_curve(
        equity_curve,
        buy_hold,
        initial_capital
    )


if __name__ == "__main__":
    main()
