import csv
import telegram_bot, market_day, profile
import alpaca_trade_api as tradeapi

# get and record last market day's performance
def summary(api):
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')
    # print('Equity       : ${}'.format(round(float(account.equity), 2)))
    # print('Buying Power : ${}'.format(round(float(account.buying_power), 2)))

    # #Get Profit/Loss
    # balance_change = float(account.equity) - float(account.last_equity)
    # print(f'Today\'s P/L: ${round(balance_change, 2)}')

    # Get today's hourly equity change
    today = market_day.today()
    performance = api.get_portfolio_history(period = "1D", timeframe = "1H", date_end = today, extended_hours = False)
    with open('./data/performance/alpaca_hour.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        # equity = round(performance.equity, 2)
        # change = round(performance.profit_loss, 2)
        # change_pct = round(performance.profit_loss_pct, 2)
        for i in range(len(performance.equity)):
            time = market_day.timestamp_to_est(performance.timestamp[i])
            equity = round(float(performance.equity[i]))
            pl = round(float(performance.profit_loss[i]))
            pl_pct = round(float(performance.profit_loss_pct[i]))
            csvwriter.writerow([time, equity, pl, pl_pct])

    # Get today's minute equity change
    performance = api.get_portfolio_history(period = "1D", timeframe = "1M", date_end = today, extended_hours = False)
    with open('./data/performance/alpaca_minute.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        # equity = round(performance.equity, 2)
        # change = round(performance.profit_loss, 2)
        # change_pct = round(performance.profit_loss_pct, 2)
        for i in range(len(performance.equity)):
            time = market_day.timestamp_to_est(performance.timestamp[i])
            equity = round(float(performance.equity[i]))
            pl = round(float(performance.profit_loss[i]))
            pl_pct = round(float(performance.profit_loss_pct[i]))
            csvwriter.writerow([time, equity, pl, pl_pct])

    #Today's Orders
    trades = api.get_activities(activity_types="FILL", direction="asc", date=today)
    with open('./data/performance/alpaca_trades.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        for trade in trades:
            csvwriter.writerow([trade.symbol, trade.side, trade.qty, trade.price])

def today(api):
    account = api.get_account()
    
    date = market_day.today()

    equity = round(float(account.equity), 2)
    balance_change = float(account.equity) - float(account.last_equity)
    balance_change = round(balance_change, 2)

    pct = round((balance_change / float(account.last_equity)) * 100, 2)

    with open('./performance/alpaca.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([date, equity, balance_change, pct])

    telegram_bot.send_message("Equity is {}".format(round(float(account.equity), 2)))

    if balance_change > 0:
        telegram_bot.send_message("You made {} today! Nice!".format(balance_change))
        telegram_bot.send_message("That's {}% profit! Nice!".format(pct))
    elif balance_change == 0:
        telegram_bot.send_message("You didn't make any money today...")
    else:
        telegram_bot.send_message("You lost {} today... Sorry...".format(balance_change))
        telegram_bot.send_message("That's {}% loss...".format(pct))

if __name__ == '__main__':
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

    #Saves daily performance        
    summary(api)
    today(api)