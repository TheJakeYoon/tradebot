import asyncio, aiohttp, csv
import profile, market_day
import pandas as pd

async def get_APIdata(session, ticker, url):
    async with session.get(url) as response:
        with open('./data/backtest/polygon_minute/{}.csv'.format(ticker), 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            try:
                results = await response.json()
                results = results["results"]
                csvwriter.writerow(['ticker','date','open','high','low','close','volume'])
                for result in results:
                    csvwriter.writerow([ticker, market_day.timestamp_to_est(result['t']/1000), result['o'], result['h'], result['l'], result['c'], result['v']])
            except Exception as e:
                # print(ticker)
                # print(e)
                pass

async def scan(tickers, date):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ticker in tickers:
            url = "https://api.polygon.io/v2/aggs/ticker/{}/range/1/minute/{}/{}?adjusted=true&sort=asc&limit=5000&apiKey={}".format(ticker['ticker'], date, date, profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, ticker['ticker'], url))
            tasks.append(task)
        #tasks = [asyncio.ensure_future(get_marketcap(session, ticker, marketcap)) for ticker in tickers]
        await asyncio.gather(*tasks)
