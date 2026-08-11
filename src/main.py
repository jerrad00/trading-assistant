from data.market_data import get_market_data
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from strategy.basic_strategy import generate_signal
from backtest.engine import run_backtest


def main():
    btc = get_market_data("BTC-USD", period="1y")

    btc["EMA20"] = calculate_ema(btc, 20)
    btc["RSI14"] = calculate_rsi(btc, 14)

    btc["Signal"] = btc.apply(generate_signal, axis=1)

    final_capital, trades = run_backtest(btc)

    print("Initial capital: $10,000")
    print(f"Final capital: ${final_capital:,.2f}")

    print("\nTrades:")

    for trade in trades:
        print(trade)


if __name__ == "__main__":
    main()