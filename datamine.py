import csv, quandl, yfinance, test, requests, asyncio, aiohttp
import profile, market_day
import alpaca_trade_api as tradeapi
from alpaca_trade_api import REST
from alpaca_trade_api.rest import TimeFrame
from os import listdir
from os.path import isfile, join
import pandas as pd

async def get_APIdata(session, url, datas):
    async with session.get(url) as response:
        result = await response.json()
        try:
            data = {
                'ticker'    : result['symbol'],
                'date'      : result['from'],
                'open'      : result['open'],
                'high'      : result['high'],
                'low'       : result['low'],
                'close'     : result['close'],
                'volume'    : result['volume']
            }
            datas.append(data)
        except Exception as e:
            pass
            #print(e)

async def scan(date):
    df = pd.read_csv('./data/tickers/polygon_list.csv')

    errors = []

    tickers = df['ticker'].tolist()

    datas = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for ticker in tickers:
            url = "https://api.polygon.io/v1/open-close/{}/{}?unadjusted=true&apiKey={}".format(ticker, date, profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, url, datas))
            tasks.append(task)
        await asyncio.gather(*tasks)

    return datas

#Get Daily Prices for 3,000 US Stocks into CSV
def get_quandl():
    quandl.ApiConfig.api_key = profile.QUANDL_API_KEY
    quandl.export_table("WIKI/PRICES")

#Create csv file for each ticker
def divide_quandl_csv():
    with open('WIKI_PRICES.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        new_file = True
        col_name = []
        name = ''
        for row in csv_reader:
            print(row[0])
            print(row)
            if line_count == 0:
                col_name = row
                line_count += 1
            else:
                if name != row[0]:
                    new_file = True
                    print("New Ticker")
                else:
                    new_file = False
                name = row[0]
                with open('data/' + name+'.csv', 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    if new_file:
                        csvwriter.writerow(col_name)
                    csvwriter.writerow(row)

#Create a list of tickers in a single csv
def get_quandl_list():
    onlyfiles = [f for f in listdir("data") if isfile(join("data", f))]
    print(onlyfiles)

#Get intraday prices from 2016 for 9,000 US Stocks into CSV
def get_alpaca():
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )
    active_assets = api.list_assets(status='active')

    for asset in active_assets:
        data = api.get_bars(asset, TimeFrame.Minute, "2016-01-01", "2021-01-01", limit = 10000, adjustment="raw")
        print(data.df)

def get_yfinance():
    ticker = "AAPL"
    data = yfinance.download(ticker, period='7d', interval='1m')
    print(data)
    data = yfinance.download(ticker, period='60d', interval='5m')
    print(data)

def get_all_stocks():

    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

    assets = api.list_assets(status='active')
    count = 0
    ticker = ['ticker']
    with open('assets_list.csv', mode='w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(ticker)
        for asset in assets:
            if asset.tradable:
                count += 1
                ticker = [asset.symbol]
                csvwriter.writerow(ticker)
        print(count)

def get_tickers_quandl():
    with open('./data/tickers/quandl.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['ticker'])
        tickers = [
        f for f in listdir('./data/historical/quandl/') if isfile(join('./data/historical/quandl/', f))
        ]
        tickers.sort()
        for n, i in enumerate(tickers):
            tickers[n] = tickers[n].replace(".csv", "")
            csvwriter.writerow([tickers[n]])
    
def get_tickers_polygon():
    tickers = []

    with open('./data/tickers/polygon_list.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['ticker', 'name', 'locale', 'exchange'])
        url = "https://api.polygon.io/v3/reference/tickers?active=true&sort=ticker&order=asc&limit=1000&apiKey=" + profile.POLYGON_API_KEY
        response = requests.get(url).json()
        while 'next_url' in response:
            #print(response['next_url'])
            for ticker in response['results']:
                if 'primary_exchange' in ticker and 'locale' in ticker and '.' not in ticker['ticker'] and len(ticker['ticker']) < 5:
                    csvwriter.writerow([ticker['ticker'], ticker['name'], ticker['locale'], ticker['primary_exchange']])
            response = requests.get(response['next_url'] + "&apiKey=" + profile.POLYGON_API_KEY).json()
    return tickers

def get_less_tickers_polygon():
    tickers = []

    df = pd.read_csv('./data/tickers/polygon_list.csv')

    df1 = df[df['exchange'].str.match('XNAS')]
    df2 = df[df['exchange'].str.match('XNYS')]

    df = df1.append(df2)

    df = df[~df['name'].str.contains('ETF')]
    df.reset_index(drop = True, inplace = True)
    print(df.info())
    #print(df)

    df.to_csv('./data/tickers/smaller_polygon_list.csv', index = False)

def get_open_close(date = market_day.prev_open()):
    print("Getting Daily Open Close")
    datas = asyncio.run(scan(date))
    for data in datas:
        with open('./data/historical/polygon_daily/{}.csv'.format(data['ticker']), 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([data['ticker'], data['date'], data['open'], data['high'], data['low'], data['close'], data['volume']])
    
if __name__ == '__main__':
    print("Let's get some data!")

    #run this if trader.py was not terminated correctly.
    get_open_close()