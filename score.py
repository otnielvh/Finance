from utils import Income, BalanceSheet, CashFlow, KeyMetrics, Period
from typing import Tuple, List
from datetime import datetime
import data
from utils import Statements
from operator import itemgetter
from joblib import Parallel, delayed

THREADS = 200


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

        score_list = Parallel(n_jobs=THREADS, prefer="threads")(delayed(self.process_ticker)(ticker) for ticker in self.ticker_list)

        self.score_list = [score for score in score_list if score]
        self.filter()
        self.sort()

    def score(self, ticker: str, income: Income = None, balance_sheet: BalanceSheet = None,
              cash_flow: CashFlow = None, key_metrics: KeyMetrics = None) -> Tuple:
        raise Exception("Unimplemented exception")

    def filter(self) -> None:
        pass

    def sort(self):
        self.score_list.sort()

    def process_ticker(self, ticker):
        financial_dict = {}
        try:
            for statement_type in [Statements.Income, Statements.BalanceSheet, Statements.CashFlow]:
                data_by_year = data.get_financials(ticker, statement=statement_type, period=Period.Year)
                data_until_today = self.filter_by_date(data_by_year)
                financial_dict[statement_type] = data_until_today

            score = self.score(ticker, financial_dict[Statements.Income], financial_dict[Statements.BalanceSheet],
                               financial_dict[Statements.CashFlow])
            return(ticker, *score)
        except Exception as e:
            print(f'Error processing {ticker!r}: {e}')


class ScoreExample(BaseScore):

    def score(self, ticker: str, income_list: Income = None, balance_sheet_list: BalanceSheet = None,
              cash_flow_list: CashFlow = None, key_metrics: KeyMetrics = None) -> Tuple:
        """
        Example of a score algorithm. To make your own score algorithm you can change the code here, or sub-class
        the BaseScore class and implement the score method

        :param ticker:
        :param income_list:
        :param balance_sheet_list:
        :param cash_flow_list:
        :param key_metrics:
        :return: a tuple
        """
        growth_score = 0.0
        rnd_score = 0.0
        debt_score = 0
        net_income_score = 0
        income_growth_score = 0

        for i in range(len(income_list)):
            try:
                growth_score += (float(income_list[i + 1].GrossProfit) - float(income_list[i].GrossProfit)) / float(
                    income_list[i].GrossProfit)
                debt_score += float(balance_sheet_list[i].TotalAssets) / float(balance_sheet_list[i].TotalLiabilities)
                rnd_score += float(income_list[i].RnDExpenses) / float(income_list[i].OperatingExpenses)
                net_income_score += float(income_list[i].NetIncome)
                income_growth_score += (float(income_list[i + 1].NetIncome) - float(income_list[i].NetIncome)) / float(
                    income_list[i].NetIncome)
            except IndexError:
                pass
            except ZeroDivisionError:
                print(f'{ticker!r} revenue is zero for {income_list[i].Date}')
            except ValueError:
                pass
        normalized_growth_score = growth_score / max(len(income_list) - 1, 1)
        normalized_rnd_score = rnd_score / max(len(income_list), 1)
        normalized_debt_score = debt_score / max(len(income_list), 1)
        normalized_net_income_score = net_income_score / max(len(income_list), 1)
        normalized_income_growth_score = income_growth_score / max(len(income_list) - 1, 1)
        return (normalized_growth_score, normalized_rnd_score, normalized_debt_score, normalized_net_income_score,
               normalized_income_growth_score, len(income_list))

    def sort(self):
        self.score_list = sorted(self.score_list, key=itemgetter(1))

    def filter(self):
        filtered_list = []
        for score in self.score_list:
            if 0.2 < score[1] < 0.5 and 0.2 < score[2] < 0.7 and 0.41 < score[3]: # < 10000 and score[4] > 0 and score[5] > 0:
                filtered_list.append(score)
        self.score_list = filtered_list

