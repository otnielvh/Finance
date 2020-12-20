import bs4 as bs
import requests
from edgar import balance_sheet

SEC_ARCHIVE_URL = 'https://www.sec.gov/Archives/'


def main():
    company = 'Facebook Inc'
    filing = '10-Q'
    year = 2020
    quarter = 'QTR3'
    # get name of all filings
    download = requests.get(f'{SEC_ARCHIVE_URL}/edgar/full-index/{year}/{quarter}/master.idx').content
    decoded_download = download.decode("utf-8").split('\n')

    txt_url = None
    for item in decoded_download:
        # company name and report type
        if (company in item) and (filing in item):
            # print(item)
            company = item
            company = company.strip()
            splitted_company = company.split('|')
            txt_url = splitted_company[-1]

    if not txt_url:
        exit(1)

    print(txt_url)  # edgar/data/1326801/0001326801-20-000076.txt

    data_url = txt_url.replace('-', '')
    data_url = data_url.split('.txt')[0]
    print(data_url)  # edgar/data/1326801/000132680120000076

    to_get_html_site = f'{SEC_ARCHIVE_URL}/{txt_url}'
    data = requests.get(to_get_html_site).content
    data = data.decode("utf-8")
    data = data.split('FILENAME>')
    # data[1]
    data = data[1].split('\n')[0]

    url_to_use = f'{SEC_ARCHIVE_URL}/{data_url}/{data}'
    print(url_to_use)

    resp = requests.get(url_to_use)
    soup = bs.BeautifulSoup(resp.text, 'lxml')

    # print(soup)
    balance_sheet.balance_sheet(soup)


if __name__ == "__main__":
    main()
