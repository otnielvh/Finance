from enum import Enum
from collections import namedtuple
from common import config
import redis
from datetime import datetime, timedelta
from typing import List, Tuple


redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True
)

TICKER_CIK_LIST_URL = 'https://www.sec.gov/include/ticker.txt'
REDIS_TICKER_SET = 'ticker_set'
REDIS_CIK2TICKER_KEY = 'cik2ticker'


class Period(Enum):
    Year = 1
    Quarter = 2


class Statements(Enum):
    Profile = 1
    Income = 2
    BalanceSheet = 3
    # CashFlow = 4
    # KeyMetrics = 5


Profile = namedtuple('Profile', ['mktCap', 'lastDiv', 'country', 'industry', 'currency', 'exchange'])

Income = namedtuple('Income', ['Date', 'Revenue', 'CostOfRevenue', 'GrossProfit', 'RnDExpenses',
                               'GAExpense', 'SaMExpense', 'OperatingExpenses',
                               'OperatingIncome', 'InterestExpense',
                               'NetIncome', 'EBITDA', 'EBITratio'])

BalanceSheet = namedtuple('BalanceSheet',
                          ['Date', 'CashAndCashEquivalents', 'ShortTermInvestments', 'Receivables',
                           'PropertyPlantAndEquipmentNet', 'GoodwillAndIntangibleAssets',
                           'LongTermInvestments', 'TaxAssets', 'TotalNonCurrentAssets', 'TotalAssets', 'Payables',
                           'ShortTermDebt', 'TotalDebt', 'TotalLiabilities',
                           'DeferredRevenue', 'NetDebt'])


# CashFlow = namedtuple('CashFlow', ['Date'])

# KeyMetrics = namedtuple('KeyMetrics', ['Date', 'MarketCap', 'Dividend'])

TickerData = namedtuple('TickerData', ['profile', 'income_list', 'balance_sheet_list'])


def redis_key(ticker: str, year: int):
    return f'{ticker}:{year}'


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
