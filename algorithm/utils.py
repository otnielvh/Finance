from enum import Enum
from collections import namedtuple
from typing import Dict


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


