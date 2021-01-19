from common.utils import *
from typing import Dict, List
from common import data_access
import loaddata


SUPPORTED_STOCK_EXCHANGES = ['NASDAQ Capital Market', 'NASDAQ Global Market', 'NYSE', 'NYSE American', 'NYSE Arca',
                             'NYSEArca', 'Nasdaq', 'Nasdaq Global Select', 'NasdaqGM', 'NasdaqGS',
                             'New York Stock Exchange']


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


# TODO: get years dynamically
def get_financials(ticker: str, from_year: int = 2016, to_year: int = 2019,
                   statement: Statements = Statements.Income,
                   period: Period = Period.Year) -> List[Income]:

    resp = loaddata.get_ticker_data(ticker, from_year, to_year)
    fin_by_year = []
    for year in range(from_year, to_year):
        element = resp.get(str(year))
        if element:
            element['date'] = str(year)
            fin_by_year.append(element)

    financial_list = []

    if statement == Statements.Income:
        financial_list = [dict2income(d) for d in fin_by_year]
    elif statement == Statements.BalanceSheet:
        financial_list = [dict2balance_sheet(d) for d in fin_by_year]

    return financial_list


def get_ticker_list() -> List[str]:
    return data_access.get_ticker_list()
