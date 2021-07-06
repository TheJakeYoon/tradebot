import datetime, random, csv
from os import PRIO_USER, listdir
from os.path import isfile, join
import pandas as pd
import matplotlib.pyplot as plt
import market_day

def random_date():
    start_date = datetime.date(2011, 1, 1)
    end_date = datetime.date(2018, 1, 1)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    return random_date

def analyze():
    print("Analyzing")
    tickers = pd.read_csv("./data/tickers/quandl.csv")['ticker'].tolist()

    date = random_date()
    #print(date)
    date = market_day.prev_open(date).strftime("%Y-%m-%d")
    prev = market_day.prev_open(date).strftime("%Y-%m-%d")
    #print(date)
    #print(prev)

    with open('./data/analysis/gap_run_3_20.csv', mode='w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['index', 'date', 'ticker', 'prev_close', 'open', 'extreme', 'chg_pct', 'reverted, max_profit'])

        index = -1
        count = 0
        for ticker in tickers:
            try:
                df = pd.read_csv("./data/historical/quandl/{}.csv".format(ticker))
                value = df.loc[df['date'] == date]
                close = round(value['adj_close'].iloc[-1], 2)
                value = df.loc[df['date'] == prev]
                today_open = round(value['adj_open'].iloc[-1], 2)
                result = 0
                reverted = None

                chg_pct = ((today_open - close) / close) * 100
                chg_pct = round(chg_pct, 2)

                #print(close, open, chg_pct)
                write = False
                if chg_pct > 5 and chg_pct < 8:
                    write = True
                    result = round(value['adj_low'].iloc[-1], 2)
                    #print(result)
                    if result < (today_open - (today_open * 0.03)):
                        reverted = True
                        count += 1
                    else:
                        reverted = False
                elif chg_pct < -5 and chg_pct > -8:
                    write = True
                    result = round(value['adj_high'].iloc[-1], 2)
                    #print(result)
                    if result > ((today_open * 0.03) + today_open):
                        reverted = True
                        count += 1
                    else:
                        reverted = False
                if write:
                    index += 1
                    profit_pct = abs(result - today_open) / today_open
                    profit_pct = round(profit_pct * 100, 2)
                    csvwriter.writerow([index, date, ticker, close, today_open, result, chg_pct, reverted, profit_pct])
            except Exception as e:
                pass

    with open('./data/analysis/gap_results.csv', mode='a') as csvfile:
        csvwriter = csv.writer(csvfile)
        pct = round((count / (index + 1) ) * 100, 2)
        csvwriter.writerow([date, index + 1, count, pct])



if __name__ == '__main__':
    print("Testing Gap Strategy")
    analyze()