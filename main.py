from common.utils import Period
from datetime import datetime
from score import ScoreExample
import data

TICKER_LIST = ['cpe', 'payc', 'aal', 'pg', 'aig', 'rtx', 'CVX', 'czr', 'SPLK', 'aapl', 'goog', 'msft', 'amzn',
               'tsla', 'sedg', 'now', 'teva', 'vrtx', 'PFG', 'RCL', 'HAL', 'NVS', 'LIN', 'c', 'rtx']

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
    title = 'ticker\tgain\t\t'
    for name in algo_score.score_list[0]._asdict().keys():
        if name != 'ticker':
            title += f'{name}\t\t'
    print(title)

    sum_gain = 0
    for scoreEntry in algo_score.score_list:
        ticker = scoreEntry.ticker
        try:
            gain = gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)
            sum_gain += gain
            scoreLine = f'{ticker:>4}\t{gain*100:>7.2f}%\t\t'
            for name, value in scoreEntry._asdict().items():
                if name != 'ticker':
                    if value < 10 ** 3:
                        scoreLine += f'{value:6.2f}  \t\t'
                    elif value < 10 ** 6:
                        scoreLine += f'{value/(10 ** 3):6.0f}K\t\t'
                    elif value < 10 ** 9:
                        scoreLine += f'{value/(10 ** 6):6.0f}M\t\t'
                    else:
                        scoreLine += f'{value/(10 ** 9):6.0f}B\t\t'
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

