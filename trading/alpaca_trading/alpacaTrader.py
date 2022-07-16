
from alpaca_trade_api.rest import REST
from abc import ABC, abstractmethod
from typing import Dict
from .order_filling import orderFiller


class alpacaTrader(ABC):

    def __init__(self):
        self.api = REST()
        self.order_filler = orderFiller(self.api)

        account = self.api.get_account()
        print(account.status)

    @abstractmethod
    def have_portfolio(self, portfolio_dict: Dict[str, float]) -> bool:
        """Change the state of the portfolio to reflect the given portfolio dict.

        Args:
            portfolio_dict (Dict[str, float]): ticker to equity % dict

        Returns:
            bool: Returns True if all orders were successfuly submitted
            (should probably change this to if portfolio state reflects input.)
        """
        # add a check to make sure this is called during market hours
        pass

    def _add_current_positions(self, portfolio_dict: dict):
        """For current positions that are not listed in the portfolio_dict,
        set their value to 0 as it is assumed they will be closed.

        Args:
            portfolio_dict (dict): _description_
        """
        positions = self.api.list_positions()
        for p in positions:
            ticker = p.symbol
            assert isinstance(ticker, str)
            if ticker not in portfolio_dict:
                portfolio_dict[ticker] = 0

    def get_position_equity(self, ticker: str) -> float:
        """Get the current equity of a ticker. (return 0 if no position)

        Args:
            ticker (str): ticker symbol

        Raises:
            e: an unaccounted for error.

        Returns:
            float: equity if you have a position with the stock, else 0
        """
        try:
            position = self.api.get_position(ticker)
            assert isinstance(position.market_value, str)
            equity = float(position.market_value)
        except Exception as e:
            if str(e) == "position does not exist":
                equity = 0.0
            else:
                raise e
        return equity

    def calculate_desired_position_equity(self, portfolio_pct: float) -> float:
        """Calculate the desired equity as a percent of the account equity.

        Args:
            portfolio_pct (float): (0-1)

        Returns:
            float: desired equity for this position.
        """
        account = self.api.get_account()
        assert isinstance(account.equity, str)
        account_equity = float(account.equity)

        position_equity = portfolio_pct * account_equity
        return position_equity