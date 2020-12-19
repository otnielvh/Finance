import bs4 as bs
import requests
from edgar import balance_sheet


def main():
    company = 'Facebook Inc'
    filing = '10-Q'
    year = 2020
    quarter = 'QTR3'
    # get name of all filings
    download = requests.get(
        f'https://www.sec.gov/Archives/edgar/full-index/{year}/{quarter}/master.idx').content
    download = download.decode("utf-8").split('\n')
    # print(download)

    for item in download:
        # company name and report type
        if (company in item) and (filing in item):
            # print(item)
            company = item
            company = company.strip()
            splitted_company = company.split('|')
            url = splitted_company[-1]

    print(url)  # edgar/data/1326801/0001326801-20-000076.txt

    url2 = url.split('-')
    url2 = url2[0] + url2[1] + url2[2]
    url2 = url2.split('.txt')[0]
    print(url2)  # edgar/data/1326801/000132680120000076

    to_get_html_site = 'https://www.sec.gov/Archives/' + url
    data = requests.get(to_get_html_site).content
    data = data.decode("utf-8")
    data = data.split('FILENAME>')
    # data[1]
    data = data[1].split('\n')[0]

    url_to_use = 'https://www.sec.gov/Archives/' + url2 + '/'+data
    print(url_to_use)

    resp = requests.get(url_to_use)
    soup = bs.BeautifulSoup(resp.text, 'lxml')

    # print(soup)
    balance_sheet.balance_Sheet(soup, 2020, quarter)


if __name__ == "__main__":
    main()
