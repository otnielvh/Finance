import argparse
import logging
import sys
from data.data_services import DataServices


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

    ds = DataServices()
    ticker_list = ds.fetch_ticker_list()
    if args.ticker:
        ticker_list = [args.ticker]

    for ticker in ticker_list:
        ds.fetch_ticker_prices(ticker)

        for year in range(year_start, year_end + 1):
            ds.fetch_ticker_financials_by_year(year, ticker)


if __name__ == "__main__":
    main()