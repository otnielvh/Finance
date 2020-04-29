import requests
import pprint
from typing import Dict, List
from utils import Period, IncomeCol, Statements
from collections import namedtuple
import data


TICKER = 'vrtx'
PERIOD = Period.Quarter

pp = pprint.PrettyPrinter(indent=4)


def get_revenue_thousands(ticker: str, period: Period = Period.Year) -> List:
    def filter(y: IncomeCol):
        return y.Date, f'{int(float(y.Revenue) / 1000):,}', f'{int(float(y.OperatingExpenses) / 1000):,}'
    return _get_revenue_filter(ticker, period, filter)


def _get_revenue_filter(ticker: str, period: Period, user_filter) -> List:
    return [user_filter(x) for x in data.get_financials(ticker, period=period)]


def main():
    pp.pprint(get_revenue_thousands(TICKER, period=PERIOD))


main()
