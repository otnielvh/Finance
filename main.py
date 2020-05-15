from utils import Period
from datetime import datetime
from score import ScoreExample
import data
import pprint as pp

TICKER_LIST = ['cpe', 'payc', 'aal', 'pg', 'aig', 'rtx', 'CVX', 'czr', 'SPLK', 'aapl', 'goog', 'msft', 'amzn',
               'tsla', 'sedg', 'now', 'teva', 'vrtx', 'PFG', 'RCL', 'HAL', 'NVS', 'LIN', 'c', 'rtx']
# TICKER_LIST = ['aapl', 'amzn']
INDEX_LIST = ['qqq', 'spy']
PERIOD = Period.Year

BUY_DATE = datetime(2016, 2, 17)
SELL_DATE = datetime(2019, 4, 26)
FINANCE_START_DATE = datetime(2012, 2, 1)
FINANCE_END_DATE = datetime(2016, 2, 1)


def gain_from_buy_and_sell(ticker: str, start: datetime, end: datetime) -> float:
    start_data = data.get_prices(ticker, start, start)[0]
    end_data = data.get_prices(ticker, end, end)[0]
    # TODO: consider better pricing startegy
    start_price = float(start_data.get('open'))
    end_price = float(end_data.get('open'))
    return (end_price - start_price) / start_price


def main():
    algo_score = ScoreExample(data.get_ticker_list(), FINANCE_START_DATE, FINANCE_END_DATE)
    algo_score.compute_score()
    print("successfully retrieved data")

    # compare high score stocks to lows score stocks performance
    print('ticker\tgain\t\tgross growth\tR&D/expense\tcash/debt\tnetIncome')
    sum_gain = 0
    for row in algo_score.score_list:
        ticker = row[0]
        try:
            gain = gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)
            sum_gain += gain
            print(f'{ticker:>4}\t{gain*100:>7.2f}%\t\t\t{row[1]:.2f}\t\t{row[2]:.2f}\t\t{row[3]:.2f}\t\t{row[4]:>8.0f}'
                  f'\t\t{row[5]*100:>7.2f}%'
                  f'\t\t{row[6]}')
            # print(row, gain)
        except Exception as e:
            print(f'Error handling {ticker!r}: {e}')
    # Index gains
    for ticker in INDEX_LIST:
        gain = gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)
        print(f'{ticker:>4}\t{gain*100:.2f}%')

    avg_gain = sum_gain / len(algo_score.score_list)
    print(f'avg \t{avg_gain*100:.2f}%')


if __name__ == "__main__":
    main()

