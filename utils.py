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

BalanceSheet = namedtuple('BalanceSheet',
                          ['Date', 'CashAndCashEquivalents', 'ShortTermInvestments', 'Receivables', 'Inventories'
                           'TotalCurrentAssets', 'PropertyPlantAndEquipmentNet', 'GoodwillAndIntangibleAssets',
                           'LongTermInvestments', 'TaxAssets', 'TotalNonCurrentAssets', 'TotalAssets', 'Payables',
                           'ShortTermDebt', 'TotalDebt', 'DeferredRevenue', 'TaxLiabilities', 'DepositLiabilities',
                           'TotalNonCurrentLiabilities', 'TotalLiabilities', 'OtherComprehensiveIncome',
                           'RetainedEarnings', 'TotalShareholdersEquity', 'Investments', 'NetDebt', 'OtherAssets',
                           'OtherLiabilities', 'TotalCurrentLiabilities', 'CashAndShortTermInvestments'])


CashFlow = namedtuple('CashFlow', ['Date'])

KeyMetrics = namedtuple('KeyMetrics', ['Date', 'MarketCap', 'Dividend'])
