import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

if __name__ == '__main__':
    df = pd.read_csv("./data/backtest/polygon_minute/CHWY.csv")
    graph_candlestick(df)



