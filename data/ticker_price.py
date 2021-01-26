import yfinance as yf
from data.data_access import DataAccess


def fetch_ticker_price_volume(ticker: str) -> None:
    yf_ticker = yf.Ticker(ticker)
    da = DataAccess()
    # allowed periods are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    price_history = yf_ticker.history(period="max")
    for index, row in price_history.iterrows():
        da.store_ticker_price(ticker, int(index.timestamp()), row['Close'])
        da.store_ticker_volume(ticker, int(index.timestamp()), row['Volume'])
    da.commit_ticker_data()
