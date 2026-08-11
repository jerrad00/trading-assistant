import yfinance as yf


def get_market_data(symbol, period="1mo"):
    data = yf.download(
        symbol,
        period=period,
        auto_adjust=False,
        multi_level_index=False
    )

    return data


if __name__ == "__main__":
    btc_data = get_market_data("BTC-USD")
    print(btc_data.tail())