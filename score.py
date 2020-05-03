from utils import Income, BalanceSheet, CashFlow, KeyMetrics, Period
from typing import Tuple, List
from datetime import datetime
import data
from utils import Statements


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
        score_list: List[Tuple] = []

        for ticker in self.ticker_list:
            financial_dict = {}
            try:
                for statement_type in [Statements.Income, Statements.BalanceSheet, Statements.CashFlow]:
                    data_by_year = data.get_financials(ticker, statement=statement_type, period=Period.Year)
                    data_until_today = self.filter_by_date(data_by_year)
                    financial_dict[statement_type] = data_until_today

                score = self.score(ticker, financial_dict[Statements.Income], financial_dict[Statements.BalanceSheet],
                                   financial_dict[Statements.CashFlow])
                score_list.append((ticker, *score))
            except Exception as e:
                print(f'Error processing {ticker!r}: {e}')
        self.score_list = score_list

    def score(self, ticker: str, income: Income = None, balance_sheet: BalanceSheet = None,
              cash_flow: CashFlow = None, key_metrics: KeyMetrics = None) -> Tuple:
        raise Exception("Unimplemented exception")

    def sort(self):
        self.score_list.sort()


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

        for i in range(len(income_list)):
            try:
                growth_score += (float(income_list[i + 1].GrossProfit) - float(income_list[i].GrossProfit)) / float(
                    income_list[i].GrossProfit)
                debt_score += float(balance_sheet_list[i].TotalAssets) / float(balance_sheet_list[i].TotalLiabilities)
                rnd_score += float(income_list[i].RnDExpenses) / float(income_list[i].OperatingExpenses)
            except IndexError:
                pass
            except ZeroDivisionError:
                print(f'{ticker!r} revenue is zero for {income_list[i].Date}')
            except ValueError:
                pass
        normalized_growth_score = growth_score / max(len(income_list) - 1, 1)
        normalized_rnd_score = rnd_score / max(len(income_list), 1)
        normalized_debt_score = debt_score / max(len(income_list), 1)
        return normalized_growth_score, normalized_rnd_score, normalized_debt_score
