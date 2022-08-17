# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 09:09:55 2022

@author: 15409
"""
from alpaca_trading import alpacaLimitTrader
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='trade.env')

limit_trader = alpacaLimitTrader()

portfolio_dict = {
  'NGL': 0.1, 
  'VTGN': 0.1, 
  'GEVO': 0.1,
  'BOLT': 0.2, 
  'OST': 0.2, 
  'ARAY': 0.2, 
  'LFMD': 0.1
}

limit_trader.have_portfolio(portfolio_dict)
