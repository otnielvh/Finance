

def balance_Sheet(soup, year, quarter):
    table = soup.find(text="Current assets:").find_parent("table")
    items = []
    values = []

    dict_value = {}
    dict_value[str(year) + quarter] = {}
    name_key = 0

    for row in table.findAll('tr')[3:]:
        # 1 Get name of the Table Row Index
        try:
            item = row.find("ix:nonfraction").attrs['name']
            item = item.replace('us-gaap:', '')
        except:
            continue
        # 2 Get value and transform the number to an appropiate format
        try:
            value = row.find("ix:nonfraction").text

            try:
                value = value.replace(',', '')
            except:

                value
            try:
                value = value.replace('(', '-')
            except:

                value
            try:
                # if there is a sign, we need to add it
                sign = row.find("ix:nonfraction")["sign"]
                value = sign + value
            except:
                value
            try:
                value = float(value)
            except:
                print(value + ' 5')
        except:
            value = ''
        # 3 Add elements to dictionaries
        dict_value[str(year) + quarter][item] = value
    print(dict_value)
