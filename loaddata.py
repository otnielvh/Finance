import requests
import argparse
import bs4 as bs
import redis
import logging
import sys
from typing import List
from datetime import datetime
import pymysql


from dataload import financial_data, ticker_price
from common import utils, config, data_access

SEC_ARCHIVE_URL = 'https://www.sec.gov/Archives/'

DBConnection = pymysql.connect(
    host=config.DB_HOST_NAME,
    user=config.DB_USER,
    passwd=config.DB_PASSWORD,
    db=config.DB_NAME
)


def fetch_company_data(ticker: str, year: int) -> None:
    """Fetch the data for the specified company and year from sec
    Args:
        ticker str: The ticker name
        year int: The year
    Returns:
        None
    """
    txt_url = data_access.get_ticker_url(ticker, year)
    if txt_url:
        _fetch_company_data(ticker, year, txt_url)
    else:
        logging.info(f"Couldn't load data for {ticker}:{year}")


def _fetch_company_data(ticker: str, year: int, txt_url: str) -> None:
    """Fetch the data for the specified company and year from sec
    Args:
        ticker str: The ticker name
        year int: The year
        txt_url str: The url to fetch from the data
    Returns:
        None
    """
    try:
        if data_access.is_ticker_stored(ticker, year):
            logging.info(
                f'data is already cached data for {ticker} {year}"')
            return
    except redis.exceptions.ConnectionError:
        logging.error("Redis isn't running")
        raise ConnectionRefusedError("Redis isn't running")

    if not txt_url:
        return

    to_get_html_site = f'{SEC_ARCHIVE_URL}/{txt_url}'
    data = requests.get(to_get_html_site).content

    xbrl_doc = bs.SoupStrainer("xbrl")
    soup = bs.BeautifulSoup(data, 'lxml', parse_only=xbrl_doc)

    if soup:
        financial_data.get_financial_data(soup, ticker, year)


def prepare_index(year: int, quarter: int) -> None:
    """Prepare the edgar index for the passed year and quarter
    The data will be saved to DB
    Args:
        year int: The year to build the index for
        quarter int: The quarter to build the index between 1-4
    Returns:
        None
    """
    filing = '|10-K|'
    download = requests.get(f'{SEC_ARCHIVE_URL}/edgar/full-index/{year}/QTR{quarter}/master.idx').content
    decoded = download.decode("ISO-8859-1").split('\n')

    with DBConnection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `sec_idx` (`cik`, `year`, `company`, `report_type`, `url`) VALUES (%s, %s, %s, %s, %s)"
        for item in decoded:
            if filing in item:
                values = item.split('|')
                try:
                    cursor.execute(sql, (values[0], int(year), values[1], values[2], values[4]))
                # TBD - some companies have multiple 10-K
                except pymysql.err.IntegrityError:
                    pass
    logging.info(f"Inserted year {year} qtr {quarter} to DB")
    DBConnection.commit()


def fetch_year(year: int, ticker: str = None) -> None:
    """Fetch stocks data according to the passed year
    The data will be saved to DB
    Args:
        year int: The year to fetch stocks data
        ticker str: if not None cache this ticker, otherwise cache all
    Returns:
        None
    """
    if ticker and data_access.is_ticker_stored(ticker, year):
        logging.info(f'data is already cached data for {ticker} {year}')
        return

    # TODO: skip in a better way. For now skip these ETFs manually
    if ticker in ['spy', 'qqq']:
        return

    with DBConnection.cursor() as cursor:
        # Create a new record
        sql = f'SELECT COUNT(*) FROM {config.DB_NAME}.sec_idx where year={year}'
        cursor.execute(sql)
        # TODO: Error handling
        result = cursor.fetchone()

        # check if the index exists
        if result[0] == 0:
            logging.info(f"Index file for year {year} is not accessible, fetching from web")
            for q in range(1, 5):  # 1 to 4 inclusive
                prepare_index(year, q)

    if ticker:
        ticker_cik = data_access.get_ticker_cik(ticker, year)
        with DBConnection.cursor() as cursor:
            # Create a new record
            sql = f'SELECT company, url FROM sec_idx where cik={ticker_cik}'
            cursor.execute(sql)
            # TODO: error handling
            result = cursor.fetchone()
            ticker_info_hash = {
                'company_name': result[0],
                f'txt_url:{year}': result[1]
            }
            data_access.store_ticker_info(ticker, ticker_info_hash)
            fetch_company_data(ticker, year)
    else:
        with DBConnection.cursor() as cursor:
            # Create a new record
            sql = f'SELECT company, url, cik FROM sec_idx where year={year}'
            cursor.execute(sql)
            # TODO: error handling
            for result in cursor.fetchall():
                current_ticker = data_access.get_ticker_by_cik(result[2])
                ticker_info_hash = {
                    'company_name': result[0],
                    f'txt_url:{year}': result[1]
                }
                data_access.store_ticker_info(current_ticker, ticker_info_hash)
                fetch_company_data(ticker, year)


