import logging
from typing import List, Tuple

from datetime import datetime
from data import sec_gov, ticker_price, data_access


class DataAccess:

    def __init__(self):
        self.ticker_list = sec_gov.fetch_tickers_list()

    @staticmethod
    def get_ticker_price(ticker: str, date: datetime) -> float:
        """
        :param ticker:
        :param date:
        :return: price at the specified date
        """
        return data_access.get_price(ticker, date)

    @staticmethod
    def get_ticker_volume(ticker: str, date: datetime) -> float:
        """
        :param ticker:
        :param date:
        :return: price at the specified date
        """
        return data_access.get_volume(ticker, date)

    def fetch_ticker_prices(self, ticker: str) -> None:
        """ Fetch the ticker prices and store them to DB
        :param ticker:
        :return: None
        """
        ticker_price.store_ticker(ticker)

    def fetch_ticker_list(self) -> List[str]:
        """Fetch a list of tickers from sec, and store them in the DB.
        Skip if already in cache.
        Returns:
            a list of tickers
        """
        return self.ticker_list

    @staticmethod
    def get_ticker_data(ticker: str, start_year: int, end_year: int):
        """
        Could be called externally to get all data_assets known about that ticker.
        :param ticker:
        :param start_year:
        :param end_year: inclusive
        :return:
        """
        data = {}

        if not data_access.is_ticker_price_exists(ticker):
            ticker_price.store_ticker(ticker)

        data['volume'] = {'volume': 'NA'}
        # TODO: use more accurate dates
        start_year_datetime = datetime.fromisoformat(f'{start_year}-01-01')
        end_year_datetime = datetime.fromisoformat(f'{end_year}-12-30')
        data['price'] = data_access.get_prices(ticker, start_year_datetime, end_year_datetime)

        for year in range(start_year, end_year + 1):
            DataAccess.fetch_ticker_financials_by_year(year, ticker)

            entry = data_access.get_ticker_financials(ticker, year)
            if not entry:
                logging.error(f"Could not retrieve data_assets for '{ticker} {year}' ")
            data[str(year)] = entry

        return data

    def get_ticker_volumes(self, ticker: str, start: datetime, end: datetime=None) -> List[Tuple[datetime, float]]:
        """
        :param ticker:
        :param start:
        :param end:
        :return: list of (datetime, volume) tuples
        """

    @staticmethod
    def fetch_ticker_financials_by_year(year: int, ticker: str = None) -> None:
        """Fetch ticker financials data according to the passed year and store to DB
        Args:
            year int: The year to fetch stocks financials data
            ticker str: if not None cache this ticker, otherwise cache all
        Returns:
            None
        """
        if ticker and data_access.is_ticker_stored(ticker, year):
            logging.info(f'data_assets is already cached data_assets for {ticker} {year}')
            return

        # TODO: skip in a better way. For now skip these ETFs manually
        if ticker in ['spy', 'qqq']:
            return

        sec_gov.fetch_ticker_financials_by_year(year, ticker)
