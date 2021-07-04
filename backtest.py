import math, asyncio, csv
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
            # print(price)
            order_open = True
            while order_open:
                if side == "buy":
                    price = df.loc[df["date"] == time]["low"].iloc[-1]
                    if price < stop_loss:
                        print("Stop Loss Reached")
                        order_open = False
                        Backtest.amount -= round((entry_price - stop_loss) * qty, 2)
                    else:
                        price = df.loc[df["date"] == time]["high"].iloc[-1]
                        if price < stop_loss:
                            print("Take lossProfit Reached")
                            order_open = False
                            Backtest.amount += round((take_profit - entry_price) * qty, 2)        
                elif side == "sell":
                    price = df.loc[df["date"] == time]["high"].iloc[-1]
                    if price > stop_loss:
                        print("Stop Loss Reached")
                        order_open = False
                        Backtest.amount -= round((stop_loss - entry_price) * qty, 2)
                    else:
                        price = df.loc[df["date"] == time]["low"].iloc[-1]
                        if price < take_profit:
                            print("Take Profit Reached")
                            order_open = False
                            Backtest.amount += round((entry_price - take_profit) * qty, 2)
                time = market_day.next_minute(time)
                temp = time.split(" ", 2)[1]
                if temp == "16:00":
                    price = df.loc[df["date"] == time]["close"].iloc[-1]
                    print("End of Day Reached")
                    order_open = False
                    if side == "buy":
                        Backtest.amount += round((price - entry_price) * qty, 2)
                    elif side == "sell":
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
        self.start_amount = start_amount
        self.amount = start_amount
        self.start_date = start_date
        self.end_date = end_date
        self.time = "{} 09:30".format(start_date)

        self.positions = []

    def get_account(self):
        return Account(self)

    def get_last_trade(self, ticker):
        return Trade(ticker, self.time)

    def submit_order(self, symbol, qty, side, entry_price, stop_loss, take_profit):
        order = Order(self, self.time, symbol, qty, side, entry_price, stop_loss, take_profit)
        return order.failed_order


if __name__ == '__main__':

    date = market_day.random_date()
    print(date)
    prev_date = market_day.prev_open(date)
    Backtest = Backtest(10000, date, date)
    initial_cash = Backtest.amount
    print("Starting Cash : {}".format(initial_cash))

    tickers = datamine.get_tickers_polygon_list(prev_date)

    # save previous day's open close
    datamine.get_open_close_backtest(tickers, prev_date)
    prev_closes = gap_backtest.get_close(tickers)
    print(len(prev_closes))

    gappers = gap_backtest.scan(None, prev_closes, date)

    print(len(gappers))

    # save today's minute bars 
    asyncio.run(async_aiohttp.scan(gappers, date))

    initial_cash = Backtest.amount
    failed_order = 0
    for ticker in gappers:
        price = ticker['current_price']
        qty = math.floor(initial_cash * 0.1 / price)
        if ticker['side'] == "buy":
            stop_loss = price * 0.98
            take_profit = price * 1.02
        elif ticker['side'] == "sell":
            stop_loss = price * 1.02
            take_profit = price * 0.98
        failed_order += Backtest.submit_order(ticker['ticker'], qty, ticker['side'], price, stop_loss, take_profit)
        print(Backtest.amount)
    pct = round((Backtest.amount - initial_cash) / initial_cash * 100, 2)
    final_amount = (Backtest.amount - (0.1 * failed_order * initial_cash))
    init_amount = (initial_cash - (0.1 * failed_order * initial_cash))
    pct_2 = round((final_amount - init_amount) / init_amount * 100, 2)
    print(pct)
    print(pct_2)
    with open('./data/backtest/results/backtest_1.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([date, pct, init_amount, round(final_amount, 2), pct_2])
    # Backtest.submit_order("AAPL", 10, "buy", 42.4, 46)
    # print(Backtest.amount)