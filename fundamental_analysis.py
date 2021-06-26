import numpy as np

#Referenced from Udemy Algorithmic Trading

#Returns Compound Annual Growth Rate
#Input: dataframe containing closing prices
def CAGR(DF):
    df = DF.copy()
    df['daily_return'] = DF['close'].pct_change()
    df['cum_return'] = (1 + df['daily_return'].cumprod())
    n = len(df)/252
    CAGR = (df['cum_return'][-1])**(1/n) - 1
    return CAGR

#Returns volatility percentage
#Input: dataframe containing closing prices
def volatility(DF):
    df = DF.copy()
    df['daily_return'] = df['close'].pct_change()
    volatility = df['daily_return'].std() * np.sqrt(252)
    return volatility

#Returns Sharpe Ratio
#Greater than 1 is good
#Greater than 2 is really good
#Input: dataframe containing closing prices, risk free return in decimal form
def sharpe(DF, risk_free_return):
    df = DF.copy()
    sharpe = (CAGR(df) - risk_free_return) / volatility(df)
    return sharpe

#Returns Sortino Ratio which takes negative return into account
#Smaller the negative number, better it will be
#Input: dataframe containing closing prices, risk free return in decimal form
def sortino(DF, risk_free_return):
    df = DF.copy()
    df['daily_return'] = DF['close'].pct_change()
    neg_vol = df[df['daily_return'] < 0]['daily_return'].std() * np.sqrt(252)
    sortino = (CAGR(df) - risk_free_return) / neg_vol
    return sortino
#Returns maximum drop in percentage
#Input: dataframe containing closing prices
def max_drawdown(DF):
    df = DF.copy()
    df['daily_return'] = DF['close'].pct_change()
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    df['cum_roll_max'] = df['cum_return'].cummax()
    df['drawdown'] = df['cum_roll_max'] - df['cum_return']
    df['drawdown_pct'] = df['drawdown'] / df['cum_roll_max']
    return df['drawdown_pct'].max()

#Returns Calmar Ratio which shows risk or downside
#Input: dataframe containing closing prices
def calmar(DF):
    df = DF.copy()
    return CAGR(df) / max_drawdown(df)