import logging
import time
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import SoupStrainer
from dateutil import parser
from datetime import datetime
from src.data.data_access import DataAccess


class SecGov:
    ELEMENT_LIST = \
    {
        "Revenue" : [
            'us-gaap:Revenues',
            'us-gaap:SalesRevenueNet',
        ],
        "Costs" : [
            'us-gaap:CostOfRevenue',
            'us-gaap:CostOfGoodsSold',
        ],
        "GrossProfit" : [
            'us-gaap:GrossProfit',
        ],
        "AdminExpenses" : [
            # costs
            'us-gaap:GeneralAndadministrativeExpense',
            'us-gaap:SellingGeneralAndadministrativeExpense',
        ],
        "RndExpenses" : [
            # costs
            'us-gaap:ResearchAndDevelopmentExpense',
        ],
        "OperatingExpenses" : [
            # costs
            'us-gaap:OperatingExpenses',
            'us-gaap:OperatingIncomeLoss',
        ],
        "NetIncome" : [
            'us-gaap:netincomeloss',
        ],
        "Liabilities": [
            'us-gaap:liabilities',
            'us-gaap:liabilitiescurrent',
        ],
        "Assets": [
            'us-gaap:assets',
            'us-gaap:assetscurrent',
        ]
    }

    SEC_ARCHIVE_URL = 'https://www.sec.gov/Archives/'
    TICKER_CIK_LIST_URL = 'https://www.sec.gov/include/ticker.txt'

    def __init__(self):
        self.data_access = DataAccess()

    def _get_data_by_key(self, soup: BeautifulSoup, keywords: [], doc_filter: str) -> Optional[Dict]:
        """
        @param soup:
        @param keywords:
        @param doc_filter:
        @return:
        """
        for key in keywords:
            element = soup.find(
                str.lower(key), {"contextref": doc_filter})
            if element:
                element_dict = self.parse_element(soup, element)
                if element_dict:
                    return element_dict

    def get_financial_data(self, soup: BeautifulSoup, ticker: str, year: int) -> None:
        """Extract from passed soup document all finanical data_assets according to keywords list
        Args:
            soup BeautifulSoup: The soup document holding the report to parse
            ticker int: The ticker of the company
            year int: The year to fetch stocks data_assets
        Returns:
            None
        """
        start = time.time()
        element_list = self.ELEMENT_LIST

        # get from the report the focus date of the report and shares
        report_date_focus = soup.find("dei:documentfiscalperiodfocus")
        shares = soup.find_all("dei:entitycommonstocksharesoutstanding")
        if report_date_focus is None:
            return

        # extract all the data_assets according to the report focus date and the keywords
        filtered_list = []
        for key_name, keywords in element_list.items():
            for key in keywords:
                report_focus = report_date_focus['contextref']
                element_dict = self._get_data_by_key(soup, keywords, report_focus)
                if element_dict:
                    element_dict['name'] = key_name
                    filtered_list.append(element_dict)
                # TODO: check that this makes sense
                else:
                    report_focus = f"FI{report_date_focus['contextref'].strip('FDYT')}"
                    element_dict = self._get_data_by_key(soup, keywords, report_focus)
                    if element_dict:
                        element_dict['name'] = key_name
                        filtered_list.append(element_dict)

        # calculate total shares
        total_shares = 0
        for share in shares:
            element_dict = self.parse_element(soup, share, False)
            if element_dict:
                total_shares += element_dict['value']
        if len(shares) > 0:
            element_dict['value'] = total_shares
            element_dict['name'] = 'SharesOutstanding'
            filtered_list.append(element_dict)

        # prepare the data_assets for saving
        data = {d.get('name'): d.get('value') for d in filtered_list}
        # TBD should this be save? We need to filter what is not interesting for us
        if not data:
            data['None'] = 0
            logging.info(f'Data for {ticker}  {year} is empty')

        # calculated fields
        if 'Assets' in data and 'Liabilities' in data:
            data['TotalEquityGross'] = data['Assets'] - data['Liabilities']

        # make sure that we have prices stored
        if 'SharesOutstanding' in data:
            dt = datetime.strptime(element_dict['date'], '%Y-%m-%d')
            ticker_price = self.data_access.get_price(ticker, dt)
            data['MarketCap'] = data['SharesOutstanding'] * ticker_price

        self.data_access.store_ticker_financials(ticker, year, data)
        logging.info(f'successfully stored {ticker} {year} from sec')
        end = time.time()
        logging.debug(f"elapsed time to parse: {(end - start)}")

    def clean_value(self, string):
        """
        Take a value that's stored as a string,
        clean it and convert to numeric.

        If it's just a dash, it's taken to mean
        zero.
        """
        if string.strip() == "-":
            return 0.0

        try:
            return float(string.strip().replace(",", "").replace(" ", ""))
        except:
            pass

        return string

    def retrieve_from_context(self, soup, contextref):
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
            contents = context.find(
                "xbrldi:explicitmember").get_text().split(":")[-1].strip()
        except:
            contents = ""
        return contents

    def retrieve_unit(self, soup, each):
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


    def retrieve_element_by_taglist(self, soup: BeautifulSoup, tag_list: List[str]) -> str:
        element = None
        for tag in tag_list:
            try:
                element = parser.parse(soup.find(tag).get_text())
                return element
            except:
                pass
        return element

    def retrieve_date(self, soup, each):
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
                return date_val
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

    def parse_element(self, soup: BeautifulSoup, element, check_is_sub_entity: bool = True) -> Dict:
        """
        For a discovered XBRL tagged element, go through, retrieve its name
        and value and associated metadata.

        Keyword arguments:
        soup -- BeautifulSoup object of accounts document
        element -- soup object of discovered tagged element
        @rtype: object
        """

        # no context so we can't extract data
        if "contextref" not in element.attrs:
            return ({})

        # check if this is a subentity
        if check_is_sub_entity:
            isSubEntity = soup.find(
                id=element.attrs['contextref']).find("xbrli:segment")
            if isSubEntity:
                return {}

        element_dict = {}

        # Basic name and value
        try:
            # Method for XBRLi docs first
            element_dict['name'] = element.attrs['name'].lower().split(":")[-1]
        except:
            # Method for XBRL docs second
            element_dict['name'] = element.name.lower().split(":")[-1]

        element_dict['value'] = element.get_text()
        element_dict['unit'] = self.retrieve_unit(soup, element)
        element_dict['date'] = self.retrieve_date(soup, element)

        # If there's no value retrieved, try raiding the associated context data
        if element_dict['value'] == "":
            element_dict['value'] = self.retrieve_from_context(
                soup, element.attrs['contextref'])

        # If the value has a defined unit (eg a currency) convert to numeric
        if element_dict['unit'] != "NA":
            element_dict['value'] = self.clean_value(element_dict['value'])

        # Retrieve sign of element if exists
        try:
            element_dict['sign'] = element.attrs['sign']

            # if it's negative, convert the value then and there
            if element_dict['sign'].strip() == "-":
                element_dict['value'] = 0.0 - element_dict['value']
        except:
            pass

        return element_dict

    def fetch_ticker_financials_by_year(self, year: int, ticker: str = None) -> None:
        """Fetch ticker data according to the passed year and store to DB
        Args:
            year int: The year to fetch stocks data_assets
            ticker str: if not None cache this ticker, otherwise cache all
        Returns:
            None
        """
        # check if the index exists
        is_ixd_stored = self.data_access.is_index_stored(year)
        if not is_ixd_stored:
            logging.info(f"Index file for year {year} is not accessible, fetching from web")
            for q in range(1, 5):  # 1 to 4 inclusive
                self._prepare_index(year, q)

        if ticker:
            ticker_cik = self.data_access.get_ticker_cik(ticker)
            result = self.data_access.get_index_row_by_cik(ticker_cik, year)
            if result is not None:
                ticker_info_hash = {
                    'company_name': result[0],
                    f'txt_url:{year}': result[1]
                }
                self.data_access.store_ticker_info(ticker, ticker_info_hash)
                self.fetch_company_data(ticker, year)
                self.data_access.commit_ticker_data()
            else:
                logging.info(f'Could not fetch data for {ticker} for year {year}')
        else:
            idx = self.data_access.get_index_by_year(year)
            for result in idx:
                current_ticker = self.data_access.get_ticker_by_cik(result[2])
                if result is not None:
                    ticker_info_hash = {
                        'company_name': result[0],
                        f'txt_url:{year}': result[1]
                    }
                    self.data_access.store_ticker_info(current_ticker, ticker_info_hash)
                    self.fetch_company_data(ticker, year)
                else:
                    logging.info(f'Could not fetch data for {ticker} for year {year}')
            self.data_access.commit_ticker_data()

    def fetch_company_data(self, ticker: str, year: int) -> None:
        """Fetch the data_assets for the specified company and year from sec
        Args:
            ticker str: The ticker name
            year int: The year
        Returns:
            None
        """
        txt_url = self.data_access.get_ticker_url(ticker, year)
        if txt_url:
            self._fetch_company_data(ticker, year, txt_url)
        else:
            logging.info(f"Couldn't load data_assets for {ticker}:{year}")

    def _fetch_company_data(self, ticker: str, year: int, txt_url: str) -> None:
        """Fetch the data_assets for the specified company and year from sec
        Args:
            ticker str: The ticker name
            year int: The year
            txt_url str: The url to fetch from the data_assets
        Returns:
            None
        """
        if not txt_url:
            return

        to_get_html_site = f'{self.SEC_ARCHIVE_URL}/{txt_url}'
        data = requests.get(to_get_html_site).content

        xbrl_doc = SoupStrainer("xbrl")
        soup = BeautifulSoup(data, 'lxml', parse_only=xbrl_doc)

        if soup:
            self.get_financial_data(soup, ticker, year)

    def _prepare_index(self, year: int, quarter: int) -> None:
        """Prepare the edgar index for the passed year and quarter
        The data_assets will be saved to DB
        Args:
            year int: The year to build the index for
            quarter int: The quarter to build the index between 1-4
        Returns:
            None
        """
        filing = '|10-K|'
        download = requests.get(f'{self.SEC_ARCHIVE_URL}/edgar/full-index/{year}/QTR{quarter}/master.idx').content
        decoded = download.decode("ISO-8859-1").split('\n')

        self.data_access.store_index(decoded, year, filing)
        logging.info(f"Inserted year {year} qtr {quarter} to DB")

    def fetch_tickers_list(self) -> List[str]:
        """Fetch a list of tickers from sec, and store them in the DB.
        Skip if already in cache.
        Returns:
            a list of tickers
        """
        ticker_list = []
        resp = requests.get(self.TICKER_CIK_LIST_URL)
        ticker_cik_list_lines = resp.content.decode("utf-8").split('\n')
        for entry in ticker_cik_list_lines:
            ticker, cik = entry.strip().split()
            ticker = ticker.strip()
            cik = cik.strip()
            self.data_access.store_ticker_cik_mapping(ticker, cik)
            ticker_list.append(ticker)
        logging.info(f'Successfully mapped tickers to cik')
        return ticker_list
