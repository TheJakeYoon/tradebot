from datetime import datetime
import alpaca_trade_api as tradeapi
from numpy import row_stack
import pytz, requests, json, time, csv
import pandas as pd
import market_day, gap, profile, performance, telegram_bot

start = datetime.now()

api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

prev_closes = gap.get_close()

print(datetime.now() - start)
start = datetime.now()

tickers = gap.scan(api, prev_closes)
print(tickers)
print(datetime.now() - start)
start = datetime.now()

gap.order(api, tickers)
gap.order_v2(api, tickers)
# telegram_bot.send_message("Order Finished")

# get runtime
print(datetime.now() - start)

# df = pd.read_csv("./data/backtest/results/backtest_2.csv")
# avg_pct = df['pct'].sum() / len(df.index)
# print(avg_pct)

# print(len(onlyfiles))

# issuefiles = []
# issuecontents = []

# for file in onlyfiles:
#     with open("./data/backtest/polygon_daily/{}".format(file), "r") as csvfile:
#         row = next(csv.reader(csvfile))
#         if row[0] != "ticker":
#             issuefiles.append(file)
#             issuecontents.append(list(csv.reader(csvfile)))

# print(len(issuefiles))

# # cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
# # i = 0
# # for file in issuefiles:
# #     with open("./data/backtest/polygon_daily/{}".format(file), "w", newline="") as csvfile:
# #         csvwriter = csv.writer(csvfile)
# #         csvwriter.writerow(cols)
# #         for row in issuecontents[i]:
# #             # print(row)
# #             csvwriter.writerow(row)
