from .score_functions import avg_growth
from .utils import dict2income
TICKER = 'tk'


def test_avg_growth_const():
    growth = 1.3
    start_year = 2015
    years = 5
    random_base = 27
    income_data_list = [
        dict(date=start_year+i, GrossProfit=random_base * (growth ** i))
        for i in range(years)
    ]

    income_data_list = [dict2income(d) for d in income_data_list]

    assert avg_growth(TICKER, income_data_list, 'GrossProfit') == growth


def test_avg_growth_variable():
    growth = [15464, 1.3, 0.7, 1.2, 1.8]
    acc_growth = [g for g in growth]
    for i in range(1, len(acc_growth)):
        acc_growth[i] = acc_growth[i-1] * acc_growth[i]
    start_year = 2015
    years = len(acc_growth)
    income_data_list = [
        dict(date=start_year+i, GrossProfit=1 * (acc_growth[i]))
        for i in range(years)
    ]

    income_data_list = [dict2income(d) for d in income_data_list]

    assert avg_growth(TICKER, income_data_list, 'GrossProfit') == (sum(growth[1:]) / len(growth[1:]))
