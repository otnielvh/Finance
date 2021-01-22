from algorithm.utils import Period
from datetime import datetime
from algorithm.score import ScoreExample
from common.data_access import get_price

TICKER_LIST = [
    'splk',
    'aapl',
    'goog',
    'msft',
    'amzn',
    'tsla',
    'sedg',
    'now',
    'teva',
    'vrtx',
    'okta',
    'ddog',
    'nvda'
]

INDEX_LIST = ['qqq', 'spy']
PERIOD = Period.Year

BUY_DATE = datetime(2018, 2, 1)
SELL_DATE = datetime(2020, 4, 26)
FINANCE_START_DATE = datetime(2016, 2, 1)
FINANCE_END_DATE = datetime(2018, 2, 1)


def gain_from_buy_and_sell(ticker: str, start: datetime, end: datetime) -> float:
    start_price = get_price(ticker, start)
    end_price = get_price(ticker, end)
    if start_price:
        return end_price / start_price
    else:
        return 0


def main():
    algo_score = ScoreExample(TICKER_LIST, FINANCE_START_DATE, FINANCE_END_DATE)
    algo_score.compute_score()
    print("successfully retrieved dataload")
    column_spacing = '\t\t'

    # compare high score stocks to lows score stocks performance
    title = f'ticker\tgain\t{column_spacing}'
    for name in algo_score.score_list[0]._asdict().keys():
        if name != 'ticker':
            title += f'{name}{column_spacing}'
    print(title)

    sum_gain = 0
    for scoreEntry in algo_score.score_list:
        ticker = scoreEntry.ticker
        try:
            gain = gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)
            sum_gain += gain
            scoreLine = f'{ticker:>5}\t{gain*100:>7.2f}%'
            for name, value in scoreEntry._asdict().items():
                if name != 'ticker':
                    s = len(name)
                    if abs(value) < 10 ** 3:
                        scoreLine += f'{value:{s}.2f} {column_spacing}'
                    elif abs(value) < 10 ** 6:
                        scoreLine += f'{value/(10 ** 3):{s}.0f}K{column_spacing}'
                    elif abs(value) < 10 ** 9:
                        scoreLine += f'{value/(10 ** 6):{s}.0f}M{column_spacing}'
                    else:
                        scoreLine += f'{value/(10 ** 9):{s}.0f}B{column_spacing}'
            print(scoreLine)
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

