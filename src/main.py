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


def main():
    initial_capital = 10000

    btc = get_market_data(
        "BTC-USD",
        period="1y"
    )

    btc["EMA20"] = calculate_ema(
        btc,
        20
    )

    btc["RSI14"] = calculate_rsi(
        btc,
        14
    )

    btc["Signal"] = btc.apply(
        generate_signal,
        axis=1
    )

    final_capital, trades, equity_curve = run_backtest(
        btc,
        initial_capital=initial_capital,
        fee_rate=0.001,
        stop_loss=0.02,
        take_profit=0.04
    )

    statistics = calculate_statistics(
        initial_capital,
        final_capital,
        trades
    )

    max_drawdown = calculate_max_drawdown(
        equity_curve
    )

    print("\n========== BACKTEST REPORT ==========\n")

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

    print("\n=====================================\n")

    # Equity Curve

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
        label="Equity"
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
