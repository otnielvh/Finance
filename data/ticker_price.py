import yfinance as yf
from data import data_access


def store_ticker(ticker: str) -> None:
    yf_ticker = yf.Ticker(ticker)
    # allowed periods are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    price_history = yf_ticker.history(period="max")
    for index, row in price_history.iterrows():
        data_access.store_ticker_price(ticker, int(index.timestamp()), row['Close'])
        data_access.store_ticker_volume(ticker, int(index.timestamp()), row['Volume'])
    data_access.commit_ticker_data()
