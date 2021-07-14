import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import market_day

#Referenced from Udemy Algorithmic Trading

#Returns Compound Annual Growth Rate in percentage
#Input: dataframe containing equity
def cagr(DF):
    df = DF.copy()
    df['daily_return'] = DF['equity'].pct_change()
    df['cum_return'] = (1 + df['daily_return'].cumprod())
    n = len(df)/252
    CAGR = ((df['equity'].iloc[-1] / df['equity'].iloc[0]) ** (1/n)) - 1
    return round(CAGR * 100, 2)

#Returns volatility percentage (How much on average it moves up or down)
#Input: dataframe containing closing prices
def volatility(DF):
    df = DF.copy()
    df['daily_return'] = df['equity'].pct_change()
    volatility = df['daily_return'].std()
    return round(volatility * 100, 2)

#Returns Sharpe Ratio
#Greater than 1 is good
#Greater than 2 is really good
#Input: dataframe containing closing prices, risk free return in decimal form
def sharpe(DF, risk_free_return):
    df = DF.copy()
    sharpe = (cagr(df) - risk_free_return) / volatility(df)
    return round(sharpe, 2)

#Returns Sortino Ratio which takes negative return into account
#Smaller the negative number, better it will be
#Input: dataframe containing closing prices, risk free return in decimal form
def sortino(DF, risk_free_return):
    df = DF.copy()
    df['daily_return'] = DF['equity'].pct_change()
    neg_vol = df[df['daily_return'] < 0]['daily_return'].std() * np.sqrt(252)
    sortino = (cagr(df) - risk_free_return) / neg_vol
    return round(sortino, 2)
#Returns maximum drop in percentage
#Input: dataframe containing closing prices
def max_drawdown(DF):
    df = DF.copy()
    df['daily_return'] = DF['equity'].pct_change()
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    df['cum_roll_max'] = df['cum_return'].cummax()
    df['drawdown'] = df['cum_roll_max'] - df['cum_return']
    df['drawdown_pct'] = df['drawdown'] / df['cum_roll_max']
    return round(df['drawdown_pct'].max() * 100, 2)

#Returns Calmar Ratio which shows risk or downside
#Input: dataframe containing closing prices
def calmar(DF):
    df = DF.copy()
    return cagr(df) / max_drawdown(df)

def graph_performance(df):
    print("CAGR = {}%".format(cagr(df)))
    print("Volatility = {}%".format(volatility(df)))
    print("Sharpe Ratio = {}".format(sharpe(df, 0.02)))
    print("Sortino Ratio = {}".format(sortino(df, 0.02)))
    print("Max Drawdown = {}%".format(max_drawdown(df)))

    fig = plt.figure(figsize=(12,8))

    ax = fig.add_subplot(211)
    ax.set_title("Equity")
    ax.semilogy(df['equity'], linestyle='-', label='Equity', linewidth=3)
    ax.set_yscale("linear")
    ax.set_ylabel("USD")
    ax.legend()

    ax = fig.add_subplot(212)
    ret_pct = df['equity'].pct_change(periods=1) * 100
    ax.set_title("Daily Return %")
    ax.semilogy(ret_pct, linestyle='-', label='% Return', linewidth=3)
    ax.set_yscale("linear")
    ax.set_xlabel("Days")
    ax.set_ylabel("%")
    ax.legend()

    ax.grid(False)
    plt.show()

def graph_candlestick(df):
    fig = go.Figure(data = [go.Candlestick(x = df['date'], open = df['open'], high = df['high'], low = df['low'], close = df['close'])])
    fig.show()

def get_fill_pct(DF, min_pct, max_pct):
    df = DF.copy()
    df_1 = df[(df['gap'] < -min_pct) & (df['gap'] > -max_pct)]
    df_2 = df[(df['gap'] < max_pct) & (df['gap'] > min_pct)]
    df_1.append(df_2)
    df_3 = df_1[(df_1['full_fill'] == 1)]
    if len(df_1.index) == 0:
        return -1
    return round(len(df_3.index) / len(df_1.index) * 100, 2)

def get_half_fill_pct(DF, min_pct, max_pct):
    df = DF.copy()
    df_1 = df[(df['gap'] < -min_pct) & (df['gap'] > -max_pct)]
    df_2 = df[(df['gap'] < max_pct) & (df['gap'] > min_pct)]
    df_1.append(df_2)
    df_3 = df_1[(df_1['half_fill'] == 1)]
    if len(df_1.index) == 0:
        return -1
    return round(len(df_3.index) / len(df_1.index) * 100, 2)

def get_fill_pct_vol(DF, min_pct, max_pct, volume):
    df = DF.copy()
    df_1 = df[(df['gap'] < -min_pct) & (df['gap'] > -max_pct) & (df['volume'] > volume)]
    df_2 = df[(df['gap'] < max_pct) & (df['gap'] > min_pct) & (df['volume'] > volume)]
    df_1.append(df_2)
    df_3 = df_1[(df_1['full_fill'] == 1)]
    if len(df_1.index) == 0:
        return -1
    return round(len(df_3.index) / len(df_1.index) * 100, 2)

def get_half_fill_pct_vol(DF, min_pct, max_pct, volume):
    df = DF.copy()
    df_1 = df[(df['gap'] < -min_pct) & (df['gap'] > -max_pct) & (df['volume'] > volume)]
    df_2 = df[(df['gap'] < max_pct) & (df['gap'] > min_pct) & (df['volume'] > volume)]
    df_1.append(df_2)
    df_3 = df_1[(df_1['half_fill'] == 1)]
    if len(df_1.index) == 0:
        return -1
    return round(len(df_3.index) / len(df_1.index) * 100, 2)

if __name__ == '__main__':
    # df = pd.read_csv("./data/backtest/polygon_minute/2010-01-11/HI.csv")
    # graph_candlestick(df)

    dates = []
    today_pct = []
    fill_pct = []
    fill_pct_vol = []
    half_pct = []
    half_pct_vol = []

    date = "2010-02-03"
    while date != "2010-03-11":
        # print(date)
        dates.append(date)
        df = pd.read_csv("./data/backtest/results/{}_analysis.csv".format(date))
        pct = get_fill_pct(df, -10000, 10000)
        min_pct = 2
        max_pct = 5
        volume = 100000
        today_pct.append(pct)
        pct = get_fill_pct(df, min_pct, max_pct)
        fill_pct.append(pct)
        pct = get_fill_pct_vol(df, min_pct, max_pct, volume)
        fill_pct_vol.append(pct)
        pct = get_half_fill_pct(df, min_pct, max_pct)
        half_pct.append(pct)
        pct = get_half_fill_pct_vol(df, min_pct, max_pct, volume)
        half_pct_vol.append(pct)

        date = market_day.next_open(date)


    plt.plot(dates, today_pct, label="%")
    plt.plot(dates, fill_pct, label="Fill %")
    plt.plot(dates, fill_pct_vol, label="Fill % Vol")
    plt.plot(dates, half_pct, label="Half %")
    plt.plot(dates, half_pct_vol, label="Half % Vol")
    plt.title("{}% - {}% Gaps with {} Volume".format(min_pct, max_pct, volume))
    plt.legend()
    plt.grid()
    plt.show()