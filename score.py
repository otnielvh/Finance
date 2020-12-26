from common.utils import TickerData, Period
from typing import List
from datetime import datetime
import data
from common.utils import Statements
from operator import itemgetter
from joblib import Parallel, delayed
from collections import namedtuple

THREADS = 200

ScoreEntry = namedtuple('Score', ['ticker', 'grossProfitGrowth', 'incomeGrowth', 'RnDRatio', 'cashPerDebt',
                                  'netIncome', 'mktCap'])


class BaseScore:

    def __init__(self, ticker_list: List[str], start_date: datetime, end_date: datetime):
        self.ticker_list = ticker_list
        self.start_date = start_date
        self.end_date = end_date
        self.score_list = []

    def filter_by_date(self, income_list: List[data.Income]) -> List[data.Income]:
        new_income_list: List[data.Income] = []
        for income in income_list:
            try:
                current_date = datetime.strptime(income.Date, data.DATE_FORMAT)
                if self.start_date <= current_date <= self.end_date:
                    new_income_list.append(income)
            except ValueError:
                print(f'ValueError: could not parse {income.date}')
        return new_income_list

    def compute_score(self):
        """

        :return: List where each row contains the ticker name and a scores (maybe more than 1)
        """

        score_list: [ScoreEntry] = Parallel(n_jobs=THREADS, prefer="threads")(
            delayed(self.process_ticker)(ticker) for ticker in self.ticker_list)

        self.score_list: [ScoreEntry] = [score for score in score_list if score]
        self.filter()
        self.sort()

    def score(self, ticker: str, ticker_data: TickerData) -> ScoreEntry:
        raise Exception("Unimplemented exception")

    def filter(self) -> None:
        pass

    def sort(self):
        self.score_list.sort()

    def process_ticker(self, ticker) -> ScoreEntry:
        financial_dict = {}
        try:
            for statement_type in [Statements.Income, Statements.BalanceSheet]:
                data_by_year = data.get_financials(ticker, statement=statement_type, period=Period.Year)
                data_until_today = self.filter_by_date(data_by_year)
                financial_dict[statement_type] = data_until_today

            ticker_data = TickerData(
                profile=data.get_financials(ticker, statement=Statements.Profile, period=Period.Year),
                income_list=financial_dict[Statements.Income],
                balance_sheet_list=financial_dict[Statements.BalanceSheet],
                # cash_flow_list=financial_dict[Statements.CashFlow]
            )
            return self.score(ticker, ticker_data)
        except Exception as e:
            print(f'Error processing {ticker!r}: {e}')


class ScoreExample(BaseScore):

    def score(self, ticker: str, ticker_data: TickerData) -> ScoreEntry:
        """
        Example of a score algorithm. To make your own score algorithm you can change the code here, or sub-class
        the BaseScore class and implement the score method

        :param ticker_data:
        :param ticker:
        :return: a tuple
        """
        rnd_score = 0.0
        debt_score = 0

        income_list = ticker_data.income_list
        balance_sheet_list = ticker_data.balance_sheet_list
        for i in range(len(income_list)):

            try:
                debt_score += float(balance_sheet_list[i].TotalAssets) / max(
                    float(balance_sheet_list[i].TotalLiabilities),
                    float(balance_sheet_list[i].TotalAssets) / 5)  # handle case of zero or very low debt for one year
                rnd_score += float(income_list[i].RnDExpenses) / float(income_list[i].OperatingExpenses)

            except IndexError:
                print(f'index {i!r} out of bounds for {ticker!r}')
            except ZeroDivisionError:
                print(f'{ticker!r} revenue is zero for {income_list[i].Date}')

        return ScoreEntry(
            ticker=ticker,
            grossProfitGrowth=avg_growth(ticker, income_list, 'GrossProfit'),
            incomeGrowth=avg_growth(ticker, income_list, 'NetIncome'),
            RnDRatio=rnd_score / max(len(income_list), 1),
            cashPerDebt=debt_score / max(len(income_list), 1),
            netIncome=average(ticker, income_list, 'NetIncome'),
            mktCap=ticker_data.profile.mktCap
        )

    def sort(self):
        self.score_list = sorted(self.score_list, key=itemgetter(1))

    def filter(self):
        filtered_list: [ScoreEntry] = []
        for score in self.score_list:
            if (1.25 < score.grossProfitGrowth < 1.5
                    and 0.25 < score.RnDRatio < 0.7):
                # and 0.2 < score.RnDRatio < 0.7
                # and 0.41 < score.cashPerDebt
                # and 0 < score.netIncome
                filtered_list.append(score)
        self.score_list = filtered_list


def avg_growth(ticker: str, my_list: List, field: str) -> float:
    acc_growth = 1
    for i in range(len(my_list) - 1):
        start_data = my_list[i]
        end_data = my_list[i+1]

        start = float(start_data._asdict().get(field))
        end = float(end_data._asdict().get(field))
        if end != 0:
            acc_growth += (end - start) / start
        else:
            print(f'ticker {ticker!r} {field} is zero for {end_data.Date}')
            acc_growth += 1
    return acc_growth / max(len(my_list) - 1.0, 1.0)


def average(ticker: str, my_list: List, field: str) -> float:
    my_sum: float = 0
    for i in range(len(my_list)):
        my_sum += float(my_list[i]._asdict().get(field))
    return my_sum / max(len(my_list), 1)
