from enum import Enum
from collections import namedtuple


class Period(Enum):
    Year = 1
    Quarter = 2


class Statements(Enum):
    Income = 1
    BalanceSheet = 2
    CashFlow = 3


Income = namedtuple('Income', ['Date', 'Revenue', 'CostOfRevenue', 'GrossProfit', 'RnDExpenses',
                                     'SGAExpense', 'OperatingExpenses', 'OperatingIncome', 'InterestExpense',
                                     'NetIncome', 'EBITDA', 'EBIT'])

BalanceSheet = namedtuple('BalanceSheet', ['Date'])

CashFlow = namedtuple('CashFlow', ['Date'])

KeyMetrics = namedtuple('KeyMetrics', ['Date', 'MarketCap', 'Dividend'])
