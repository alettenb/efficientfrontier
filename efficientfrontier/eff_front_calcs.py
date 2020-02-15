"""Actually does all the efficient frontier calculations""" 
import numpy as np
import pandas as pd
import holoviews as hv
hv.extension('bokeh')
from .scrape_data import get_returns

def get_sharpe_weights(stocks):
    """
    Gets the (slightly inoptimal) sharpe weights (normalized). 
    Uses the utility function mu - 2 a w^t V(stocks) w.
    Params:
    stocks: A list of stocks you want to calculate this for.
    """

    mu, sig = get_mean_and_variance(stocks)

    w = np.matmul(np.linalg.inv(sig), mu)
    w_t = np.transpose(w / np.sum(w))[0]
    return pd.DataFrame(data={'stock': stocks, 'weight': w_t})

def get_mean_and_variance(stocks):
    """
    Gets the expected returns (monthly) and covariance matrix for stocks
    Params:
    stocks: A list of stocks
    """
    price_df = get_returns(stocks)

    sig = np.cov(np.transpose(price_df))

    mu = np.array([np.mean(price_df).values])
    mu = np.transpose(mu)

    return mu, sig    

def efficient_frontier_fn(mu, sigma):
    """
    Gets the function for efficient frontier; from the return to the standard
    deviation.
    Params:
    mu: The expected return vector.
    sigma: The covariance matrix for the stocks.
    """

    inv_sig = np.linalg.inv(sigma)

    ones = np.ones(mu.shape)

    a = np.matmul(np.matmul(np.transpose(mu), inv_sig), mu)
    b = np.matmul(np.matmul(np.transpose(ones), inv_sig), mu)
    c = np.matmul(np.matmul(np.transpose(ones), inv_sig), ones)

    return lambda rets : np.sqrt((a - 2 * b * rets + c * rets**2) / 
        (a * c - b**2))


def plot_efficient_frontier_curve(stdevs, rets, width, height):
    """
    Plots the curve for an efficient frontier.

    Params:
    stdevs: Array of standard deviations.
    rets: Array of returns.
    width: width of plot.
    height: Height of plot.
    """

    df_std = pd.DataFrame(data = {
        'Standard Deviation (%/month)': np.array(stdevs), 
        'Expected Monthly Return (%/month)': np.array(rets)
    })
    c = hv.Curve(df_std, label='Efficient Frontier').opts(
        title="Efficient Frontier",
        width=width,
        height=height,
    )

    return c

def plot_stock_data(mu, sig, stocks):
    """
    Returns a plot of stocks' expected returns and standard deviation.

    params:
    mu: A list of expected returns for the stocks.
    sig: A covariance matrix for the stocks.
    stocks: A list of the stocks in question.
    """
    # Gets data for all the stocks.
    stock_info = [[], [], []]
    for i, stock in enumerate(stocks):
        stock_info[1].append(mu[i, 0])
        stock_info[0].append(np.sqrt(sig[i, i]))
        stock_info[2].append(stock)

    # Converts stock_info to a dataframe.
    df_stocks = pd.DataFrame(data={
        'stock': stock_info[2],
        'return': stock_info[1],
        'std': stock_info[0],
    })
    
    # plots the expected returns and standard deviations.
    stock_data_points = hv.Points(
        data=df_stocks,
        kdims=['std', 'return'],
        label='Stocks'
    ).opts(
        tools=['hover'],
        color='orange',
        size=5,
    )

    return stock_data_points

def plot_sharpe_weight_portfolio(stocks, mu, sig):
    """
    Gets and plots the sharpe weight portfolio returns and variance for given 
    stocks.

    Params:
    stocks: A list of stocks to look at
    mu: A list of expected returns for the stocks.
    sig: A covariance matrix for the stocks.
    """

    # Gets the sharpe weights for the stocks along with the return/variance 
    # of the Sharpe Weight Portfolio.
    weights_dataframe = get_sharpe_weights(stocks)
    w = weights_dataframe['weight'].values
    w = np.transpose(np.array([w]))
    ret = np.matmul(np.transpose(mu), w)[0, 0]
    var = np.matmul(np.transpose(w), sig)
    var = np.matmul(var, w)[0, 0]
    
    # Lists out the weights so we can hover over it on the graph.
    weights = ''
    for row, vals in weights_dataframe.iterrows():
        weights += vals.stock + ": " + str(round(vals.weight, 3)) + "\n"
    
    # Plots the sharpe weight portfolio.
    wplot = hv.Points(
        data=pd.DataFrame({
            'Return': [ret],
            'Std': [np.sqrt(var)],
            'Weights': weights,
        }),
        kdims=['Std', 'Return'],
        label='Sharpe Ratio Portfolio',
    ).opts(
        tools=['hover'],
        color='red',
        size=5,
    )

    return wplot

def efficient_frontier_graph(
    stocks, 
    width=600, 
    height=500, 
    use_sharpe_portfolio = False
):
    """
    Plots the efficient frontier for the given stocks.
    Params:
    stocks: A list of stocks you ar calculating the efficient frontier for.
    use_sharpe_portfolio: If True, includes a point for the sharpe portfolio.
    """

    # Gets the return, variance, and standard deviation from stocks.
    mu, sig = get_mean_and_variance(stocks)
    stdev_fn = efficient_frontier_fn(mu, sig)
    rets = [min(mu - .001)[0]]
    stdevs = [stdev_fn(rets[0])[0][0]]

    # Gets the maximum standard deviation of the stocks
    max_stdev = 0
    for i in range(len(sig)):
        if (np.sqrt(sig[i, i]) > max_stdev):
            max_stdev = np.sqrt(sig[i, i])

    # Gets the standard deviation value as a function of returns.
    while (stdevs[-1] < max_stdev + .01):
        ret = rets[-1] + .0001
        rets.append(ret)

        stdevs.append(stdev_fn(ret)[0][0])
    
    # Plots the efficient frontier curve.    
    efficient_frontier_curve = plot_efficient_frontier_curve(
        stdevs, 
        rets, 
        width, 
        height
    )
    
    # Plots the stocks' expected returns and standard deviations.
    stock_data_points = plot_stock_data(mu, sig, stocks)
    
    # Combines the above graphs. 
    fin = efficient_frontier_curve * stock_data_points

    if (use_sharpe_portfolio):
        sharpe_weight_plot = plot_sharpe_weight_portfolio(stocks, mu, sig)
        
        fin = efficient_frontier_curve * stock_data_points * sharpe_weight_plot
        
    return fin