# -*- coding: utf-8 -*-

"""
Created on Tue Oct 31 01:04:08 2017

@author: dmitry
"""

from urllib import urlencode, urlopen
from datetime import datetime
from pandas import read_csv, set_option


def getfinamdata(symbol, period, start_date_str, end_date_str):
    finam_symbols = urlopen('http://www.finam.ru/cache/icharts/icharts.js').readlines()

    s_id = finam_symbols[0]
    s_code = finam_symbols[2]
    s_market = finam_symbols[3]

    ids = s_id[s_id.find('[') + 1:s_id.find(']')].split(',')
    codes = s_code[s_code.find('[\'') + 1:s_code.find('\']')].split('\',\'')
    markets = s_market[s_market.find('[') + 1:s_market.find(']')].split(',')
    res = []
    for (i, c, m) in zip(ids, codes, markets):
        if c == symbol:
            res.append((i, c, m))

    res = sorted(res, key=lambda icm: int(icm[2]))
    if not res:
        raise Exception("%s not found." % symbol)

    periods = {'tick': 1, 'min': 2, '5min': 3, '10min': 4, '15min': 5, '30min': 6, 'hour': 7, 'daily': 8, 'week': 9, 'month': 10}
    finam_url = "http://export.finam.ru/table.csv?"
    market = res[0][2]
    start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
    end_date = datetime.strptime(end_date_str, "%d.%m.%Y").date()
    symbol_code = res[0][0]
    # Формируем строку с параметрами запроса:
    params = urlencode([('market', market), ('em', symbol_code), ('code', symbol),
                        ('df', start_date.day), ('mf', start_date.month - 1), ('yf', start_date.year),
                        ('from', start_date_str),
                        ('dt', end_date.day), ('mt', end_date.month - 1), ('yt', end_date.year),
                        ('to', end_date_str),
                        ('p', periods[period]), ('f', "table"), ('e', ".csv"), ('cn', symbol),
                        ('dtf', 1), ('tmf', 3), ('MSOR', 1), ('mstime', "on"), ('mstimever', 1),
                        ('sep', 3), ('sep2', 1), ('datf', 5), ('at', 1)])

    url = finam_url + params  # Полная строка адреса со всеми параметрами.
    # Соединяемся с сервером, получаем данные и выполняем их разбор:
    data = read_csv(url, header=0, index_col=0, parse_dates={'Date&Time': [0, 1]}, sep=';').sort_index()
    data.columns = ['' + i for i in ['Open', 'High', 'Low', 'Close', 'Volume']]  # Заголовки столбцов

    set_option('display.max_columns', 50)  # Кол-во колонок
    set_option('display.width', 500)  #
    return data


if __name__ == "__main__":
    result = getfinamdata('SBER', 'hour', "01.12.2017", "06.10.2018")
    print(result)
