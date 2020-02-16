# Efficient Frontier Calculator

This project is all about finding the efficient frontier for stocks. It both scrapes data from Yahoo! Finance and uses it to get the optimal combination of given stocks. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project uses a couple of preexisting Python packages. Since it is not hosted on `pip` yet, you will have to install each of them before using this code.
* `yahoofinancials`
* `pandas`
* `numpy`
* `holoviews` 
* `bokeh`


### Installing

To install: Go to the folder above where you download this in the terminal you use with python (can be a Jupyter Notebook/Lab terminal). Then, type
`pip install -e efficientfrontier`. After that, you should be able to import and use the code. 

## Usage
The walkthrough is contained in `sandbox/stock_calcs.ipynb`. It is also outlined below here. You can get data for the following stocks:
```
stocks = ['GOOGL', 'AAPL', 'PG', 'JPM']
```
To get various data for the stocks, you can use the following function:
```
efficientfrontier.get_data(stocks, ['open', 'close', 'high', 'low', 'adjclose'])
```
This gets the open, close, high, low and adjusted closing prices for the stocks, on a monthly basis. 

Then, to get monthly returns for the stocks, you can use the `get_returns` function.
```
efficientfrontier.get_returns(stocks)
```

You can also get the stocks' expected returns (means) and covariances. 
```
efficientfrontier.get_mean_and_variance(stocks)
```

You can get the Sharpe Weight portfolio by using
```
efficientfrontier.get_sharpe_weights(stocks)
```

Finally, you can get a HoloViews graph for the efficient frontier by using
```
efficientfrontier.efficient_frontier_graph(stocks, use_sharpe_portfolio=True)
```
The `use_sharpe_portfolio` argument adds a point on the efficient frontier graph with the expected return and standard deviation of the Sharpe Weight portfolio.

## Author

* Alex Lettenberger