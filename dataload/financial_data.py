import logging
import time
from typing import List, Dict
import redis
from bs4 import BeautifulSoup
from dateutil import parser
from common import utils, config

redis_client = redis.Redis(
    host=config.REDIS_HOST_NAME,
    port=config.REDIS_PORT,
    decode_responses=True
)

ELEMENT_LIST = [
    # general
    # 'us-gaap:CommonStockSharesOutstanding',
    'dei:EntityCommonStockSharesOutstanding',

    # income statement

    # revenue
    'us-gaap:salesrevenuenet',
    'us-gaap:revenues',
    'us-gaap:costofgoodssold',

    # revenue
    'us-gaap:costofrevenue',
    'us-gaap:grossprofit',

    # expense
    'us-gaap:generalandadministrativeexpense',
    'us-gaap:sellinggeneralandadministrativeexpense',

    'us-gaap:researchanddevelopmentexpense',

    'us-gaap:operatingexpenses',
    'us-gaap:operatingincomeloss',

    # Balance sheet
    'us-gaap:netincomeloss',

    'us-gaap:noncurrentassets',

    # Liabilities
    'us-gaap:liabilities',
    'us-gaap:liabilitiescurrent'
]


def get_financial_data(soup: BeautifulSoup, ticker: str, year: int) -> None:
    """Extract from passed soup document all finanical data according to keywords list
    Args:
        soup BeautifulSoup: The soup document holding the report to parse
        ticker int: The ticker of the company
        year int: The year to fetch stocks data
    Returns:
        None
    """
    start = time.time()
    keywords = ELEMENT_LIST

    # get from the report the focus date of the report
    report_date_focus = soup.find("dei:documentfiscalperiodfocus")
    if report_date_focus is None:
        return []

    # extract all the data according to the report focus date and the keywords
    filtered_list = []
    for key in keywords:
        element_list = soup.find_all(
            key, {"contextref": report_date_focus['contextref']})
        for element in element_list:
            element_dict = parse_element(soup, element)
            if element_dict:
                filtered_list.append(element_dict)

    # prepare the data for saving
    data = {d.get('name'): d.get('value') for d in filtered_list}
    # TBD should this be save? We need to filter what is not interesting for us
    if not data:
        data['None'] = 0
        logging.info(f'Data for "{utils.redis_key(ticker, year)}" is empty')

    redis_client.hset(utils.redis_key(ticker, year), mapping=data)
    logging.info(
        f'successfully retrieved "{utils.redis_key(ticker, year)}" dataload from sec')
    end = time.time()
    logging.debug(f"elapsed time to parse: {(end - start)}")
    # return filtered_list


def clean_value(string):
    """
    Take a value that's stored as a string,
    clean it and convert to numeric.

    If it's just a dash, it's taken to mean
    zero.
    """
    if string.strip() == "-":
        return (0.0)

    try:
        return float(string.strip().replace(",", "").replace(" ", ""))
    except:
        pass

    return string


def retrieve_from_context(soup, contextref):
    """
    Used where an element of the document contained no dataload, only a
    reference to a context element.
    Finds the relevant context element and retrieves the relevant dataload.

    Returns a text string

    Keyword arguments:
    soup -- BeautifulSoup souped html/xml object
    contextref -- the id of the context element to be raided
    """

    try:
        context = soup.find("xbrli:context", id=contextref)
        contents = context.find(
            "xbrldi:explicitmember").get_text().split(":")[-1].strip()
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
            return "NA"

    return unit_str.strip()


def retrieve_element_by_taglist(soup: BeautifulSoup, tag_list: List[str]) -> str:
    element = None
    for tag in tag_list:
        try:
            element = parser.parse(soup.find(tag).get_text())
            return element
        except:
            pass
    return element


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
            date_val = parser.parse(soup.find(id=each['contextref']).find(tag).get_text()). \
                date(). \
                isoformat()
            return (date_val)
        except:
            pass

    try:
        date_val = parser.parse(each.attrs['contextref']). \
            date(). \
            isoformat()
        return (date_val)
    except:
        pass

    return "NA"


def parse_element(soup, element) -> Dict:
    """
    For a discovered XBRL tagged element, go through, retrieve its name
    and value and associated metadata.

    Keyword arguments:
    soup -- BeautifulSoup object of accounts document
    element -- soup object of discovered tagged element
    """

    # no context so we can't extract dataload
    if "contextref" not in element.attrs:
        return ({})

    # check if this is a subentity
    isSubEntity = soup.find(
        id=element.attrs['contextref']).find("xbrli:segment")
    if isSubEntity:
        return ({})

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

    # If there's no value retrieved, try raiding the associated context dataload
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

    return element_dict
