from datetime import datetime
from src.algorithm.score import ScoreExample, Filter, SCORE_ENTRY_KEYS
from src.data.data_services import DataServices
from flask import Flask, request
from src.algorithm.stock_list import LONG_TICKER_LIST
from typing import List, Dict
import logging

algo = Flask(__name__)

SHORT_TICKER_LIST = [
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

BUY_DATE = datetime(2018, 2, 1)
SELL_DATE = datetime(2020, 4, 26)
FINANCE_START_DATE = datetime(2016, 2, 1)
FINANCE_END_DATE = datetime(2018, 2, 1)


def gain_from_buy_and_sell(ticker: str, start: datetime, end: datetime) -> float:
    ds = DataServices()
    start_price = ds.get_ticker_price(ticker, start)
    end_price = ds.get_ticker_price(ticker, end)
    if start_price:
        return end_price / start_price
    else:
        return 0


def get_scores(filter_params: List[Filter], short_list: bool = False) -> List:
    """
    Returns a list of tickers with their scores (after filtering)
    :return:
    """
    ticker_list = SHORT_TICKER_LIST if short_list else LONG_TICKER_LIST
    algo_score = ScoreExample(ticker_list, FINANCE_START_DATE, FINANCE_END_DATE)
    algo_score.compute_score(filter_params)
    response = []
    for score_entry in algo_score.score_list:
        ticker = score_entry.ticker
        gain = gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)
        entry = {name: value for name, value in score_entry._asdict().items()}
        entry['gain'] = gain
        response.append(entry)
    return response


def main(filter_params: List[Filter]):
    score_list = get_scores(filter_params, short_list=True)
    if not score_list:
        print('No stocks match the filter')
        return

    print("successfully retrieved data")
    print_table(score_list)


def print_table(score_list):
    column_spacing = '\t\t'

    # compare high score stocks to lows score stocks performance
    title = f'ticker\tgain\t{column_spacing}'
    for name in score_list[0].keys():
        if name not in ['ticker', 'gain']:
            title += f'{name}{column_spacing}'

    print(title)

    sum_gain = 0
    for score_entry in score_list:
        ticker = score_entry.get('ticker')
        try:
            gain = score_entry.get('gain')
            sum_gain += gain
            score_line = f'{ticker:>5}\t{gain*100:>7.2f}%'
            for name, value in score_entry.items():
                if name not in ['ticker', 'gain']:
                    s = len(name)
                    if abs(value) < 10 ** 3:
                        score_line += f'{value:{s}.2f} {column_spacing}'
                    elif abs(value) < 10 ** 6:
                        score_line += f'{value/(10 ** 3):{s}.0f}K{column_spacing}'
                    elif abs(value) < 10 ** 9:
                        score_line += f'{value/(10 ** 6):{s}.0f}M{column_spacing}'
                    else:
                        score_line += f'{value/(10 ** 9):{s}.0f}B{column_spacing}'
            print(score_line)
        except Exception as e:
            print(f'Error handling {ticker!r}: {e}')
    # Index gains
    for ticker in INDEX_LIST:
        gain = gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)
        print(f'{ticker:>4}\t{gain*100:.2f}%')

    avg_gain = sum_gain / len(score_list)
    print(f'avg \t{avg_gain*100:.2f}%')


def calc_stats(score_list: List[Dict]) -> Dict:
    avg_score = sum(s.get('gain') for s in score_list)/len(score_list)
    index_list = [{ticker: gain_from_buy_and_sell(ticker, BUY_DATE, SELL_DATE)}
                  for ticker in INDEX_LIST]
    return {
        'score_list': score_list,
        'avg_gain': avg_score,
        'index_gains': index_list
    }


@algo.route('/api/ticker-scores', methods=['GET'])
def get_all_scores():
    is_short_list = request.args.get('short_list', '').lower() == 'true'
    score_list = get_scores([], is_short_list)
    return calc_stats(score_list)


@algo.route('/api/ticker-scores', methods=['POST'])
def get_ticker_scores():
    data = request.json
    logging.info(f' Received request: POST /filter {data}')
    filter_params: List[Filter] = []
    for my_filter in data.get('filters', []):
        # TODO: add input validation
        filter_params.append(
            Filter(
                my_filter.get('name'),
                float(my_filter.get('min')),
                float(my_filter.get('max'))
            )
        )

    is_short_list = request.args.get('short_list', '').lower() == 'true'
    score_list = get_scores(filter_params, is_short_list)
    return calc_stats(score_list)


@algo.route('/api/filters', methods=['GET'])
def get_filters():
    return {'filters': SCORE_ENTRY_KEYS}


if __name__ == "__main__":
    filter_list = [Filter('RnDRatio', 0.25, 0.7),
                   Filter('grossProfitGrowth', 1.25, 1.7)]
    main(filter_list)
