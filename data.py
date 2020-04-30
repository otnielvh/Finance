from utils import IncomeCol, Period, Statements
from typing import Dict, List
import requests
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d'

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

    resp = requests.get(url)

    financial_list = [dict2income(d) for d in resp.json()['financials']]
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
    resp = requests.get(url)
    return resp.json()['historical']
