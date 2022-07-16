
### trading module

The trading module is for the basic portfolio rebalance functionality, necessary for an automated implementation of the \<redacted\> strategy.
Makes use of the alpaca brokerage and python sdk: https://github.com/alpacahq/alpaca-trade-api-python

`have_portfolio` attempted to make it such that after execution, the portfolio is composed of a set of tickers, in line with the specified proportions,
and only what is listed in the dictionary.

#### Install
Will use poetry, later.
```
pandas
numpy 
alpaca-trade-api
```

#### Usage
Have an alpaca brokerage account and put the `apca_api_key_id` and `apca_api_secret_key` in an `trading/alpaca_credentials.py` file
for the `trading/example.py` file,

#### Future changes
Testing of the implementation for slippage in buying and selling as well as final proportion of the portfolio after rebalancing is called.
