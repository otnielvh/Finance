from utils import IncomeCol, Period, Statements
from typing import Dict, List
import requests
from datetime import datetime
import redis
import json

DATE_FORMAT = '%Y-%m-%d'
REDIS_HOST_NAME = 'localhost'
REDIS_PORT = 6379


r = redis.Redis(
    host=REDIS_HOST_NAME,
    port=REDIS_PORT)


def get_cached_url(url) -> Dict:
    """ Get URL from cache. If URL not in cache, get from source url and cache the response """
    try:
        resp = r.get(url)
        if resp is not None:
            return json.loads(resp)
    except redis.exceptions.ConnectionError:
        pass

    resp = requests.get(url).json()

    try:
        r.set(url, json.dumps(resp))
    except redis.exceptions.ConnectionError:
        pass

    return resp


def dict2income(d: Dict) -> IncomeCol:
    return IncomeCol(
        Date=d.get('date'),
        Revenue=d.get('Revenue'),
        CostOfRevenue=d.get('Cost of Revenue'),
        GrossProfit=d.get('Gross Profit'),
        RnDExpenses=d.get('R&D Expenses'),
        SGAExpense=d.get('SG&A Expense'),
        OperatingExpenses=d.get('Operating Expenses'),
        OperatingIncome=d.get('Operating Income'),
        InterestExpense=d.get('Interest Expense'),
        NetIncome=d.get('Net Income'),
        EBITDA=d.get('EBITDA'),
        EBIT=d.get('EBIT')
    )


def statements2url(statement: Statements) -> str:
    d = {
        Statements.Income: 'income-statement',
        Statements.BalanceSheet: 'balance-sheet-statement',
        Statements.CashFlow: 'cash-flow-statement'
    }
    return d[statement]


def get_financials(ticker: str, statement: Statements = Statements.Income,
                   period: Period = Period.Year) -> List[IncomeCol]:

    url = f'https://financialmodelingprep.com/api/v3/financials/{statements2url(statement)}/{ticker}/'
    if period == Period.Quarter:
        url += '?period=quarter'

    resp = get_cached_url(url)

    financial_list = [dict2income(d) for d in resp['financials']]
    financial_list.reverse()
    return financial_list


def get_ticker_list():
    url = 'https://financialmodelingprep.com/api/v3/company/stock/list'
    return requests.get(url).json()['symbolsList']  # list of dictionaries


def get_prices(ticker: str, start: datetime, end: datetime) -> List:
    # date format: 2018 - 03 - 12
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    url = f'https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_str}&to={end_str}'
    resp = get_cached_url(url)
    return resp.get('historical', [])
