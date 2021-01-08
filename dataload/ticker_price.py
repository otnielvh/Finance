import redis
import datetime
import yfinance as yf
from pandas.core.frame import DataFrame
from common import config
import logging


redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True
)


def get_prices(ticker: str, start: datetime, end: datetime) -> float:
    starttime = int(start.timestamp())
    endtime = int(end.timestamp())
    return redis_client.execute_command(
        "TS.RANGE", f"{ticker}:price", starttime, endtime)


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
            if error == "TSDB: Timestamp cannot be older than the latest timestamp in the time series":
                pass


start = datetime.datetime.strptime('2017-04-07T00:00:00', '%Y-%m-%dT%H:%M:%S')
start = start.replace(tzinfo=datetime.timezone.utc)
end = datetime.datetime.strptime('2017-04-11T00:00:00', '%Y-%m-%dT%H:%M:%S')
end = end.replace(tzinfo=datetime.timezone.utc)

result = get_prices("okta", start, end)
print(result)
# store_ticker("okta")
