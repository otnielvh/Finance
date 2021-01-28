from typing import List
import logging


def avg_growth(ticker: str, my_list: List, field: str) -> float:
    acc_growth = 0
    count = 0
    for i in range(len(my_list) - 1):
        start_data = my_list[i]
        end_data = my_list[i+1]
        try:
            start = start_data._asdict().get(field)
            end = end_data._asdict().get(field)
            if start and end:
                acc_growth += (float(end) / float(start)) - 1
                count += 1
            else:
                logging.info(f'ticker {ticker!r} {field} is None or zero for {start_data.Date} or {end_data.Date}')
        except Exception as e:
            logging.error(f'failed to process ticker {ticker} field {field} -> {e}')
    return 1 + (acc_growth / count) if count > 0 else 0


def average(my_list: List, field: str) -> float:
    my_sum: float = 0
    count = 0
    for i in range(len(my_list)):
        data_point = my_list[i]._asdict().get(field)
        if data_point:
            my_sum += float(data_point)
            count += 1
    return my_sum / count if count else 0.0
