from enum import Enum
from collections import namedtuple


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


def redis_key(name: str, year: int):
    return f'{name.replace(" ", "-")}:{year}'
