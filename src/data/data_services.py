import logging
from typing import List, Tuple

from datetime import datetime
from src.data import ticker_price
from src.data.sec_gov import SecGov
from src.data.data_access import DataAccess
from flask import Flask, request

data_services = Flask(__name__)


class DataServices:

    def __init__(self):
        self.sec_gov = SecGov()
        self.data_access = DataAccess()
        if not self.data_access.is_ticker_list_exist():
            self.sec_gov.fetch_tickers_list()

    def get_ticker_price(self, ticker: str, date: datetime) -> float:
        """
        :param ticker:
        :param date:
        :return: price at the specified date
        """
        if not self.data_access.is_ticker_price_exists(ticker):
            ticker_price.fetch_ticker_price_volume(ticker)
        return self.data_access.get_price(ticker, date)

    def get_ticker_volume(self, ticker: str, date: datetime) -> float:
        """
        :param ticker:
        :param date:
        :return: price at the specified date
        """
        if not self.data_access.is_ticker_volume_exists(ticker):
            ticker_price.fetch_ticker_price_volume(ticker)
        return self.data_access.get_volume(ticker, date)

    @staticmethod
    def fetch_ticker_prices(ticker: str) -> None:
        """ Fetch the ticker prices and store them to DB
        :param ticker:
        :return: None
        """
        ticker_price.fetch_ticker_price_volume(ticker)

    def fetch_ticker_list(self) -> List[str]:
        """Fetch a list of tickers from sec, and store them in the DB.
        Skip if already in cache.
        Returns:
            a list of tickers
        """
        return self.data_access.get_ticker_list()

    def get_ticker_data(self, ticker: str, start_year: int, end_year: int):
        """
        Could be called externally to get all data_assets known about that ticker.
        :param ticker:
        :param start_year:
        :param end_year: inclusive
        :return:
        """
        data = {}

        if not self.data_access.is_ticker_price_exists(ticker):
            ticker_price.fetch_ticker_price_volume(ticker)

        data['volume'] = {'volume': 'NA'}
        # TODO: use more accurate dates
        start_year_datetime = datetime.fromisoformat(f'{start_year}-01-01')
        end_year_datetime = datetime.fromisoformat(f'{end_year}-12-30')
        data['price'] = self.data_access.get_prices(ticker, start_year_datetime, end_year_datetime)

        for year in range(start_year, end_year + 1):
            self.fetch_ticker_financials_by_year(year, ticker)

            entry = self.data_access.get_ticker_financials(ticker, year)
            if not entry:
                logging.error(f"Could not retrieve data_assets for '{ticker} {year}' ")
            data[str(year)] = entry

        return data

    def get_ticker_financials(self, ticker: str, start_year: int, end_year: int):
        """
        Could be called to get ticker financials
        :param ticker:
        :param start_year:
        :param end_year: inclusive
        :return:
        """
        data = {}

        for year in range(start_year, end_year + 1):
            self.fetch_ticker_financials_by_year(year, ticker)

            entry = self.data_access.get_ticker_financials(ticker, year)
            if not entry:
                logging.error(f"Could not retrieve data_assets for '{ticker} {year}' ")
            data[str(year)] = entry

        return data

    def get_ticker_volumes(self, ticker: str, start: datetime, end: datetime = None) -> List[Tuple[datetime, float]]:
        """
        :param ticker:
        :param start:
        :param end:
        :return: list of (datetime, volume) tuples
        """

    def fetch_ticker_financials_by_year(self, year: int, ticker: str = None) -> None:
        """Fetch ticker financials data according to the passed year and store to DB
        Args:
            year int: The year to fetch stocks financials data
            ticker str: if not None cache this ticker, otherwise cache all
        Returns:
            None
        """
        if ticker in ['spy', 'qqq']:
            return

        if self.data_access.is_ticker_stored(ticker, year):
            logging.info(
                f'data_assets is already cached data_assets for {ticker} {year}')
            return
        self.sec_gov.fetch_ticker_financials_by_year(year, ticker)


ds = DataServices()


@data_services.route('/api/ticker-volume/<ticker>/<date>', methods=['GET'])
def get_ticker_volume(ticker: str, date: datetime) -> float:
    date = datetime.strptime(date, '%d-%m-%Y')
    return str(ds.get_ticker_volume(ticker, date))


@data_services.route('/api/ticker-price/<ticker>/<date>', methods=['GET'])
def get_ticker_price (ticker: str, date: str) -> float:
    date = datetime.strptime(date, '%d-%m-%Y')
    return str(ds.get_ticker_price(ticker, date))


@data_services.route('/api/ticker-data/<ticker>/<int:start_year>/<int:end_year>', methods=['GET'])
def get_ticker_data(ticker: str, start_year: int, end_year: int):
    return ds.get_ticker_data(ticker, start_year, end_year)


def main():
    global ds


if __name__ == "__main__":
    data_services.run(port = 4000)
    main()

