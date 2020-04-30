import pprint
from typing import List
from utils import Period, IncomeCol
import data
from datetime import datetime
import simulator

TICKER = 'vrtx'
TICKER_LIST = ['pg', 'aig', 'rtx', 'CVX', 'czr', 'SPLK', 'aapl', 'goog', 'msft', 'amzn', 'tsla', 'sedg', 'teva', 'vrtx']
INDEX_LIST = ['qqq', 'spy']
PERIOD = Period.Year

pp = pprint.PrettyPrinter(indent=4)


def get_revenue_thousands(ticker: str, period: Period = Period.Year) -> List:
    def filter(y: IncomeCol):
        return y.Date, f'{int(float(y.Revenue) / 1000):,}', f'{int(float(y.OperatingExpenses) / 1000):,}'
    return _get_revenue_filter(ticker, period, filter)


def _get_revenue_filter(ticker: str, period: Period, user_filter) -> List:
    return [user_filter(x) for x in data.get_financials(ticker, period=period)]


def main():

    # pp.pprint(get_revenue_thousands(TICKER, period=PERIOD))

    # calculate gain
    # start_date = datetime(2016, 4, 25)
    # end_date = datetime(2019, 4, 29)
    # gain = simulator.gain_from_buy_and_sell(TICKER, start_date, end_date)
    # print(f'gains are:  {gain * 100:.2f}%')

    # pp.pprint(simulator.remove_dates_newer_than_today(data.get_financials(TICKER), datetime(2016, 4, 25)))

    score_list = simulator.get_growth_score(TICKER_LIST, datetime(2017, 1, 1))
    start_date = datetime(2017, 2, 13)
    end_date = datetime(2018, 4, 27)

    # compare high score stocks to lows score stocks performance
    print('ticker\tscore\tgain')
    for ticker, score in score_list:
        gain = simulator.gain_from_buy_and_sell(ticker, start_date, end_date)
        print(f'{ticker:>4}\t{score:.2f}\t{gain*100:.2f}%')

    # Index gains
    for ticker in INDEX_LIST:
        gain = simulator.gain_from_buy_and_sell(ticker, start_date, end_date)
        print(f'{ticker:>4}\t\t\t{gain*100:.2f}%')

main()
