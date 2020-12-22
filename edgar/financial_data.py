from typing import List
from bs4 import BeautifulSoup
import redis
import utils
from common import config

redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT)

KEY_WORDS = [
    # general
    'dei:tradingsymbol',

    # income statement
    'us-gaap:revenues',
    'us-gaap:costofrevenue',
    'us-gaap:grossprofit',

    'us-gaap:generalandadministrativeexpense',
    'us-gaap:researchanddevelopmentexpense',
    'us-gaap:operatingexpenses',
    'us-gaap:operatingincomeloss',

    # Balance sheet
    'us-gaap:netincomeloss',

    'us-gaap:noncurrentassets',

    'us-gaap:liabilities',
]


def getFinancialData(soup: BeautifulSoup, company: str, year: int, keywords: List[str] = None) -> List[List[str]]:
    if keywords is None:
        keywords = KEY_WORDS

    filtered_list = []
    hash_key = dict()
    for key in keywords:
        tag_list = soup.find_all(key)
        for tag in tag_list:
            filtered_list.append([key, tag.get('contextref'), tag.get('name'), tag.text, tag.get('unitref')])
            hash_key[key] = str(tag.text)
    redis_client.hset(utils.redis_key(company, year), mapping=hash_key)
    print(f'successfully retrieved "{utils.redis_key(company, year)}" data from sec')
    return filtered_list
