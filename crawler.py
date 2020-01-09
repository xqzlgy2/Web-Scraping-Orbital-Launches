#-*-coding:utf-8-*-

import csv
import re
import calendar
import datetime
import pandas as pd
from urllib import error
from urllib import request

def get_page_code(url):
    try:
        rqs = request.urlopen(url)
        pagecode = rqs.read().decode('utf-8')
        return pagecode
    except error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

def replace(pagecode):
    #replace navbox table and head
    hlist = re.compile('<table class="navbox hlist"(.*?)</table>', re.DOTALL)
    title = re.compile('<h3>(.*?)</h3>', re.DOTALL)
    pagecode = re.sub(hlist, ' ', pagecode)
    pagecode = re.sub(title, ' ', pagecode)
    return pagecode

def get_time_str(timestr):
    idx = timestr.find('[')
    if idx != -1:
        timestr = timestr[0: idx]
    idx = timestr.find('(')
    if idx != -1:
        timestr = timestr[0: idx]
    strs = timestr.split()
    result = strs[1] + " " + strs[0]
    return result

def get_stat_info(pagecode):
    #replace some labels
    pagecode = replace(pagecode)

    #get needed table
    tables = pd.read_html(pagecode, attrs={'class':'wikitable collapsible'})
    table = tables[0]
    #print(table)

    result = {}
    month = {''}
    last_time = ""
    status = ['Successful', 'Operational', 'En Route']
    lauch_success = False
    counter = 0
    for index, row in table.iterrows():
        #print(str(row[0]) + " " + str(row[5]) + " " + str(row[6]))
        first_col = str(row[0])
        valid = False
        for i in range(1, 13):
            if calendar.month_name[i] in first_col:
                valid = True
                first_col = first_col.replace(calendar.month_name[i], str(i) + " ")
                break
        if not valid:
            continue
        else:
            time_str = get_time_str(first_col)
            #print(time_str + " " + row[5] + " " + row[6])
            if last_time != time_str:
                if lauch_success:
                    counter += 1
                    lauch_success = False
                if last_time != "":
                    result[last_time] = counter
                last_time = time_str
                counter = 0
            if row[5] == row[6]:
                if lauch_success:
                    counter += 1
                lauch_success = False
            else:
                for s in status:
                    if s in str(row[6]):
                        lauch_success = True
                        break
    if lauch_success:
        counter += 1
    result[last_time] = counter
    return result

def output_result(result):
    with open('result.csv', 'w') as csv_file:
        fields = ['date', 'value']
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()

        day = datetime.datetime(2019,1,1,0,0,0)
        for i in range(1, 366):
            key = str(day.month) + " " + str(day.day)
            value = '0'
            if key in result:
                value = str(result[key])
            date_str = day.isoformat() + '+00:00'
            writer.writerow({'date': date_str, 'value': value})
            day = day + datetime.timedelta(days=1)

def begin(url):
    print('Fetching source code...')
    pagecode = get_page_code(url)
    #print(pagecode)
    print('Cauculating...')
    result = get_stat_info(pagecode)
    #print(result)
    print('Writing result...')
    output_result(result)
    print('Done.')


url = "https://en.m.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"
begin(url)