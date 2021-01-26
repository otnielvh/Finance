import logging
import pymysql
from datetime import datetime, timedelta
from typing import List, Tuple

import redis
from common import config


class DataAccess:
    redis_client = redis.Redis(
        host=config.REDIS_HOST_NAME,
        port=config.REDIS_PORT,
        decode_responses=True
    )

    DBConnection = pymysql.connect(
        host=config.DB_HOST_NAME,
        user=config.DB_USER,
        passwd=config.DB_PASSWORD,
        db=config.DB_NAME
    )

    REDIS_TICKER_SET = 'ticker_set'
    REDIS_CIK2TICKER_KEY = 'cik2ticker'

    # Ticker financials

    @staticmethod
    def _financials_key(ticker: str, year: int) -> str:
        return f'{ticker}:{year}'

    def store_ticker_financials(self, ticker: str, year: int, data: dict):
        try:
            self.redis_client.hset(self._financials_key(ticker, year), mapping=data)
        except redis.ResponseError as error:
            logging.debug(error)

    def get_ticker_financials(self, ticker: str, year: int):
        try:
            return self.redis_client.hgetall(f'{ticker}:{year}')
        except redis.ResponseError as error:
            logging.debug(error)

    def is_ticker_stored(self, ticker: str, year: int):
        try:
            return self.redis_client.exists(self._financials_key(ticker, year))
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def commit_ticker_data(self):
        try:
            return self.redis_client.bgsave()
        except redis.ResponseError as error:
            logging.debug(error)

    # Ticker info
    @staticmethod
    def _info_key(ticker: str) -> str:
        return f'{ticker}:info'

    def store_ticker_info(self, ticker: str, data: dict):
        try:
            self.redis_client.hset(self._info_key(ticker), mapping=data)
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def get_ticker_url(self, ticker: str, year: int):
        try:
            return self.redis_client.hget(self._info_key(ticker), f'txt_url:{year}')
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def get_ticker_cik(self, ticker: str):
        try:
            return self.redis_client.hget(self._info_key(ticker), 'cik')
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    # Ticker price
    def store_ticker_price(self, ticker: str, timestamp: int, value: float) -> None:
        try:
            self.redis_client.execute_command(
                "TS.ADD", f"{ticker}:price", timestamp, value)
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def store_ticker_volume(self, ticker: str, timestamp: int, value: float) -> None:
        try:
            self.redis_client.execute_command(
                "TS.ADD", f"{ticker}:volume", timestamp, value)
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def is_ticker_price_exists(self, ticker: str):
        try:
            return self.redis_client.exists(f'{ticker}:price')
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def get_prices(self, ticker: str, start: datetime, end: datetime) -> List[Tuple[datetime, float]]:
        """
        :param ticker:
        :param start:
        :param end:
        :return: list of (datetime, price) tuples
        """
        try:
            start_time = int(start.timestamp())
            end_time = int(end.timestamp())
            redis_response = self.redis_client.execute_command("TS.RANGE", f"{ticker}:price", start_time, end_time)
            response_list = [(datetime.fromtimestamp(e[0]), float(e[1])) for e in redis_response]
            return response_list
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def get_volumes(self, ticker: str, start: datetime, end: datetime) -> List[Tuple[datetime, float]]:
        """
        :param ticker:
        :param start:
        :param end:
        :return: list of (datetime, price) tuples
        """
        try:
            start_time = int(start.timestamp())
            end_time = int(end.timestamp())
            redis_response = self.redis_client.execute_command("TS.RANGE", f"{ticker}:volume", start_time, end_time)
            response_list = [(datetime.fromtimestamp(e[0]), float(e[1])) for e in redis_response]
            return response_list
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def get_price(self, ticker: str, date: datetime) -> float:
        """

        :param ticker:
        :param date:
        :return: price at the specified date
        """
        start_time = date - timedelta(weeks=1)
        price_res = self.get_prices(ticker, start_time, date)
        if price_res is not None and len(price_res) and len(price_res[-1]):
            return self.get_prices(ticker, start_time, date)[-1][-1]
        else:
            return 0

    def get_volume(self, ticker: str, date: datetime) -> float:
        """

        :param ticker:
        :param date:
        :return: price at the specified date
        """
        start_time = date - timedelta(weeks=1)
        price_res = self.get_prices(ticker, start_time, date)
        if price_res is not None and len(price_res) and len(price_res[-1]):
            return self.get_volumes(ticker, start_time, date)[-1][-1]
        else:
            return 0

    def get_ticker_by_cik(self, ticker):
        try:
            return self.redis_client.hget(self.REDIS_CIK2TICKER_KEY, ticker)
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def store_ticker_cik_mapping(self, ticker: str, cik: str) -> None:
        try:
            self.redis_client.hset(self._info_key(ticker), 'cik', cik)
            self.redis_client.hset(f'{self.REDIS_CIK2TICKER_KEY}', cik, ticker)
            self.redis_client.sadd(self.REDIS_TICKER_SET, ticker)
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def is_ticker_mapped(self, ticker: str) -> bool:
        try:
            return self.redis_client.sismember(self.REDIS_TICKER_SET, ticker)
        except redis.ResponseError as error:
            logging.debug(f'{error} ticker: {ticker}')

    def is_ticker_list_exist(self) -> bool:
        try:
            return self.redis_client.exists(self.REDIS_TICKER_SET)
        except redis.ResponseError as error:
            logging.debug(f'{error}')

    def get_ticker_list(self) -> List[str]:
        try:
            ticker_list_resp = self.redis_client.sscan(self.REDIS_TICKER_SET, 0, count=30 * 1000)
            if ticker_list_resp[0] == 0:  # i.e. status OK
                return ticker_list_resp[1]
            else:
                logging.error('failed to load ticker list')
        except redis.ResponseError as error:
            logging.debug(error)

    # Index
    def store_index(self, data: List[str], year, filling: str) -> None:
        with self.DBConnection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `sec_idx` (`cik`, `year`, `company`, `report_type`, `url`) VALUES (%s, %s, %s, %s, %s)"
            for item in data:
                if filling in item:
                    values = item.split('|')
                    try:
                        cursor.execute(sql, (values[0], int(year), values[1], values[2], values[4]))
                    # TBD - some companies have multiple 10-K
                    except pymysql.err.IntegrityError:
                        pass
        self.DBConnection.commit()

    def is_index_stored(self, year: int) -> bool:
        with self.DBConnection.cursor() as cursor:
            sql = f'SELECT COUNT(*) FROM {config.DB_NAME}.sec_idx where year={year}'
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0]

    def get_index_row_by_cik(self, cik: int, year: int) -> List[str]:
        with self.DBConnection.cursor() as cursor:
            # Create a new record
            sql = f'SELECT company, url FROM sec_idx where cik={cik} and year={year}'
            cursor.execute(sql)
            return cursor.fetchone()

    def get_index_by_year(self, year: int) -> List[List[str]]:
        with self.DBConnection.cursor() as cursor:
            # Create a new record
            sql = f'SELECT company, url, cik FROM sec_idx where year={year}'
            cursor.execute(sql)
            return cursor.fetchall()
