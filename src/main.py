from data.market_data import get_market_data
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from strategy.basic_strategy import generate_signal
from backtest.engine import run_backtest, calculate_statistics


def main():
    initial_capital = 10000

    btc = get_market_data("BTC-USD", period="1y")

    btc["EMA20"] = calculate_ema(btc, 20)
    btc["RSI14"] = calculate_rsi(btc, 14)

    btc["Signal"] = btc.apply(generate_signal, axis=1)

    final_capital, trades = run_backtest(
        btc,
        initial_capital
    )

    statistics = calculate_statistics(
        initial_capital,
        final_capital,
        trades
    )

    print("\n========== BACKTEST REPORT ==========\n")

    print(f"Initial Capital : ${statistics['initial_capital']:,.2f}")
    print(f"Final Capital   : ${statistics['final_capital']:,.2f}")
    print(f"Total Profit    : ${statistics['total_profit']:,.2f}")
    print(f"Total Return    : {statistics['total_return']:.2f}%")

    print()

    print(f"Total Trades    : {statistics['total_trades']}")
    print(f"Winning Trades  : {statistics['winning_trades']}")
    print(f"Losing Trades   : {statistics['losing_trades']}")
    print(f"Win Rate        : {statistics['win_rate']:.2f}%")

    print("\n=====================================\n")


if __name__ == "__main__":
    main()