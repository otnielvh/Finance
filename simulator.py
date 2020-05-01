import data
from datetime import datetime
from typing import List, Tuple
from utils import Period
from dateutil.relativedelta import relativedelta

DEFAUTL_YEARS_BACK = 4

def _growth_score(income_list: List[data.IncomeCol]):
    '''
    Call back function used in get ticker score
    :param income_list:
    :return:
    '''
    growth_score = 0.0
    rnd_score = 0.0

    for i in range(len(income_list)):
        try:
            growth_score += (float(income_list[i+1].GrossProfit) - float(income_list[i].GrossProfit)) / float(income_list[i].GrossProfit)
            rnd_score += float(income_list[i].RnDExpenses) / float(income_list[i].OperatingExpenses)
        except IndexError:
            pass
        except ZeroDivisionError:
            print(f'revenue is zero for {income_list[i].Date}')
        except ValueError:
            pass
    normalized_growth_score = growth_score/ max(len(income_list) - 1, 1)
    normalized_rnd_score = rnd_score / max(len(income_list), 1)
    return (normalized_growth_score, normalized_rnd_score)


def filter_by_date(income_list: List[data.IncomeCol], start_date: datetime, end_date: datetime) -> List[data.IncomeCol]:
    new_income_list: List[data.IncomeCol] = []
    for income in income_list:
        try:
            current_date = datetime.strptime(income.Date, data.DATE_FORMAT)
        except ValueError:
            continue
        if start_date <= current_date <= end_date:
            new_income_list.append(income)
    return new_income_list


def get_growth_score(ticker_list: List[str], today: datetime):
    return get_ticker_score(ticker_list, today - relativedelta(years=DEFAUTL_YEARS_BACK), today, score_fun=_growth_score)


def get_ticker_score(ticker_list: List[str], start_date: datetime, end_date: datetime, score_fun):
    score_list: List[Tuple[str, int]] = []

    for ticker in ticker_list:
        print(f'getting data for {ticker!r}')
        income_by_quarter = data.get_financials(ticker, period=Period.Year)
        income_until_today = filter_by_date(income_by_quarter, start_date, end_date)
        score = score_fun(income_until_today)
        score_list.append((ticker, score))
    return score_list


def gain_from_buy_and_sell(ticker: str, start: datetime, end: datetime) -> float:
    start_data = data.get_prices(ticker, start, start)[0]
    end_data = data.get_prices(ticker, end, end)[0]
    # TODO: consider better pricing startegy
    start_price = float(start_data.get('open'))
    end_price = float(end_data.get('open'))
    return (end_price - start_price) / start_price

