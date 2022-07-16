# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 09:09:55 2022

@author: 15409
"""
from alpaca_trading import alpacaLimitTrader
import os
from TinyTitans.src.trading.alpaca_credentials import apca_api_key_id, apca_api_secret_key

os.environ["APCA_API_KEY_ID"] = apca_api_key_id
os.environ["APCA_API_SECRET_KEY"] = apca_api_secret_key

limit_trader = alpacaLimitTrader()

portfolio_dict = {'NGL': 0.1, 'VTGN': 0.1, 'GEVO': 0.1,
                  'BOLT': 0.2, 'OST': 0.2, 'ARAY': 0.2, 'LFMD': 0.1}

limit_trader.have_portfolio(portfolio_dict)
