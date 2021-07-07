#### This trading bot uses Open Gap Reversal strategy using data from Polyon.io and brokerage from Alapca

##### Upon researching, backtesting, and testing with paper trading, average daily return is 0.5% - 0.7% and average monthly return is 10% - 15% (Alpaca is commission free)

## How to use

Run trader.py for main trading
Run telegram_bot.py to send/recieve updates via Telegram (/help for list of commands)


## Requirements

python --version = 3.9.5
pip --version = 21.1.2
size = 2.4g
required modules found in requirements.txt

## Strategy

### Open Gap Reversal ###

There's a common saying - "All gaps are filled"
While most gaps do fill, it can take days or weeks and simply taking the opposite trade of the open gap is not wise.

This bot will find stocks that gap without catalysts (news, announcements, earnings reports, etc.) AND stocks that are not in a down/up trend.

This bot will find open gaps in 2 - 5% range (Gaps lower than %2 are hard to profit and higher than 5% have a lower probability of reversing) and look for profit target of half of the open gap. Stop loss will be full open gap percent.