def fetch_ticker_list() -> List[str]:
    """Fetch a list of tickers from sec, and store them in the DB.
    Skip if already in cache.
    Returns:
        a list of tickers
    """
    ticker_list = []
    if not data_access.is_ticker_list_exist():
        resp = requests.get(utils.TICKER_CIK_LIST_URL)
        ticker_cik_list_lines = resp.content.decode("utf-8").split('\n')
        for entry in ticker_cik_list_lines:
            ticker, cik = entry.strip().split()
            ticker = ticker.strip()
            cik = cik.strip()
            data_access.store_ticker_cik_mapping(ticker, cik)
            ticker_list.append(ticker)
    return ticker_list


def fetch_ticker(ticker: str) -> None:
    """Fetch tickers from sec, and store it in the DB.
    Skip if already in cache.
    Args:
        ticker str: ticker to fetch
    Returns:
        None
    """
    if not data_access.is_ticker_mapped(ticker):
        resp = requests.get(utils.TICKER_CIK_LIST_URL)
        ticker_cik_list_lines = resp.content.decode("utf-8").split('\n')

        for entry in ticker_cik_list_lines:
            other_ticker, cik = entry.strip().split()
            other_ticker = other_ticker.strip()
            cik = cik.strip()
            data_access.store_ticker_cik_mapping(other_ticker, cik)
            if other_ticker == ticker:
                logging.info(f'Successfully mapped {ticker} to cik {cik}')


def get_ticker_data(ticker: str, start_year: int, end_year: int):
    """
    Could be called externally to get all data known about that ticker.
    :param ticker:
    :param start_year:
    :param end_year: inclusive
    :return:
    """
    data = {}

    fetch_ticker(ticker)

    if not data_access.is_ticker_price_exists(ticker):
        ticker_price.store_ticker(ticker)

    data['volume'] = {'volume': 'NA'}
    # TODO: use more accurate dates
    start_year_datetime = datetime.fromisoformat(f'{start_year}-01-01')
    end_year_datetime = datetime.fromisoformat(f'{end_year}-12-30')
    data['price'] = data_access.get_prices(ticker, start_year_datetime, end_year_datetime)

    for year in range(start_year, end_year + 1):
        fetch_year(year, ticker)

        entry = data_access.get_ticker_financials(ticker, year)
        if not entry:
            logging.error(f"Could not retrieve data for '{ticker} {year}' ")
        data[str(year)] = entry

    return data


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("yearStart",
                        type=int,
                        help="The year from we want to start scraping")
    parser.add_argument("yearEnd",
                        type=int,
                        help="The year on which we will stop scraping")
    parser.add_argument("--ticker",
                        type=str,
                        help="Add a single ticker to the database")
    args = parser.parse_args()
    # Startup parameters
    year_start = args.yearStart
    year_end = args.yearEnd

    if args.ticker:
        fetch_ticker(args.ticker)
        ticker_list = [args.ticker]
    else:
        ticker_list = fetch_ticker_list()

    for ticker in ticker_list:
        ticker_price.store_ticker(ticker)

    for year in range(year_start, year_end + 1):
        fetch_year(year, args.ticker)


if __name__ == "__main__":
    main()
