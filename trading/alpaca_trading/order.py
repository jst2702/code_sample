from typing import Union
from dataclasses import dataclass


@dataclass
class Order:
    """Base order to store basic order information. 
    Equity for market orders, quantity for limit orders.
    """
    ticker: str
    side: str
    equity: Union[float, None] = None
    quantity: Union[float, None] = None
    close_position: bool = False

    def __post_init__(self):
        print(self)
        assert self.equity is not None or self.quantity is not None
