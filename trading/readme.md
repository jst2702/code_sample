
### trading module

The trading module is for the basic portfolio rebalance functionality, necessary for an automated implementation of the TinyTitans strategy.
Makes use of the alpaca brokerage and python sdk: https://github.com/alpacahq/alpaca-trade-api-python

`have_portfolio` attempted to make it such that after execution, the portfolio is composed of a set of tickers, in line with the specified proportions,
and only what is listed in the dictionary.

#### Libraries
```
pandas
numpy 
alpaca-trade-api
python-dotenv
```

#### Usage
Have an alpaca brokerage account and create the `trading/trade.env` file with the fields:
* `APCA_API_KEY_ID`
* `APCA_API_SECRET_KEY`

#### Future changes
Testing of the implementation for slippage in buying and selling as well as final proportion of the portfolio after rebalancing is called.
