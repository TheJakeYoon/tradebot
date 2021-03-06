import alpaca_trade_api as tradeapi
import time
import gap, profile, market_day, datamine, telegram_bot, performance
import pandas as pd

#TRADE BOT
if __name__ == '__main__':

    #Prevents the computer from sleeping MAC ONLY!
    #caffeine.on()

    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

    # run forever!
    while True:
        print("Trading Bot Started!")
        today = market_day.today()
        prev_day = market_day.prev_open(today)
        print(today)
        print(market_day.now())

        if api.get_clock().is_open:
            print("Market Open!")
            print(market_day.now())
        else:
            print("Market Closed")
            print(market_day.now())

        prev_closes = gap.get_close(prev_day)
        print("Total Prev Closes: {}".format(len(prev_closes)))

        market_time = market_day.now()
        while market_time != "09:30":
            market_time = market_day.now()

        if api.get_clock().is_open:
            print("Scanning for stocks")
            tickers = gap.scan(api, prev_closes)

            print("Ordering now")
            gap.order(api, tickers)
            #Place stop limit and take profit order
            # gap.order_v2(api, tickers)
            
            print("Order finished Done!")

            telegram_bot.send_message("Order Finished!")

            df = pd.DataFrame(tickers)
            df.to_csv("./orders/{}.csv".format(today))

            while api.list_positions() is not None and market_time != "12:01":
                time.sleep(10)
                market_time = market_day.now()
                if market_time == "12:01":
                    pass
                    #Strategy specific!!!!!!
                    api.cancel_all_orders()
                    gap.order_v3(api)

            time.sleep(1800)

            api.cancel_all_orders()
            gap.order_v4(api)
            time.sleep(1800)
            api.cancel_all_orders()
            gap.close(api)

            print("All positions closed now")
            telegram_bot.send_message("All positions closed now!")

            #Wait until after hour closed
            print("Waiting for after hour to close")
            while market_time != "20:05":
                time.sleep(10)
                market_time = market_day.now()

            while market_time != "23:59":
                time.sleep(10)
                market_time = market_day.now()

            time.sleep(300)

            #get daily open close from Polygon.io
            datamine.get_tickers_alpaca()
            datamine.get_open_close(today)
            telegram_bot.send_message("Stored daily open/close from Polyon.io {}".format(today))

            #Saves daily performance
            try:        
                performance.summary(api)
            except Exception as e:
                print(e)
            performance.today(api)
        else:
            while market_time != "23:59":
                time.sleep(10)
                market_time = market_day.now()
        time.sleep(60)
