import redis
import yfinance as yf
from common import config, data_access
import logging


# redis_client = redis.Redis(
#     host=config.REDIS_HOST_NAME,
#     port=config.REDIS_PORT,
#     decode_responses=True
# )


def store_ticker(ticker: str) -> None:
    yf_ticker = yf.Ticker(ticker)
    # allowed periods are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    price_history = yf_ticker.history(period="max")
    for index, row in price_history.iterrows():
        data_access.store_ticker_price(ticker, int(index.timestamp()), row['Close'])
        data_access.store_ticker_volume(ticker, int(index.timestamp()), row['Volume'])
        # try:
        #     redis_client.execute_command(
        #         "TS.ADD", f"{ticker}:price", int(index.timestamp()), row['Close'])
        #     redis_client.execute_command(
        #         "TS.ADD", f"{ticker}:volume", int(index.timestamp()), row['Volume'])
        # except redis.ResponseError as error:
        #     logging.debug(error)
