import math, asyncio, csv, caffeine
import datamine, market_day, gap_backtest, async_aiohttp
import pandas as pd

class Account:
    def __init__(self, Backtest):
        self.buying_power = Backtest.amount

class Trade:
    def __init__(self, ticker, time):
        df = pd.read_csv("./data/backtest/polygon_minute/{}.csv".format(ticker))
        self.price = df.loc[df["date"] == time]["open"].iloc[-1]

def process_order(Backtest, time, symbol, qty, side, entry_price, stop_loss, take_profit):
    try:
        df = pd.read_csv("./data/backtest/polygon_minute/{}.csv".format(symbol))
        price = df.loc[df["date"] == time]["open"].iloc[-1]
        # print("{} - {}".format(price, entry_price))
        if price == entry_price:
            # print("Order Successful")
            initial_cash = 5000
            print(symbol)
            print(price, take_profit, stop_loss)
            order_open = True
            while order_open:
                if side == "buy":
                    price = df.loc[df["date"] == time]["low"].iloc[-1]
                    if price < stop_loss:
                        print("Stop Loss Reached")
                        Backtest.loss += 1
                        print(time)
                        order_open = False
                        Backtest.initial_cash += qty * entry_price
                        Backtest.amount += qty * entry_price
                        Backtest.amount -= round((entry_price - stop_loss) * qty, 2)
                    else:
                        price = df.loc[df["date"] == time]["high"].iloc[-1]
                        if price < stop_loss:
                            print("Take Profit Reached")
                            Backtest.profit += 1
                            print(time)
                            order_open = False
                            Backtest.initial_cash += qty * entry_price
                            Backtest.amount += qty * entry_price
                            Backtest.amount += round((take_profit - entry_price) * qty, 2)        
                elif side == "sell":
                    price = df.loc[df["date"] == time]["high"].iloc[-1]
                    if price > stop_loss:
                        print("Stop Loss Reached")
                        Backtest.loss += 1
                        print(time)
                        order_open = False
                        Backtest.initial_cash += qty * entry_price
                        Backtest.amount += qty * entry_price
                        Backtest.amount -= round((stop_loss - entry_price) * qty, 2)
                    else:
                        price = df.loc[df["date"] == time]["low"].iloc[-1]
                        if price < take_profit:
                            print("Take Profit Reached")
                            Backtest.profit += 1
                            print(time)
                            order_open = False
                            Backtest.initial_cash += qty * entry_price
                            Backtest.amount += qty * entry_price
                            Backtest.amount += round((entry_price - take_profit) * qty, 2)
                time = market_day.next_minute(time)
                temp = time.split(" ", 2)[1]
                if temp == "12:00":
                    price = df.loc[df["date"] == time]["close"].iloc[-1]
                    print("Noon Reached")
                    order_open = False
                    Backtest.timed_out += 1
                    if side == "buy":
                        Backtest.initial_cash += qty * entry_price
                        Backtest.amount += qty * entry_price
                        Backtest.amount += round((price - entry_price) * qty, 2)
                    elif side == "sell":
                        Backtest.initial_cash += qty * entry_price
                        Backtest.amount += qty * entry_price
                        Backtest.amount += round((entry_price - price) * qty, 2)
        return 0
    except Exception as e:
        print(e)
        print(time)
        print(symbol)
        return 1

class Order:
    def __init__(self, Backtest, time, symbol, qty, side, price, stop_loss, take_profit):
        self.Backtest = Backtest
        self.symbol = symbol
        self.qty = qty
        self.side = side
        self.failed_order = 0
        try:
            df = pd.read_csv("./data/backtest/polygon_minute/{}.csv".format(symbol))
            price = df.loc[df["date"] == time]["open"].iloc[-1]
        except Exception as e:
            print(e)

        self.failed_order += process_order(Backtest, time, symbol, qty, side, price, stop_loss, take_profit)

class Backtest:
    def __init__(self, start_amount, start_date, end_date):
        self.initial_cash = 0
        self.start_amount = 0
        self.amount = 0
        self.start_date = start_date
        self.end_date = end_date
        self.time = "{} 09:30".format(start_date)
        self.profit = 0
        self.loss = 0
        self.timed_out = 0

        self.positions = []

    def get_account(self):
        return Account(self)

    def get_last_trade(self, ticker):
        return Trade(ticker, self.time)

    def submit_order(self, symbol, qty, side, entry_price, stop_loss, take_profit):
        order = Order(self, self.time, symbol, qty, side, entry_price, stop_loss, take_profit)
        return order.failed_order


if __name__ == '__main__':

    caffeine.on()

    date = "2019-01-01"

    while date != market_day.next_open("2020-01-01"):
        date = market_day.next_open(date)
        print(date)
        prev_date = market_day.prev_open(date)
        backtest = Backtest(10000, date, date)

        tickers = datamine.get_tickers_polygon_list(prev_date)

        # save previous day's open close
        datamine.get_open_close_backtest(tickers, prev_date)
        prev_closes = gap_backtest.get_close(tickers)
        print(len(prev_closes))

        gappers = gap_backtest.scan(None, prev_closes, date)

        print(len(gappers))
        # print(gappers)

        # save today's minute bars 
        asyncio.run(async_aiohttp.scan(gappers, date))

        failed_order = 0
        for ticker in gappers:
            price = ticker['current_price']
            profit_pct = abs(ticker['pct'] / 1.25)
            loss_pct = abs(ticker['pct'])
            qty = math.floor(5000 / price)
            if ticker['side'] == "buy":
                stop_loss = price * (1 - (loss_pct/100))
                take_profit = price * (1 + (profit_pct/100))
            elif ticker['side'] == "sell":
                stop_loss = price * (1 + (loss_pct/100))
                take_profit = price * (1 - (profit_pct/100))
            failed_order += backtest.submit_order(ticker['ticker'], qty, ticker['side'], price, stop_loss, take_profit)
        pct = round((backtest.amount - backtest.initial_cash) / backtest.initial_cash * 100, 2)
        print(backtest.initial_cash)
        print(backtest.amount)
        print(pct)
        print("Total : {} Stop : {} Profit: {}  Closed on Noon:  {} Failed:  {}".format(len(gappers), backtest.loss, backtest.profit, backtest.timed_out, failed_order))
        with open('./data/backtest/results/backtest_2.csv', 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([date, round(backtest.initial_cash, 2), round(backtest.amount, 2), pct, len(gappers), backtest.loss, backtest.profit, backtest.timed_out, failed_order])