from typing import List, Dict
from bs4 import BeautifulSoup
import redis
import utils
from common import config
from dateutil import parser
import json

redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT)

ELEMENT_LIST = [
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


def getFinancialData(soup: BeautifulSoup, company: str, year: int, keywords: List[str] = None) -> List:
    if keywords is None:
        keywords = ELEMENT_LIST

    filtered_list = []
    for key in keywords:
        element_list = soup.find_all(key)
        for element in element_list:
            element_dict = parse_element(soup, element)
            filtered_list.append(element_dict)

    # redis_client.hset(utils.redis_key(company, year), mapping=hash_key)
    redis_client.set(utils.redis_key(company, year), json.dumps(filtered_list))
    print(f'successfully retrieved "{utils.redis_key(company, year)}" data from sec')
    return filtered_list


def clean_value(string):
    """
    Take a value that's stored as a string,
    clean it and convert to numeric.

    If it's just a dash, it's taken to mean
    zero.
    """
    if string.strip() == "-":
        return(0.0)

    try:
        return(float(string.strip().replace(",", "").replace(" ", "")))
    except:
        pass

    return(string)


def retrieve_from_context(soup, contextref):
    """
    Used where an element of the document contained no data, only a
    reference to a context element.
    Finds the relevant context element and retrieves the relevant data.

    Returns a text string

    Keyword arguments:
    soup -- BeautifulSoup souped html/xml object
    contextref -- the id of the context element to be raided
    """

    try:
        context = soup.find("xbrli:context", id=contextref)
        contents = context.find("xbrldi:explicitmember").get_text().split(":")[-1].strip()
    except:
        contents = ""
    return contents


def retrieve_unit(soup, each):
    """
    Gets the reporting unit by trying to chase a unitref to
    its source, alternatively uses element attribute unitref
    if it's not a reference to another element.

    Returns the unit

    Keyword arguments:
    soup -- BeautifulSoup souped html/xml object
    each -- element of BeautifulSoup souped object
    """

    # If not, try to discover the unit string in the
    # soup object
    try:
        unit_str = soup.find(id=each['unitref']).get_text()
    except:
        # Or if not, in the attributes of the element
        try:
            unit_str = each.attrs['unitref']
        except:
            return("NA")

    return unit_str.strip()


def retrieve_date(soup, each):
    """
    Gets the reporting date by trying to chase a contextref
    to its source and extract its period, alternatively uses
    element attribute contextref if it's not a reference
    to another element.
    Returns the date

    Keyword arguments:
    soup -- BeautifulSoup souped html/xml object
    each -- element of BeautifulSoup souped object
    """

    # Try to find a date tag within the contextref element,
    # starting with the most specific tags, and starting with
    # those for ixbrl docs as it's the most common file.
    date_tag_list = ["xbrli:enddate",
                     "xbrli:instant",
                     "xbrli:period",
                     "enddate",
                     "instant",
                     "period"]

    for tag in date_tag_list:
        try:
            date_val = parser.parse(soup.find(id=each['contextref']).find(tag).get_text()).\
                date().\
                isoformat()
            return(date_val)
        except:
            pass

    try:
        date_val = parser.parse(each.attrs['contextref']).\
            date().\
            isoformat()
        return(date_val)
    except:
        pass

    return("NA")


def parse_element(soup, element) -> Dict:
    """
    For a discovered XBRL tagged element, go through, retrieve its name
    and value and associated metadata.

    Keyword arguments:
    soup -- BeautifulSoup object of accounts document
    element -- soup object of discovered tagged element
    """

    if "contextref" not in element.attrs:
        return({})

    element_dict = {}

    # Basic name and value
    try:
        # Method for XBRLi docs first
        element_dict['name'] = element.attrs['name'].lower().split(":")[-1]
    except:
        # Method for XBRL docs second
        element_dict['name'] = element.name.lower().split(":")[-1]

    element_dict['value'] = element.get_text()
    element_dict['unit'] = retrieve_unit(soup, element)
    element_dict['date'] = retrieve_date(soup, element)

    # If there's no value retrieved, try raiding the associated context data
    if element_dict['value'] == "":
        element_dict['value'] = retrieve_from_context(
            soup, element.attrs['contextref'])

    # If the value has a defined unit (eg a currency) convert to numeric
    if element_dict['unit'] != "NA":
        element_dict['value'] = clean_value(element_dict['value'])

    # Retrieve sign of element if exists
    try:
        element_dict['sign'] = element.attrs['sign']

        # if it's negative, convert the value then and there
        if element_dict['sign'].strip() == "-":
            element_dict['value'] = 0.0 - element_dict['value']
    except:
        pass

    return(element_dict)