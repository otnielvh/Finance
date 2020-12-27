import financial_data
import requests
import argparse
import bs4 as bs
import redis
from common import config
from common import utils


SEC_ARCHIVE_URL = 'https://www.sec.gov/Archives/'

redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT)


def fetchCompanyData(company_line, year):
    company_line = company_line.strip()
    splitted_company = company_line.split('|')
    txt_url = splitted_company[-1]
    company_name = splitted_company[1]

    try:
        if redis_client.exists(utils.redis_key(company_name, year)):
            print(
                f'returning cached data for "{utils.redis_key(company_name, year)}"')
            return redis_client.get(utils.redis_key(company_name, year))
    except redis.exceptions.ConnectionError:
        print("Redis isn't running")
        raise ConnectionRefusedError("Redis isn't running")

    if not txt_url:
        return

    to_get_html_site = f'{SEC_ARCHIVE_URL}/{txt_url}'
    print(to_get_html_site)
    data = requests.get(to_get_html_site).content

    soup = bs.BeautifulSoup(data, 'lxml')
    financial_data.getFinancialData(soup, company_name, year)


def prepareIndex(year, quarter):
    filing = '10-K'
    filter = '10-K/A'
    download = requests.get(
        f'{SEC_ARCHIVE_URL}/edgar/full-index/{year}/{quarter}/master.idx').content
    decoded = download.decode("utf-8").split('\n')

    idx = []
    for item in decoded:
        if (filing in item) and (filter not in item):
            idx.append(item)
    return idx


def fetchYear(year):
    quarter = 'QTR1'
    filename = f'{year}-{quarter}-master.idx'

    try:
        idx = open(filename)
    except IOError:
        print("File not accessible, fetching from web")
        # get name of all filings
        idx = prepareIndex(year, quarter)
        with open(filename, 'w+') as f:
            for item in idx:
                f.write("%s\n" % item)

    for item in idx:
        fetchCompanyData(item, year)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yearStart", type=int,
                        help="The year from we want to start scraping")
    parser.add_argument("yearEnd", type=int,
                        help="The year on which we will stop scraping")
    args = parser.parse_args()
    # Startup parameters
    year_start = args.yearStart
    year_end = args.yearEnd

    for year in range(year_start, year_end):
        fetchYear(year)


if __name__ == "__main__":
    main()
