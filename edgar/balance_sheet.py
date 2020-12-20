from typing import List
from bs4 import BeautifulSoup

BALANCE_SHEET_KEY_WORDS = [
    'dei:TradingSymbol',
    # dei:CurrentFiscalYearEndDate
    'us-gaap:Liabilities',
    'us-gaap:NoncurrentAssets',
    'us-gaap:CostOfRevenue',
    'us-gaap:GeneralAndAdministrativeExpense',
    'us-gaap:OperatingIncomeLoss',
    'us-gaap:NetIncomeLoss',
]


def balance_sheet(soup: BeautifulSoup) -> List[List[str]]:

    tag_list = soup.find_all("ix:nonfraction")

    filtered_list = []
    for tag in tag_list:
        if tag.get('name') in BALANCE_SHEET_KEY_WORDS:
            filtered_list.append([tag.get('contextref'), tag.get('name'), tag.text, tag.get('unitref')])
    for line in filtered_list:
        print(line)
    return filtered_list

