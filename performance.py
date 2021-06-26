import alpaca_trade_api as tradeapi
from datetime import datetime
import csv, pytz
import gap, profile, datamine, telegram_bot, market_day

# get and record last market day's performance
def summary(api):
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')
    print('Equity       : ${}'.format(round(float(account.equity), 2)))
    print('Buying Power : ${}'.format(round(float(account.buying_power), 2)))

    #Get Profit/Loss
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s P/L: ${round(balance_change, 2)}')

    #Today's Equity Change
    today = datetime.today().strftime("%Y-%m-%d")
    performance = api.get_portfolio_history(period = "1D", timeframe = "1H", date_end = today, extended_hours = False)
    with open('./data/performance/alpaca.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        # equity = round(performance.equity, 2)
        # change = round(performance.profit_loss, 2)
        # change_pct = round(performance.profit_loss_pct, 2)
        for i in range(len(performance.equity)):
            tz = pytz.timezone('America/New_York')
            time = datetime.utcfromtimestamp(performance.timestamp[i]).replace(tzinfo=pytz.utc).astimezone(tz)
            equity = round(float(performance.equity[i]))
            pl = round(float(performance.profit_loss[i]))
            pl_pct = round(float(performance.profit_loss_pct[i]))
            csvwriter.writerow([time, equity, pl, pl_pct])

    #Today's Orders
    timestamp = today + "T00:00:00Z"
    timestamp2 = today + "T23:59:59Z"
    trades = api.get_activities(activity_types="FILL", direction="asc", date=today)
    with open('./data/performance/alpaca_trades.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        for trade in trades:
            csvwriter.writerow([trade.symbol, trade.side, trade.qty, trade.price])
