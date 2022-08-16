from typing import Dict, List, Union
import pandas as pd
from .order import Order
from .alpacaTrader import alpacaTrader


class alpacaMarketTrader(alpacaTrader):

    def have_portfolio(self, portfolio_dict: Dict[str, float]) -> Dict[str, bool]:
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
        ticker_results = {
            ticker: result for ticker, result 
            in zip(df['ticker'], order_results)
        }
        return ticker_results

    def _determine_orders(self, df: pd.DataFrame) -> List[Union[Order, None]]:
        """For a given DataFrame, get a list of notional market orders 
        to be submitted so that afterwards, the portfolio is in the desired state.

        Args:
            df (pd.DataFrame): position equity df

        Returns:
            List[order]: List of independently executed orders to be submitted.
        """
        orders = [
            self.get_order(
                row['ticker'],
                row['current_position_equity'],
                row['desired_position_equity']
            )
            for _, row in df.iterrows()
        ]
        return orders

    def get_order(self, ticker, cur_equity: float, des_equity: float) -> Union[Order, None]:
        """Get the order object necessary to achieve the corresponding position
        such that <portfolio_pct> of the account is <ticker> shares.

        This can mean either buying or selling of the security.

        Args:
            ticker (_type_): _description_
            cur_equity (float): _description_
            des_equity (float): _description_

        Returns:
            Union[Order, None]: Returns an order if there is a valid order to place.
            None otherwise.
        """
        if des_equity < cur_equity:
            order_equity = float(cur_equity - des_equity)
            close_position = des_equity == 0
            order = Order(ticker, 'sell', equity=order_equity, close_position=close_position)
        elif des_equity > cur_equity:
            order_equity = float(des_equity - cur_equity)
            order = Order(ticker, 'buy', equity=order_equity)
        else:
            order = None
        return order

    def _submit_orders(self, orders: List[Union[Order, None]]) -> List[bool]:
        """Submit a list of orders using an input list of order objects.
        (closes position if so dictated)

        Args:
            orders (List[order]): list of order objects that indicate
            whether to buy/sell a stock and how much (only used notional orders)

        Returns:
            List[bool]: returns true if the order was accepted
        """
        order_results = [
            self.order_filler.fill_order(order) if order is not None else True
            for order in orders
        ]
        return order_results
