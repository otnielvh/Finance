from utils import TickerData, Statements, Period
from typing import Tuple, List
from datetime import datetime
import data
from utils import Statements
from operator import itemgetter
from joblib import Parallel, delayed
from collections import namedtuple


THREADS = 200


ScoreEntry = namedtuple('Score', ['ticker', 'grossGrowth', 'incomeGrowth', 'RnDRatio', 'cashPerDebt',
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

        score_list: [ScoreEntry] = Parallel(n_jobs=THREADS, prefer="threads")(delayed(self.process_ticker)(ticker) for ticker in self.ticker_list)

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
            for statement_type in [Statements.Income, Statements.BalanceSheet, Statements.CashFlow]:
                data_by_year = data.get_financials(ticker, statement=statement_type, period=Period.Year)
                data_until_today = self.filter_by_date(data_by_year)
                financial_dict[statement_type] = data_until_today

            ticker_data = TickerData(
                profile=data.get_financials(ticker, statement=Statements.Profile, period=Period.Year),
                income_list=financial_dict[Statements.Income],
                balance_sheet_list=financial_dict[Statements.BalanceSheet],
                cash_flow_list=financial_dict[Statements.CashFlow]
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
        growth_score = 0.0
        rnd_score = 0.0
        debt_score = 0
        net_income_score = 0
        income_growth_score = 0

        income_list = ticker_data.income_list
        balance_sheet_list = ticker_data.balance_sheet_list
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
            # except ValueError:
            #     pass

        return ScoreEntry(
            ticker=ticker,
            grossGrowth=growth_score / max(len(income_list) - 1, 1),
            incomeGrowth=income_growth_score / max(len(income_list) - 1, 1),
            RnDRatio=rnd_score / max(len(income_list), 1),
            cashPerDebt=debt_score / max(len(income_list), 1),
            netIncome=net_income_score / max(len(income_list), 1),
            mktCap=ticker_data.profile.mktCap
        )

    def sort(self):
        self.score_list = sorted(self.score_list, key=itemgetter(1))

    def filter(self):
        filtered_list: [ScoreEntry] = []
        for score in self.score_list:
            if (0.2 < score.grossGrowth < 0.5
                    and 0.2 < score.RnDRatio < 0.7
                    and 0.41 < score.cashPerDebt
                    and 0 < score.netIncome):
                filtered_list.append(score)
        self.score_list = filtered_list

