import csv, requests, asyncio, aiohttp
import profile, market_day
import alpaca_trade_api as tradeapi
from alpaca_trade_api import REST
from datetime import datetime
import pandas as pd

async def get_APIdata(session, url, datas):
    async with session.get(url) as response:
        try:
            result = await response.json()
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
            # print(e)
            pass

async def scan(date):
    df = pd.read_csv('./data/tickers/assets_list.csv')

    errors = []

    tickers = df['ticker'].tolist()

    datas = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for ticker in tickers:
            url = "https://api.polygon.io/v1/open-close/{}/{}?adjusted=true&apiKey={}".format(ticker, date, profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, url, datas))
            tasks.append(task)
        await asyncio.gather(*tasks)

    return datas

def get_tickers_alpaca():
    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

    assets = api.list_assets(status='active')
    count = 0
    ticker = ['ticker']
    with open('./data/tickers/assets_list.csv', mode='w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(ticker)
        for asset in assets:
            if asset.tradable and asset.shortable and asset.easy_to_borrow and '.' not in asset.symbol:
                count += 1
                ticker = [asset.symbol]
                csvwriter.writerow(ticker)
        print("{} stocks stored in assets_list.csv".format(count))

def get_tickers_polygon(date = market_day.prev_open()):
    tickers = []

    with open('./data/tickers/polygon_list.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['ticker', 'name', 'locale', 'exchange'])
        url = "https://api.polygon.io/v3/reference/tickers?date={}&active=true&sort=ticker&order=asc&limit=1000&apiKey={}".format(date, profile.POLYGON_API_KEY)
        response = requests.get(url).json()
        while 'next_url' in response:
            #print(response['next_url'])
            for ticker in response['results']:
                if 'locale' in ticker and '.' not in ticker['ticker'] and len(ticker['ticker']) < 5:
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
    print("Getting Daily Open Close {}".format(date))
    datas = asyncio.run(scan(date))
    for data in datas:
        with open('./data/historical/polygon_daily/{}.csv'.format(data['ticker']), 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['ticker','date','open','high','low','close','volume'])
            csvwriter.writerow([data['ticker'], data['date'], data['open'], data['high'], data['low'], data['close'], data['volume']])

if __name__ == '__main__':

    print("Let's get some data!")
    # run this if trader.py was not terminated correctly.
    start = datetime.now()
    get_open_close()
    print(datetime.now() - start)