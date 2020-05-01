import pprint
from typing import List
from utils import Period, IncomeCol
import data
from datetime import datetime
import simulator

TICKER = 'vrtx'
TICKER_LIST = ['cpe', 'payc', 'aal', 'pg', 'aig', 'rtx', 'CVX', 'czr', 'SPLK', 'aapl', 'goog', 'msft', 'amzn', 'tsla', 'sedg',
               'teva', 'vrtx']
# TICKER_LIST = ['pg', 'aig', 'rtx', 'CVX']
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

    score_list = simulator.get_growth_score(TICKER_LIST, datetime(2016, 2, 1))
    print("successfully retrieved data")
    start_date = datetime(2016, 2, 17)
    end_date = datetime(2019, 4, 24)

    # compare high score stocks to lows score stocks performance
    print('ticker\tgain\t\tgross growth\tR&D/expense')
    for ticker, score in score_list:
        gain = simulator.gain_from_buy_and_sell(ticker, start_date, end_date)
        print(f'{ticker:>4}\t{gain*100:.2f}%\t\t\t{score[0]:.2f}\t\t{score[1]:.2f}')

    # Index gains
    for ticker in INDEX_LIST:
        gain = simulator.gain_from_buy_and_sell(ticker, start_date, end_date)
        print(f'{ticker:>4}\t{gain*100:.2f}%')


if __name__ == "__main__":
    # print(data.get_cached_url('a'))
    main()

