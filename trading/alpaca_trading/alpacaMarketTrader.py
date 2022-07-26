from typing import Dict, List
import pandas as pd
from .order import Order
from .alpacaTrader import alpacaTrader


class alpacaMarketTrader(alpacaTrader):

    def have_portfolio(self, portfolio_dict: Dict[str, float]) -> bool:
        """Change the state of the portfolio to reflect the given portfolio dict.

        Args:
            portfolio_dict (Dict[str, float]): ticker to equity % dictionary

        Returns:
            bool: Returns True if all appropriate positions were taken.
        """
        self._add_current_positions(portfolio_dict)
        df = self._get_position_equity_df(portfolio_dict)
        orders = self._determine_orders(df)
        order_results = self._submit_orders(orders)
        return all(order_results)

    def _determine_orders(self, df: pd.DataFrame) -> List[Order]:
        """For a given DataFrame, get a list of notional market orders 
        to be submitted so that afterwards, the portfolio is in the desired state.

        Args:
            df (pd.DataFrame): position equity df

        Returns:
            List[order]: List of independently executed orders to be submitted.
        """
        orders = []
        for _, row in df.iterrows():

            ticker = row['ticker']
            cur_equity = row['current_position_equity']
            des_equity = row['desired_position_equity']

            if des_equity < cur_equity:
                order_equity = float(cur_equity - des_equity)
                close_position = des_equity == 0
                orders.append(
                    Order(ticker, 'sell', equity=order_equity, close_position=close_position))

            elif des_equity > cur_equity:
                order_equity = float(des_equity - cur_equity)
                orders.append(
                    Order(ticker, 'buy', equity=order_equity))

        return orders

    def _submit_orders(self, orders: List[Order]) -> List[bool]:
        """Submit a list of orders using an input list of order objects.
        (closes position if so dictated)

        Args:
            orders (List[order]): list of order objects that indicate
            whether to buy/sell a stock and how much (only used notional orders)

        Returns:
            List[bool]: returns true if the order was accepted
        """
        order_results = [
            self.order_filler.fill_order(order)
            for order in orders
        ]
        return order_results
