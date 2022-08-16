
from alpaca_trade_api.rest import REST
from abc import ABC, abstractmethod
from typing import Dict
from .order_filling import orderFiller
import pandas as pd


class alpacaTrader(ABC):

    def __init__(self):
        self.api = REST()
        self.order_filler = orderFiller(self.api)

        account = self.api.get_account()
        print(account.status)

    @abstractmethod
    def have_portfolio(self, portfolio_dict: Dict[str, float]) -> Dict[str, bool]:
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

    def _get_position_equity_df(self, portfolio_dict: Dict[str, float]) -> pd.DataFrame:
        """Get the dataframe that lists the tickers and the equity values for:
        how much is currently held, how much is desired to be held.

        Args:
            portfolio_dict (Dict[str, float]): ticker to equity % dictionary

        Returns:
            pd.DataFrame:
            'ticker': the ticker symbol
            'portfolio_pct': percent of the portfolio the ticker is expected to make.
            'current_position_equity': Current position equity of the ticker. (if any)
            'desired_position_equity': Desired position equity of the ticker (if any)


            checks to make sure proportions total to 1
        """
        df = pd.DataFrame({'ticker': portfolio_dict.keys(),
                           'portfolio_pct': portfolio_dict.values()})

        rounded_total_proportion = round(df['portfolio_pct'].sum(), 5)
        assert rounded_total_proportion == 1, "sum(portfolio percent) != 1"

        df['current_position_equity'] = df['ticker'].apply(
            lambda ticker: self.get_position_equity(ticker))
        df['desired_position_equity'] = df['portfolio_pct'].apply(
            lambda f: self.calculate_desired_position_equity(f))

        df['equity_diff'] = df['desired_position_equity'] - \
            df['current_position_equity']

        # sell, then buy
        df.sort_values('equity_diff', ascending=True, inplace=True)
        return df

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
        account_equity = self.get_account_equity()

        position_equity = portfolio_pct * account_equity
        return position_equity

    def get_portfolio_results_comparison(
            self,
            portfolio_dict: Dict[str, float],
            ticker_results: Dict[str, bool]) -> pd.DataFrame:
        """_summary_

        Args:
            portfolio_dict (Dict[str, float]): _description_
            ticker_results (Dict[str, float]): _description_

        Returns:
            pd.DataFrame: _description_
        """
        data_df = pd.DataFrame(data=[
            {'ticker': ticker,
             'desired_pct': pct,
             'position_filled': ticker_results[ticker]}
            for ticker, pct in portfolio_dict.items()
        ])
        data_df = data_df[data_df['position_filled'] == True]
        data_df['current_pct'] = data_df['ticker'].apply(
            lambda ticker: self.get_position_equity(ticker)) 
        return data_df

    def get_slippage(self, ticker_results: Dict[str, bool]) -> pd.DataFrame:
        data_df = pd.DataFrame(data=[
            {'ticker': ticker,
             'position_filled': filled}
            for ticker, filled in ticker_results.items()
        ])
        data_df = data_df[data_df['position_filled'] == True]
        positions_df = pd.DataFrame(
            data=[p.__dict__['_raw'] for p in self.api.list_positions()]
        )
        merge_df = pd.merge(
            data_df, positions_df,
            left_on='ticker', right_on='symbol'
        )

        assert len(merge_df) == len(merge_df.drop_duplicates('ticker'))
        return merge_df[['ticker', 'cost_basis', 'market_value', 'unrealized_intraday_plpc']]

    def get_account_equity(self) -> float:
        account = self.api.get_account()
        assert isinstance(account.equity, str)
        account_equity = float(account.equity)
        return account_equity
