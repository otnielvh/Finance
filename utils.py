from enum import Enum
from collections import namedtuple


class Period(Enum):
    Year = 1
    Quarter = 2


class Statements(Enum):
    Profile = 1
    Income = 2
    BalanceSheet = 3
    CashFlow = 4
    KeyMetrics = 5


Profile = namedtuple('Profile', ['mktCap', 'lastDiv', 'country', 'industry'])

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

TickerData = namedtuple('TickerData', ['profile', 'income_list', 'balance_sheet_list', 'cash_flow_list'])
