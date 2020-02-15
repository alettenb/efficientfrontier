"""Python file for scraping data from Yahoo! Finance."""

import yahoofinancials as yf
import pandas as pd
import numpy as np

def get_last_first_trade_date(stocks):
    """
    Returns the start of the month of the first trade date.
    Params:
    stocks: List of stocks that you are looking at.
    """
    stock_financials = yf.YahooFinancials(stocks)
    today = str(yf.datetime.date.today())
    prices = stock_financials.get_historical_price_data(
        today, 
        today, 
        'monthly',)

    ftdates = []
    for st in stocks:
        ftdates.append(prices[st]['firstTradeDate']['formatted_date'])

    max_date = max(ftdates)
    max_date = max_date[: max_date.rfind('-') + 1] + '01'
    return max_date

def extract_attributes_from_stock_dataframe(
    stock,
    attributes,
    all_stock_prices
):

    """
    Given a dataframe of stock prices, along with the price and attributes we
    are looking for, returns a dataframe of the stock prices.

    Params:
    stock: A string representing the stock we are looking for.
    attributes: A list of attributes about the price we are getting.
    all_stock_prices: A dataframe from yahoo financials containing the stock
        in question's historical data.
    """
    pass



def get_data(stocks, attributes, timeframe='monthly'):
    """
    Gets data for the given stocks for each step of the timeframe.

    Params:
    stocks: A string/list of stocks that you want to get data for.
    attributes: A string/list of attributes about price that you want to get.
        Options include: adjclose, close, open, high, and low.
    timeframe: The time step you want to get data for. Includes daily, weekly,
        monthly. 
    """

    # If there is only a string passed in, convert it to an array.
    if (type(stocks) == str):
        stocks = [stocks]
    if (type(attributes) == str):
        attributes = [attributes]

    # Gets the most recent IPO date.
    stock_financials = yf.YahooFinancials(stocks)
    today = str(yf.datetime.date.today())
    first_trade = get_last_first_trade_date(stocks)

    prices_together = stock_financials.get_historical_price_data(
        first_trade,
        today,
        timeframe,
    )

    df = None
    for s in stocks:
        prices_dict = {}
        p = prices_together[s]['prices']
        date = []
        for a in attributes:
            prices_dict[s + '.' + a] = []

        for json in p:
            date.append(json['formatted_date'])
            for a in attributes:
                prices_dict[s + '.' + a].append(json[a])
            
        prices_dict['date'] = date
        
        d = pd.DataFrame(data = prices_dict)
        if df is None:
            df = d
        else:
            df = df.merge(d)
    df = df.set_index('date')

    arr = []
    for c in df.columns:
        dot_ind = c.find('.')
    
        arr.append((c[: dot_ind], c[dot_ind + 1 :]))
    
    df.columns = pd.MultiIndex.from_tuples(arr, names=('Stock', 'Attribute'))
     
    return df

def get_returns(stocks, timeframe='monthly'):
    """
    Returns a dataframe of returns for given stocks.
    Params:
    stocks: String or list of stocks you want to get it for.
    timeframe: The timeframe you want to get it for. Can do daily, weekly, monthly.
    """
    if (type(stocks) == str):
        stocks = [stocks]

    df_init = get_data(stocks, 'adjclose', timeframe=timeframe)

    expected_returns = {}
    expected_returns['date'] = []
    for s in stocks:
        expected_returns[s] = []

    for i in range(1, len(df_init)):
        old_row = df_init.iloc[i-1]
        new_row = df_init.iloc[i]
        
        expected_returns['date'].append(new_row.name)

        for s in stocks:
            er = (new_row[s, 'adjclose'] - old_row[s, 'adjclose']) / old_row[s, 'adjclose']
            expected_returns[s].append(er)

    df = pd.DataFrame(data=expected_returns)
    df = df.set_index('date')

    
    return df
