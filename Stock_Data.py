from bs4 import BeautifulSoup as bs
import urllib2
import quandl

# This allows me to make more than 50 requests a day
quandl.ApiConfig.api_key = 'vcdxyPSvy2mTN56WPZkz'

SP = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
page = urllib2.urlopen(SP)
soup = bs(page, "html.parser")

table = soup.find("table", {"class" : "wikitable sortable"})

# Getting all the S&P500 indices from wikipedia, and put them into a list
SP_ticker = []

for row in table.findAll("tr"):
    cells = row.findAll("td")
    if len(cells) == 8:
          SP_ticker.append(cells[0].find(text=True))

# Creating a timestamp from 2006-01-01 until 2017-02-09
# Turns out this is unnecessary

import pandas as pd
import datetime
from datetime import date, timedelta as td

today = date(2017, 2, 9)
day = date(2015, 1, 1)

wrong_calender = []

delta = today - day
for i in range(delta.days + 1):
    wrong_calender.append(day + td(days=i))
# Calender list is the wrong way up, need to reverse it
calender = wrong_calender[::-1]

days = pd.DataFrame(calender, index=None)
type(days)

# Defining a function to grab data about a single company
# This is the dataframe. It contains a small crop of information about the stock indices. I'm particularly interested
# in the Average value right now, for my correlation matrix. But the other values may come in useful for a linear
# regression later on in the project.

def Stck(x):
    data = quandl.get("WIKI/{}".format(x), start_date="2015-01-01", end_date="2017-02-09")
    data['Avrg_{}'.format(x)] = (data['High'] + data['Low'] + data['Open'] + data['Close']) / 4
    data['Open_{}'.format(x)] = data['Open']
    data['High_{}'.format(x)] = data['High']
    data['Low_{}'.format(x)] = data['Low']
    data['Close_{}'.format(x)] = data['Close']
    data['Volume_{}'.format(x)] = data['Volume']
    data['ExDividen_{}'.format(x)] = data['Ex-Dividend']
    data['SplitRatio_{}'.format(x)] = data['Split Ratio']
#     a = data.iloc[:,[13, 14, 15, 16, 17]]
    a = data.iloc[:, 12:19]
    return a

# Get data for all the S&P500 companies and then join them into one big dataframe
# It came up with a Quandl code error
# Used try and except to find out which was wrong

Stck_dict = {}
for stck in SP_ticker:
    try:
        Stck_dict[stck + "_n"] = Stck(stck)
    except:
        print "{} was not found in Quandl".format(stck)


# I used the MMM indices to create a template for the dataframe that would fix the dimensions. There is defo a quicker way of
# doing this, but this was fairly easy and quick so I stuck with it.

df = Stck('MMM')

for Comp in SP_ticker:
    try:
        comp = Stck(Comp)
        df = df.merge(comp, how='outer', left_index=True, right_index=True)
    except:
        pass

# To get rid of all the NaN values in the table and replace them with the mean value of the column 

df.fillna(df.mean(), inplace=True)

# To drop the duplicate MMM values

df.drop(df.columns[1:8], axis=1, inplace=True)

# Then I wanted to rename the MMM columns to get rid of the _y that was generated because of the duplicate

df.rename(columns={'Avrg_MMM_y':'Avrg_MMM', 'Open_MMM_y':'Open_MMM', 'High_MMM_y':'High_MMM', 'Low_MMM_y':'Low_MMM', 'Close_MMM_y':'Close_MMM', 'Volume_MMM_y':'Volume_MMM', 'ExDividen_MMM_y':'ExDividen_MMM', 'SplitRatio_MMM_y':'SplitRatio_MMM'}, inplace=True)

# save to an excel file

df.to_excel("Stock_Date_Perf.xlsx", "Sheet 1")
