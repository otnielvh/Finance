import logging
from common.utils import *
from typing import Dict, List
import requests
from datetime import datetime
import time
import redis
import json
import csv
from common import config

API_KEY = 'Demo'
DATE_FORMAT = '%Y-%m-%d'
SYMBOLS_PATH = '../assets/nasdaq_symbols.csv'
BASE_URL_V3 = 'https://financialmodelingprep.com/api/v3'
r = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True

)


SUPPORTED_STOCK_EXCHANGES = ['NASDAQ Capital Market', 'NASDAQ Global Market', 'NYSE', 'NYSE American', 'NYSE Arca',
                             'NYSEArca', 'Nasdaq', 'Nasdaq Global Select', 'NasdaqGM', 'NasdaqGS',
                             'New York Stock Exchange']


def get_cached_url(url, params) -> Dict:
    """ Get URL from cache. If URL not in cache, get from source url and cache the response """
    try:
        redis_key = url
        for key, val in params.items():
            if key != 'apikey':
                redis_key += f'--{key}:{val}'
        redis_resp = r.get(redis_key)
        if redis_resp is not None:
            return json.loads(redis_resp)
    except redis.exceptions.ConnectionError:
        pass

    resp = requests.get(url, params=params)
    counter = 0
    while resp.status_code == 429:
        seconds = resp.json().get('X-Rate-Limit-Retry-After-Seconds', 0) + 1
        print(f'received 429: sleeping for {seconds} for the {counter}th time')
        time.sleep(seconds)
        resp = requests.get(url, params=params)
        counter += 1

    resp.raise_for_status()

    data = resp.json()

    try:
        r.set(redis_key, json.dumps(data))
    except redis.exceptions.ConnectionError:
        pass

    return data


def dict2profile(d: Dict) -> Profile:
    return Profile(
        mktCap=d.get('mktCap'),
        lastDiv=d.get('lastDiv'),
        country=d.get('country'),
        industry=d.get('industry'),
        currency=d.get('currency'),
        exchange=d.get('exchangeShortName')
    )


def dict2income(d: Dict) -> Income:
    return Income(
        Date=d.get('date'),
        Revenue=None,
        CostOfRevenue=None,
        GrossProfit=d.get('grossprofit'),
        RnDExpenses=d.get('researchanddevelopmentexpense'),
        GAExpense=None,
        SaMExpense=d.get('sellinggeneralandadministrativeexpense'),
        OperatingExpenses=d.get('operatingexpenses'),
        OperatingIncome=d.get('operatingincomeloss'),
        InterestExpense=None,
        NetIncome=d.get('netincomeloss'),
        EBITDA=None,
        EBITratio=None
    )


def dict2balance_sheet(d: Dict) -> BalanceSheet:
    return BalanceSheet(
        Date=d.get('date'),
        CashAndCashEquivalents=d.get('cashAndCashEquivalents'),
        ShortTermInvestments=d.get('shortTermInvestments'),
        Receivables=d.get('netReceivables'),
        # Inventories=d.get('Inventories', ''),
        # TotalCurrentAssets=d.get('Total current assets'),
        PropertyPlantAndEquipmentNet=d.get('propertyPlantEquipmentNet'),
        GoodwillAndIntangibleAssets=d.get('goodwillAndIntangibleAssets'),
        LongTermInvestments=d.get('longTermInvestments'),
        TaxAssets=d.get('taxAssets'),
        TotalNonCurrentAssets=d.get('totalNonCurrentAssets'),
        TotalAssets=d.get('totalAssets'),
        Payables=d.get('accountPayables'),
        ShortTermDebt=d.get('shortTermDebt'),
        # LongTermDebt=d.get('Long-term debt'),
        TotalLiabilities=d.get('totalLiabilities'),
        TotalDebt=d.get('totalDebt'),
        DeferredRevenue=d.get('deferredRevenue'),
        NetDebt=d.get('netDebt'),
    )


# def dict2cash_flow(d: Dict) -> CashFlow:
#     return CashFlow(
#         Date=d.get('date'),
#         #TODO: fill in
#     )


def getUrl(statement: Statements) -> str:
    d = {
        Statements.Profile: 'profile',
        Statements.Income: 'income-statement',
        Statements.BalanceSheet: 'balance-sheet-statement',
        # Statements.CashFlow: 'cash-flow-statement'
    }
    return d[statement]


# TODO: get years dynamically
def get_financials(ticker: str, from_year: int = 2016, to_year: int = 2019,
                   statement: Statements = Statements.Income,
                   period: Period = Period.Year) -> List[Income]:

    fin_by_year = []
    for year in range(from_year, to_year + 1):
        resp = r.hgetall(f'{ticker}:{year}')
        resp['date'] = year
        fin_by_year.append(resp)

    financial_list = []
    if statement == Statements.Income:
        financial_list = [dict2income(d) for d in fin_by_year]
    elif statement == Statements.BalanceSheet:
        financial_list = [dict2balance_sheet(d) for d in fin_by_year]

    return financial_list


def get_ticker_list() -> List[str]:
    ticker_list_resp = r.sscan(REDIS_TICKER_SET, 0, count=30 * 1000)
    if ticker_list_resp[0] == 0:  # i.e. status OK
        return ticker_list_resp[1]
    else:
        logging.error('failed to load ticker list')


def get_prices(ticker: str, start: datetime, end: datetime) -> List:
    # date format: 2018 - 03 - 12
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    url = f'{BASE_URL_V3}/historical-price-full/{ticker}'
    params ={
        'from': start_str,
        'to': end_str,
        'apikey': API_KEY
    }
    resp = get_cached_url(url, params)
    return resp.get('historical', [])


def get_symbols():
    symbols = []
    nasdaq_symbol_pos = -1
    etf_pos = 4
    with open(SYMBOLS_PATH) as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        next(reader)
        for row in reader:
            if row[etf_pos] == "N":  # not an ETF
                symbols.append(row[nasdaq_symbol_pos])
    return symbols
