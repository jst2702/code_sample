from alpaca_trade_api.rest import REST
from alpaca_trade_api.entity import Order as orderEntity
from TinyTitans.src.trading.alpaca_trading.order import Order
from TinyTitans.src.trading.utils import alpaca_get_last_close
import time


def get_limit(ticker: str, side: str, api: REST) -> float:
    """Get the limit price for a buy or sell limit order

    Args:
        ticker (str): ticker symbol

    Returns:
        float: limit price
    """
    # modify to get the bid instead, perhaps.
    last = alpaca_get_last_close(ticker, api)
    scaler = 0.015
    delta = (last*scaler) if side == 'buy' else -(last*scaler)
    limit = round(last + delta, 2)
    return limit


class orderFiller:

    def __init__(self, api: REST):
        self.api = api

    def fill_order(self, order: Order) -> bool:
        """ Fill base order object

        Args:
            order (Order): Order object

        Raises:
            Exception: If order has neither equity or quantity.

        Returns:
            bool: True if order is filled.
        """
        if order.equity is not None:
            order_result = self.fill_market_order(order)
        elif order.quantity is not None:
            order_result = self.fill_limit_order(order)
        else:
            raise Exception("invalid order type: {order}")
        return order_result

    def fill_market_order(self, order: Order) -> bool:
        """Fill a market base order using notional market orders from alpaca.
        Assumes that any market order will be filled if able, and does
        not attempt to fill order after initial submission.

        Args:
            order (Order): Order object

        Returns:
            bool: True if order is filled.
        """
        if order.close_position == True:
            self.api.close_position(order.ticker)
            return True
        else:
            # Using notional market orders
            assert order.equity is not None
            order_entity = self.api.submit_order(
                symbol=order.ticker,
                notional=order.equity,
                side=order.side,
                type='market',
                time_in_force='day'
            )
            time.sleep(8)
            order_entity = self.api.get_order(order_entity.id)  # type: ignore
            assert order_entity is not None
            return order_entity.status == "filled"

    def fill_limit_order(self, order: Order) -> bool:
        """Fill a limit base order using limit quantity orders from alpaca.
        Assumes it's possible a limit order might not be filled, and attempts
        to fill the order if initially unsuccessful.


        Args:
            order (Order): Order object

        Returns:
            bool: True if order is filled.
        """
        assert order.quantity is not None
        print(f"initial order received: {order}")
        order_entity = self.api.submit_order(
            symbol=order.ticker,
            time_in_force='day',
            side=order.side,
            type='limit',
            limit_price=str(get_limit(order.ticker, order.side, self.api)),
            qty=order.quantity
        )
        time.sleep(10)
        order_entity = self.api.get_order(order_entity.id)  # type: ignore
        assert order_entity is not None
        if order_entity.status != 'filled':
            return self.attempt_to_fill_limit_order(order_entity)
        else:
            return True

    def attempt_to_fill_limit_order(self, order_entity: orderEntity,
                                    max_limit_scaler: float = 0.04,
                                    increase_increment: float = 0.005,
                                    jitter: float = 10,
                                    cancel_on_fail: bool = True) -> bool:
        """For a given limit order, attempt to adjust the limit price incrementally
        so as to hopefully fill the order, replacing as necessary, until the order fills
        or the limit threshold is met.

        Args:
            order_entity (orderEntity): _description_
            max_limit_scaler (float, optional): max increase to the limit price 
            while attempting to fill, before giving up. Defaults to 0.04.
            increase_increment (float, optional): proportion by which to 
            incrementally increase the limit. Defaults to 0.005.
            jitter (float, optional): Time to wait for the order to fill 
            before adjusting limit price.. Defaults to 10.
            cancel_on_fail (bool, optional): Cancel order if unsuccessful in filling. Defaults to True.

        Raises:
            e: if an exception occurs while attempting to replace orders.

        Returns:
            bool: True if order is successfully filled following the attempt.
        """
        print(f"attempting to fill order: {order_entity}")
        # assumed input is the initial order for the desired position
        print(f"desired quantity: {order_entity.qty}")

        order_entity = self.api.get_order(order_entity.id)  # type: ignore
        if order_entity.status != 'filled':
            print(
                f"desired qty < current_qty: {order_entity.qty}, {order_entity.filled_qty}")

            attempting_to_fill = True
            is_filled = False
            current_scaler = 0

            while attempting_to_fill:
                current_scaler += increase_increment
                new_limit_price = self._get_new_limit_price(
                    order_entity, current_scaler)

                if new_limit_price == order_entity.limit_price:
                    # continue if increase resulted in no change to limit.
                    continue

                try:
                    order_entity = self.api.replace_order(
                        order_id=order_entity.id,  # type: ignore
                        limit_price=new_limit_price
                    )
                except Exception as e:
                    if 'order is not open' in str(e):
                        is_filled = True
                        break
                    else:
                        raise e

                print(f"new order: {order_entity}")
                time.sleep(jitter)

                print(f"filled qty: {order_entity.filled_qty}")
                is_filled = order_entity.status == 'filled'

                print(f" is filled: {is_filled}")
                attempting_to_fill = not is_filled and current_scaler <= max_limit_scaler

            if cancel_on_fail and not is_filled:
                self.api.cancel_order(order_entity.id)  # type: ignore

            return is_filled
        else:
            return True

    @staticmethod
    def _get_new_limit_price(order_entity: orderEntity, current_scaler: float) -> str:
        """Get an adjusted limit price for an order entity, increased or decreased depending
        on the order side.

        Args:
            order_entity (orderEntity): limit order entity
            current_scaler (float): current scaler for an increase or decrease.

        Returns:
            str: a string of the new limit price
        """
        limit_price = float(order_entity.limit_price)
        
        delta = (
            limit_price * current_scaler  # type: ignore
            if order_entity.side == 'buy'
            else - limit_price * current_scaler  # type: ignore
        )

        new_limit_price = str(round(limit_price + delta, 2))  # type: ignore
        return new_limit_price
