# File: core_types.py

import datetime
from dataclasses import dataclass
from enum import StrEnum, auto


class OrderTypeEnum(StrEnum):
    LIMIT = auto()
    MARKET = auto()
    TRIGGER = auto()


class BidAskEnum(StrEnum):
    BID = auto()
    ASK = auto()


@dataclass
class Order:
    order_id: int
    timestamp: datetime.datetime
    order_type_enum: OrderTypeEnum
    bid_ask_enum: BidAskEnum
    price: float | None
    quantity: float
    client: str
