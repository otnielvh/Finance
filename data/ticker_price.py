import yfinance as yf
from pandas.core.frame import DataFrame


def get_price(ticker: str) -> DataFrame:
    yf_ticker = yf.Ticker(ticker)
    # allowed periods are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    price_history = yf_ticker.history(period="max")
    return price_history
