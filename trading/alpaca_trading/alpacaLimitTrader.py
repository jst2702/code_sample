from typing import Dict, Union
from TinyTitans.src.trading.alpaca_trading.order import Order
from TinyTitans.src.trading.alpaca_trading.alpacaTrader import alpacaTrader, REST
from TinyTitans.src.trading.utils import alpaca_get_last_close
import math


def check_for_close(ticker: str, api: REST):
    try:
        alpaca_get_last_close(ticker, api)
        return True
    except Exception as e:
        print(e, ticker)
        return False


class alpacaLimitTrader(alpacaTrader):

    def have_portfolio(self, portfolio_dict: Dict[str, float]) -> Dict[str, bool]:
        """Change the state of the portfolio to reflect the given portfolio dict.

        Args:
            portfolio_dict (Dict[str, float]): ticker to equity % dictionary

        Returns:
            bool: Returns True if all orders were successfuly submitted and filled
            (should probably change this to if portfolio state reflects input.
            with some leeway)
        """
        self._add_current_positions(portfolio_dict)
        df = self._get_position_equity_df(portfolio_dict)

        assert all(df['ticker'].apply(lambda s: check_for_close(s, self.api)))

        ticker_results = {
            row['ticker']: self._set_position(
                row['ticker'], row['portfolio_pct'])
            for _, row in df.iterrows()
        }
        return ticker_results

    def _set_position(self, ticker: str, portfolio_pct: float) -> bool:
        """Take the position in the account by getting the order and
        attemping to have it filled.

        Args:
            ticker (str): ticker symbol
            portfolio_pct (float): desired portfolio proportion

        Returns:
            bool: True if appropriate order successfully submitted and filled.
        """
        order = self.get_order(ticker, portfolio_pct)
        position_set = True if order is None \
            else self.order_filler.fill_order(order)
        return position_set

    def get_order(self, ticker: str, portfolio_pct: float) -> Union[Order, None]:
        """Get the order object necessary to achieve the corresponding position
        such that <portfolio_pct> of the account is <ticker> shares.

        This can mean either buying or selling of the security.

        Args:
            ticker (str): stock symbol
            portfolio_pct (float): pct of the portfolio this stock equity should be.

        Returns:
            Union[Order, None]: Returns an order if there is a valid order to place.
            None otherwise.
        """

        cur_equity = self.get_position_equity(ticker)
        des_equity = self.calculate_desired_position_equity(portfolio_pct)

        if des_equity < cur_equity:
            order_quantity = math.floor(
                (cur_equity - des_equity)/alpaca_get_last_close(ticker, self.api))
            close_position = des_equity == 0

            order = Order(ticker, 'sell', quantity=order_quantity,
                          close_position=close_position) \
                if order_quantity != 0 or close_position else None
        elif des_equity > cur_equity:
            order_quantity = math.floor(
                (des_equity - cur_equity)/alpaca_get_last_close(ticker, self.api))
            order = Order(ticker, 'buy', quantity=order_quantity) \
                if order_quantity != 0 else None
        else:
            order = None
        return order
