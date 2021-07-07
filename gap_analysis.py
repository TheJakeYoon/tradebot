import csv
import pandas as pd
import market_day

def analyze1(min_pct, max_pct, date):
    print(date)

    df = pd.read_csv("./data/backtest/polygon_tickers/{}.csv".format(date))
    tickers = df['ticker'].tolist()

    full_reversed = 0
    half_reversed = 0
    no_reversed = 0
    prev_open = market_day.prev_open(date)
    num_tickers = len(tickers)
    num_scanned = 0
    num_error = 0
    total_half_pct = 0
    total_full_pct = 0

    for ticker in tickers:
        try:
            df = pd.read_csv("./data/backtest/polygon_daily/{}.csv".format(ticker))
            df_prev = df.loc[df['date'] == prev_open]
            prev_close = df_prev['close'].iloc[-1]
            df = df.loc[df['date'] == date]
            today_open = df['open'].iloc[-1]
            today_low = df['low'].iloc[-1]
            today_high = df['high'].iloc[-1]

            pct = ((today_open - prev_close) / prev_close) * 100
            # print("GAP: {}".format(pct))
            if pct > min_pct and pct < max_pct:
                num_scanned += 1
                gap_size = today_open - prev_close
                if today_low < today_open - (gap_size/2):
                    half_reversed += 1
                if today_low < prev_close:
                    full_reversed += 1
                else:
                    no_reversed += 1
            elif pct < -min_pct and pct > -max_pct:
                num_scanned += 1
                gap_size = prev_close - today_open
                if today_high > today_open + (gap_size/2):
                    total_half_pct += (pct/2)
                    half_reversed += 1
                if today_high > prev_close:
                    full_reversed += 1
                else:
                    no_reversed += 1
        except Exception as e:
            # print(e)
            num_error += 1
            pass

    # print("{} Total tickers:{} Scanned tickers:{} Reversed:{} Half-Reversed:{} Fill %:{} Half-Fill %:{}".format(date, num_tickers, num_scanned, full_reversed, half_reversed, round(full_reversed/num_scanned, 2), round(half_reversed/num_scanned, 2)))
    with open('./data/backtest/results/analysis_05_10.csv', 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([date, round((full_reversed/num_scanned) * 100, 2), round((half_reversed/num_scanned) * 100, 2), min_pct, max_pct, num_tickers, num_scanned, num_error, full_reversed, half_reversed])

def analyze2(min_pct, max_pct, date):
    print("Analyzing")

    df = pd.read_csv("./data/backtest/polygon_tickers/{}.csv".format(date))
    tickers = df['ticker'].tolist()

    full_reversed = 0
    half_reversed = 0
    no_reversed = 0
    prev_open = market_day.prev_open(date)
    num_tickers = len(tickers)
    num_scanned = 0

    for ticker in tickers:
        try:
            df = pd.read_csv("./data/backtest/polygon_daily/{}.csv".format(ticker))
            df_prev = df.loc[df['date'] == prev_open]
            prev_close = df_prev['close'].iloc[-1]
            prev_low = df_prev['low'].iloc[-1]
            prev_high = df_prev['high'].iloc[-1]
            df = df.loc[df['date'] == date]
            today_open = df['open'].iloc[-1]
            today_low = df['low'].iloc[-1]
            today_high = df['high'].iloc[-1]

            pct = ((today_open - prev_close) / prev_close)
            if pct > min_pct/100 and pct < max_pct/100 and today_open < prev_high:
                num_scanned += 1
                if today_low < prev_close:
                    # print("Gap Closed")
                    full_reversed += 1
                else:
                    # print("Gap didn't close")
                    no_reversed += 1
            elif pct < -min/100 and pct > -max/100 and today_open > prev_low:
                num_scanned += 1
                if today_high > prev_close:
                    full_reversed += 1
                else:
                    no_reversed += 1
        except Exception as e:
            pass

    print("{} Total tickers:{} Scanned tickers:{} Reversed:{} Fill %:{}".format(date, num_tickers, num_scanned, full_reversed, round(full_reversed/num_scanned, 2)))
    # while date != market_day.next_open("2021-07-01"):
    #     df = pd.read_csv("./data/backtest/polygon_tickers")
    #     tickers = df['ticker'].tolist()
    
if __name__ == '__main__':
    print("Testing Gap Strategy")

    date = market_day.next_open("2010-01-04")

    while date != market_day.next_open("2011-01-01"):
        analyze1(0.5, 1, date)
        date = market_day.next_open(date)