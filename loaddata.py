import requests
import argparse
import bs4 as bs
import redis
import logging
import sys
import os
from typing import List

from dataload import financial_data as financial_data
from common import utils, config

SEC_ARCHIVE_URL = 'https://www.sec.gov/Archives/'

redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True
)


def fetch_company_data(ticker: str, year: int) -> None:
    """Fetch the data for the specified company and year from sec
    Args:
        ticker str: The ticker name
        year int: The year
    Returns:
        None
    """
    txt_url = redis_client.hget(f'{ticker}:info', f'txt_url:{year}')
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
        if redis_client.exists(utils.redis_key(ticker, year)):
            logging.info(
                f'data is already cached data for "{utils.redis_key(ticker, year)}"')
            return  # redis_client.hgetall(utils.redis_key(ticker, year))
    except redis.exceptions.ConnectionError:
        logging.error("Redis isn't running")
        raise ConnectionRefusedError("Redis isn't running")

    if not txt_url:
        return

    to_get_html_site = f'{SEC_ARCHIVE_URL}/{txt_url}'
    data = requests.get(to_get_html_site).content

    xbrl_doc = bs.SoupStrainer("xbrl")
    soup = bs.BeautifulSoup(data, 'lxml', parse_only=xbrl_doc)
    # if soup is None:
    #     xbrl_doc = bs.SoupStrainer("xbrli:xbrl")
    #     soup = bs.BeautifulSoup(data, 'lxml', parse_only=xbrl_doc)

    if soup:
        financial_data.get_financial_data(soup, ticker, year)


def prepare_index(year: int, quarter: int) -> List[List[str]]:
    """Prepare the edgar index for the passed year and quarter
    The data will be saved to DB
    Args:
        year int: The year to build the index for
        quarter int: The quarter to build the index between 1-4
    Returns:
        List
    """
    filing = '10-K'
    exclude = '10-K/A'
    download = requests.get(
        f'{SEC_ARCHIVE_URL}/edgar/full-index/{year}/QTR{quarter}/master.idx').content
    decoded = download.decode("ISO-8859-1").split('\n')

    idx = []
    for item in decoded:
        if (filing in item) and (exclude not in item):
            idx.append(item.split('|'))
    return idx


def fetch_year(year: int, ticker: str = None) -> None:
    """Fetch stocks data according to the passed year
    The data will be saved to DB
    Args:
        year int: The year to fetch stocks data
        ticker str: if not None cache this ticker, otherwise cache all
    Returns:
        None
    """

    filename = f'{config.ASSETS_DIR}/{year}-master.idx'

    if not os.path.isdir(config.ASSETS_DIR):
        os.mkdir(config.ASSETS_DIR)

    # check if the index exists
    if not os.path.exists(filename):
        logging.info(f"File {filename} is not accessible, fetching from web")
        # build the index file

        yearly_idx = []
        for q in range(1, 5):  # 1 to 4 inclusive
            idx = prepare_index(year, q)
            yearly_idx.extend(idx)
        yearly_idx.sort(key=lambda k: k[0])
        with open(filename, 'w+') as f:
            for item in yearly_idx:
                f.write('|'.join(item) + '\n')

    # TODO: skip if ticker data is cached
    with open(filename, 'r+') as f:
        for item in f.readlines():
            # store each entry in Redis
            company_line = item.strip()
            splitted_company = company_line.split('|')
            txt_url = splitted_company[-1]
            company_name = splitted_company[1]
            cik = splitted_company[0].strip()
            current_ticker = redis_client.hget(utils.REDIS_CIK2TICKER_KEY, cik)
            if (ticker and current_ticker == ticker) or current_ticker:
                ticker_info_hash = {
                    'company_name': company_name,
                    f'txt_url:{year}': txt_url
                }
                redis_client.hset(f'{current_ticker}:info', mapping=ticker_info_hash)

    if ticker:
        fetch_company_data(ticker, year)
    else:
        ticker_list_resp = redis_client.sscan(
            utils.REDIS_TICKER_SET, count=30 * 1000)
        if ticker_list_resp[0] == 0:  # i.e. status OK
            for ticker in ticker_list_resp[1]:
                fetch_company_data(ticker, year)
        else:
            logging.error('error in ticker_list_response')


def fetch_ticker_list() -> None:
    """Fetch a list of tickers from sec, and store them in the DB.
    Skip if already in cache.
    Returns:
        None
    """
    if not redis_client.exists(utils.REDIS_TICKER_SET):
        resp = requests.get(utils.TICKER_CIK_LIST_URL)
        ticker_cik_list_lines = resp.content.decode("utf-8").split('\n')

        for entry in ticker_cik_list_lines:
            ticker, cik = entry.strip().split()
            ticker = ticker.strip()
            cik = cik.strip()
            store_ticker_cik_mapping(ticker, cik)


def fetch_ticker(ticker: str) -> None:
    """Fetch tickers from sec, and store it in the DB.
    Skip if already in cache.
    Args:
        ticker str: ticker to fetch
    Returns:
        None
    """
    if not redis_client.sismember(utils.REDIS_TICKER_SET, ticker):
        resp = requests.get(utils.TICKER_CIK_LIST_URL)
        ticker_cik_list_lines = resp.content.decode("utf-8").split('\n')

        for entry in ticker_cik_list_lines:
            other_ticker, cik = entry.strip().split()
            other_ticker = other_ticker.strip()
            cik = cik.strip()
            if other_ticker == ticker:
                store_ticker_cik_mapping(ticker, cik)


def store_ticker_cik_mapping(ticker: str, cik: str) -> None:
        redis_client.hset(f'{ticker}:info', 'cik', cik)
        redis_client.hset(f'{utils.REDIS_CIK2TICKER_KEY}', cik, ticker)
        redis_client.sadd(utils.REDIS_TICKER_SET, ticker)


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
    else:
        fetch_ticker_list()

    for year in range(year_start, year_end + 1):
        fetch_year(year, args.ticker)


if __name__ == "__main__":
    main()
