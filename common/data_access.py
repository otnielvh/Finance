import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import redis
from common import config

redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True
)

REDIS_TICKER_SET = 'ticker_set'
REDIS_CIK2TICKER_KEY = 'cik2ticker'


# Ticker financials

def financials_key(ticker: str, year: int) -> str:
    return f'{ticker}:{year}'


def store_ticker_financials(ticker: str, year: int, data: dict):
    try:
        redis_client.hset(financials_key(ticker, year), mapping=data)
    except redis.ResponseError as error:
        logging.debug(error)


def get_ticker_financials(ticker: str, year: int):
    try:
        return redis_client.hgetall(f'{ticker}:{year}')
    except redis.ResponseError as error:
        logging.debug(error)


def is_ticker_stored(ticker: str, year: int):
    return redis_client.exists(financials_key(ticker, year))

# Ticker info


def info_key(ticker: str) -> str:
    return f'{ticker}:info'


def store_ticker_info(ticker: str, data: dict):
    try:
        redis_client.hset(info_key(ticker), mapping=data)
    except redis.ResponseError as error:
        logging.debug(error)


def get_ticker_url(ticker: str, year: int):
    return redis_client.hget(info_key(ticker), f'txt_url:{year}')


def get_ticker_cik(ticker: str, year: int):
    return redis_client.hget(info_key(ticker), 'cik')


# Ticker price


def store_ticker_price(ticker: str, timestamp: int, value: float) -> None:
    try:
        redis_client.execute_command(
            "TS.ADD", f"{ticker}:price", timestamp, value)
    except redis.ResponseError as error:
        logging.debug(error)


def store_ticker_volume(ticker: str, timestamp: int, value: float) -> None:
    try:
        redis_client.execute_command(
            "TS.ADD", f"{ticker}:volume", timestamp, value)
    except redis.ResponseError as error:
        logging.debug(error)


def get_prices(ticker: str, start: datetime, end: datetime) -> List[Tuple[datetime, float]]:
    """
    :param ticker:
    :param start:
    :param end:
    :return: list of (datetime, price) tuples
    """
    start_time = int(start.timestamp())
    end_time = int(end.timestamp())
    redis_response = redis_client.execute_command("TS.RANGE", f"{ticker}:price", start_time, end_time)
    response_list = [(datetime.fromtimestamp(e[0]), float(e[1])) for e in redis_response]
    return response_list


def get_price(ticker: str, date: datetime) -> float:
    """

    :param ticker:
    :param date:
    :return: price at the specified date
    """
    start_time = date - timedelta(weeks=1)
    price_res = get_prices(ticker, start_time, date)
    if len(price_res) and len(price_res[-1]):
        return get_prices(ticker, start_time, date)[-1][-1]
    else:
        return 0


def get_ticker_by_cik(ticker):
    return redis_client.hget(REDIS_CIK2TICKER_KEY, ticker)


def store_ticker_cik_mapping(ticker: str, cik: str) -> None:
    redis_client.hset(info_key(ticker), 'cik', cik)
    redis_client.hset(f'{REDIS_CIK2TICKER_KEY}', cik, ticker)
    redis_client.sadd(REDIS_TICKER_SET, ticker)


def is_ticker_mapped(ticker: str) -> bool:
    return redis_client.sismember(REDIS_TICKER_SET, ticker)


def is_ticker_list_exist() -> bool:
    return redis_client.exists(REDIS_TICKER_SET)


def get_ticker_list() -> List[str]:
    try:
        ticker_list_resp = redis_client.sscan(REDIS_TICKER_SET, 0, count=30 * 1000)
        if ticker_list_resp[0] == 0:  # i.e. status OK
            return ticker_list_resp[1]
        else:
            logging.error('failed to load ticker list')
    except redis.ResponseError as error:
        logging.debug(error)
