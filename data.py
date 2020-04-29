from utils import IncomeCol, Period, Statements
from typing import Dict, List
import requests


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
                   period: Period = Period.Year) -> List:

    url = f'https://financialmodelingprep.com/api/v3/financials/{statements2url(statement)}/{ticker}/'
    if period == Period.Quarter:
        url += '?period=quarter'

    resp = requests.get(url)

    return [dict2income(d) for d in resp.json()['financials']]


def get_ticker_list():
    url = 'https://financialmodelingprep.com/api/v3/company/stock/list'
    return requests.get(url).json()['symbolsList']  # list of dictionaries
