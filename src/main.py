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

    capital_after_entry_fee = (
        initial_capital - entry_fee
    )

    position = (
        capital_after_entry_fee
        / first_price
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

    # حذف ردیف‌هایی که اندیکاتور هنوز
    # مقدار معتبر ندارد
    btc = btc.dropna(
        subset=["EMA20", "RSI14"]
    )

    # =========================
    # STRATEGY BACKTEST
    # =========================

    final_capital, trades, equity_curve = run_backtest(
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

    # =========================
    # BUY & HOLD REPORT
    # =========================

    print(
        "\n========== BUY & HOLD ==============\n"
    )

    print(
        f"Initial Capital : "
        f"${buy_hold['initial_capital']:,.2f}"
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

    # =========================
    # COMPARISON
    # =========================

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
            "Result          : Strategy performed better"
        )
    elif difference < 0:
        print(
            "Result          : Buy & Hold performed better"
        )
    else:
        print(
            "Result          : Both performed equally"
        )

    print(
        "\n=====================================\n"
    )

    # =========================
    # SAVE TRADES
    # =========================

    save_trades_to_csv(trades)

    # =========================
    # EQUITY CURVE
    # =========================

    dates = [
        point["date"]
        for point in equity_curve
    ]

    equity_values = [
        point["equity"]
        for point in equity_curve
    ]

    plt.figure(figsize=(12, 6))

    plt.plot(
        dates,
        equity_values,
        label="Trading Strategy"
    )

    plt.title(
        "Trading Strategy Equity Curve"
    )

    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")

    plt.legend()
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    main()
