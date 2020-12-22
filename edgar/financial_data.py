from typing import List
from bs4 import BeautifulSoup

GAAP_KEY_WORDS = [
    'dei:TradingSymbol',
    # dei:CurrentFiscalYearEndDate
    'us-gaap:liabilities',
    'us-gaap:noncurrentassets',
    'us-gaap:costofrevenue',
    'us-gaap:generalandadministrativeexpense',
    'us-gaap:operatingincomeloss',
    'us-gaap:netincomeloss',
    'us-gaap:grossprofit',
    'us-gaap:researchanddevelopmentexpense',
    'us-gaap:revenues',
    'us-gaap:operatingexpenses',
]

DEI_KEY_WORDS = [
    'dei:tradingsymbol',
]


def getFinancialData(soup: BeautifulSoup) -> List[List[str]]:
    filtered_list = getData(soup, "ix:nonfraction", GAAP_KEY_WORDS)
    filtered_list += (getData(soup, "ix:nonnumeric", DEI_KEY_WORDS))
    print(filtered_list)
    return filtered_list


# def getData(soup: BeautifulSoup, searchString: str, keywords: []) -> List[List[str]]:
#     tag_list = soup.find_all(searchString)

#     filtered_list = []
#     for tag in tag_list:
#         if tag.get('name') in keywords:
#             filtered_list.append([tag.get('contextref'), tag.get(
#                 'name'), tag.text, tag.get('unitref')])
#     return filtered_list


def getData(soup: BeautifulSoup, searchString: str, keywords: []) -> List[List[str]]:
    filtered_list = []
    for key in keywords:
        tag_list = soup.find_all(key)
        for tag in tag_list:
            filtered_list.append([key, tag.get('contextref'), tag.get(
                'name'), tag.text, tag.get('unitref')])
    return filtered_list
