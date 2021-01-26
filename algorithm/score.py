import logging
from algorithm.utils import TickerData
from typing import List
from datetime import datetime
from algorithm.utils import Statements, Income, dict2income, dict2balance_sheet
from operator import itemgetter
from collections import namedtuple
from algorithm.score_functions import average, avg_growth
from data.data_services import DataServices

ScoreEntry = namedtuple('Score', ['ticker', 'grossProfitGrowth', 'incomeGrowth', 'RnDRatio', 'cashPerDebt',
                                  'netIncome', 'mktCap'])


class BaseScore:

    def __init__(self, ticker_list: List[str], start_date: datetime, end_date: datetime):
        self.ticker_list = ticker_list
        self.start_date = start_date
        self.end_date = end_date
        self.score_list = []
        self.ds = DataServices()

    def filter_by_date(self, income_list: List[Income]) -> List[Income]:
        new_income_list: List[Income] = []
        for income in income_list:
            try:
                new_income_list.append(income)
            except ValueError:
                print(f'ValueError: could not parse {income.date}')
        return new_income_list

    def compute_score(self):
        """

        :return: List where each row contains the ticker name and a scores (maybe more than 1)
        """

        score_list: [ScoreEntry] = []

        for ticker in self.ticker_list:
            score = self.process_ticker(ticker)
            score_list.append(score)

        self.score_list: [ScoreEntry] = [score for score in score_list if score]
        self.filter()
        self.sort()

    def score(self, ticker: str, ticker_data: TickerData) -> ScoreEntry:
        raise Exception("Unimplemented exception")

    def filter(self) -> None:
        pass

    def sort(self):
        self.score_list.sort()

    # TODO: get years dynamically
    def get_financials(self, ticker: str, from_year: int = 2016, to_year: int = 2019,
                       statement: Statements = Statements.Income, ) -> List[Income]:
        resp = self.ds.get_ticker_data(ticker, from_year, to_year)
        fin_by_year = []
        for year in range(from_year, to_year):
            element = resp.get(str(year))
            if element:
                element['date'] = str(year)
                fin_by_year.append(element)

        financial_list = []

        if statement == Statements.Income:
            financial_list = [dict2income(d) for d in fin_by_year]
        elif statement == Statements.BalanceSheet:
            financial_list = [dict2balance_sheet(d) for d in fin_by_year]

        return financial_list

    def process_ticker(self, ticker) -> ScoreEntry:
        financial_dict = {}
        try:
            for statement_type in [Statements.Income, Statements.BalanceSheet]:
                data_by_year = self.get_financials(ticker, statement=statement_type)
                data_until_today = self.filter_by_date(data_by_year)
                financial_dict[statement_type] = data_until_today

            ticker_data = TickerData(
                profile=self.get_financials(ticker, statement=Statements.Profile),
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
        rnd_count = 0.0
        # TODO: add debt score
        # debt_score = 0

        income_list = ticker_data.income_list
        # balance_sheet_list = ticker_data.balance_sheet_list
        for i in range(len(income_list)):

            try:
                # debt_score += float(balance_sheet_list[i].TotalAssets) / max(
                #     float(balance_sheet_list[i].TotalLiabilities),
                #     float(balance_sheet_list[i].TotalAssets) / 5)  # handle case of zero or very low debt for one year
                if income_list[i].RnDExpenses and income_list[i].OperatingExpenses:
                    rnd_score += float(income_list[i].RnDExpenses) / float(income_list[i].OperatingExpenses)
                    rnd_count += 1
                else:
                    logging.info(f'failed to process inclcome list {i} for {ticker}')
            except IndexError as e:
                print(f'index {i!r} out of bounds for {ticker!r} -> {e}')
            except ZeroDivisionError as e:
                print(f'{ticker!r} revenue is zero for {income_list[i].Date} -> {e}')

        return ScoreEntry(
            ticker=ticker,
            grossProfitGrowth=avg_growth(ticker, income_list, 'GrossProfit'),
            incomeGrowth=avg_growth(ticker, income_list, 'NetIncome'),
            RnDRatio=rnd_score / rnd_count if rnd_count else 0,
            cashPerDebt=0,
            netIncome=average(income_list, 'NetIncome'),
            mktCap=0
        )

    def sort(self):
        self.score_list = sorted(self.score_list, key=itemgetter(1))

    def filter(self):
        filtered_list: [ScoreEntry] = []
        for score in self.score_list:
            # if (1.25 < score.grossProfitGrowth < 1.5
            #         and 0.25 < score.RnDRatio < 0.7):
                # and 0.2 < score.RnDRatio < 0.7
                # and 0.41 < score.cashPerDebt
                # and 0 < score.netIncome
            if 0 < score.RnDRatio:
                filtered_list.append(score)
        self.score_list = filtered_list


