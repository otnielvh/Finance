import redis
import yfinance as yf
from common import config
import logging


redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True
)


def store_ticker(ticker: str) -> None:
    yf_ticker = yf.Ticker(ticker)
    # allowed periods are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    price_history = yf_ticker.history(period="max")
    for index, row in price_history.iterrows():
        try:
            redis_client.execute_command(
                "TS.ADD", f"{ticker}:price", int(index.timestamp()), row['Close'])
            redis_client.execute_command(
                "TS.ADD", f"{ticker}:volume", int(index.timestamp()), row['Volume'])
        except redis.ResponseError as error:
            logging.debug(error)
