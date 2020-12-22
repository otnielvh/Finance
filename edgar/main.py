import financial_data
import requests
import argparse
import bs4 as bs
import os

SEC_ARCHIVE_URL = 'https://www.sec.gov/Archives/'


def fetchCompanyData(companyItem):
    company = companyItem
    company = company.strip()
    splitted_company = company.split('|')
    txt_url = splitted_company[-1]

    if not txt_url:
        return

    print(txt_url)  # edgar/data/1326801/0001326801-20-000076.txt

    data_url = txt_url.replace('-', '')
    data_url = data_url.split('.txt')[0]

    to_get_html_site = f'{SEC_ARCHIVE_URL}/{txt_url}'
    print(to_get_html_site)  # edgar/data/1326801/000132680120000076
    data = requests.get(to_get_html_site).content
    soup = bs.BeautifulSoup(data, 'lxml')

    # print(soup)
    financial_data.getFinancialData(soup)


def prepareIndex(year, quarter):
    filing = '10-K'
    filter = '10-K/A'
    download = requests.get(
        f'{SEC_ARCHIVE_URL}/edgar/full-index/{year}/{quarter}/master.idx').content
    decoded = download.decode("utf-8").split('\n')

    idx = []
    for item in decoded:
        if (filing in item) and (filter not in item):
            idx.append(item)
    return idx


def fetchYear(year):
    quarter = 'QTR4'
    filename = f'{year}-{quarter}-master.idx'

    try:
        idx = open(filename)
    except IOError:
        print("File not accessible, fetching from web")
        # get name of all filings
        idx = prepareIndex(year, quarter)
        with open(filename, 'w+') as f:
            for item in idx:
                f.write("%s\n" % item)

    txt_url = None
    for item in idx:
        fetchCompanyData(item)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yearStart",
                        type=int,
                        help='''
    The year from we want to start scraping
                        ''')
    parser.add_argument("yearEnd",
                        type=int,
                        help='''
    The year on which we will stop scraping
                        ''')
    args = parser.parse_args()
    # Startup parameters
    yearStart = args.yearStart
    yearEnd = args.yearEnd

    for year in range(yearStart, yearEnd):
        fetchYear(year)


if __name__ == "__main__":
    main()


# check companies, parsing normalization
