import pprint
from typing import List
from utils import Period, IncomeCol
import data
from datetime import datetime
import simulator

TICKER = 'vrtx'
PERIOD = Period.Year

pp = pprint.PrettyPrinter(indent=4)


def get_revenue_thousands(ticker: str, period: Period = Period.Year) -> List:
    def filter(y: IncomeCol):
        return y.Date, f'{int(float(y.Revenue) / 1000):,}', f'{int(float(y.OperatingExpenses) / 1000):,}'
    return _get_revenue_filter(ticker, period, filter)


def _get_revenue_filter(ticker: str, period: Period, user_filter) -> List:
    return [user_filter(x) for x in data.get_financials(ticker, period=period)]


def main():

    pp.pprint(get_revenue_thousands(TICKER, period=PERIOD))

    # calculate gain
    start_date = datetime(2016, 4, 25)
    end_date = datetime(2019, 4, 29)
    gain = simulator.simulator(TICKER, start_date, end_date)
    print(f'gains are:  {gain * 100:.2f}%')


main()
