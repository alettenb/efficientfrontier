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

def extract_attributes_from_stock_json(
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
    all_stock_prices: A json from yahoo financials containing the stock
        in question's historical data.
    """
    prices_dict = {}
    p = all_stock_prices[stock]['prices']
    date = []
    for a in attributes:
        prices_dict[stock + '.' + a] = []

    for json in p:
        date.append(json['formatted_date'])
        for a in attributes:
            prices_dict[stock + '.' + a].append(json[a])
        
    prices_dict['date'] = date
    
    return pd.DataFrame(data = prices_dict)


def get_stock_json(stocks, timeframe='monthly'):
    """
    Gets a JSON of historical stock data from yahoo financials.

    Params:
    stocks: A list of stocks you want to get data for.
    timeframe: The time step you want to get data for. Includes daily, weekly,
        monthly. 
    """

    # Gets the most recent IPO date.
    stock_financials = yf.YahooFinancials(stocks)
    today = str(yf.datetime.date.today())
    first_trade = get_last_first_trade_date(stocks)

    return stock_financials.get_historical_price_data(
        first_trade,
        today,
        timeframe,
    )


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

    # Gets a JSON of all stock prices. 
    prices_together = get_stock_json(stocks, timeframe)

    # Converts the JSON to a clean DataFrame.
    df = None
    for s in stocks:
        d = extract_attributes_from_stock_json(
            s, 
            attributes, 
            prices_together
        )
        if df is None:
            df = d
        else:
            df = df.merge(d)
    df = df.set_index('date')

    # Changes the title of the DataFrame Columns.
    arr = []
    for c in df.columns:
        dot_ind = c.find('.')
    
        arr.append((c[: dot_ind], c[dot_ind + 1 :]))
    
    df.columns = pd.MultiIndex.from_tuples(arr, names=('Stock', 'Attribute'))
     
    return df

def derive_returns(stocks, price_dataframe):
    """
    Given stocks and a dataframe containing closing prices, derives monthly
    returns.

    Params:
    stocks: A list of stocks you are looking at.
    price_dataframe: A dataframe of the stocks' closing prices.
    """
    # Creates an dictionary for the stocks' expected returns.
    expected_returns = {}
    expected_returns['date'] = []
    for s in stocks:
        expected_returns[s] = []

    # Iterates throught the dataframe and gets the return at each date.
    for i in range(1, len(price_dataframe)):
        previous_date = price_dataframe.iloc[i-1]
        current_date = price_dataframe.iloc[i]
        
        expected_returns['date'].append(current_date.name)

        for s in stocks:
            single_return = (current_date[s, 'adjclose'] - 
                previous_date[s, 'adjclose']) / previous_date[s, 'adjclose']
            expected_returns[s].append(single_return)
    return expected_returns


def get_returns(stocks, timeframe='monthly'):
    """
    Returns a dataframe of returns for given stocks.
    Params:
    stocks: String or list of stocks you want to get it for.
    timeframe: The timeframe you want to get it for. Can do daily, weekly, monthly.
    """
    # Converts a string of stocks to a list.
    if (type(stocks) == str):
        stocks = [stocks]

    # Gets the adjusted closing price for the stocks in question.
    df_init = get_data(stocks, 'adjclose', timeframe=timeframe)

    # Gets the expected returns and makes them into a dataframe.
    expected_returns = derive_returns(stocks, df_init)
    df = pd.DataFrame(data=expected_returns)
    df = df.set_index('date')

    
    return df
