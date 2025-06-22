# File: tests/base_test.py

import unittest
from datetime import datetime
from src.core_types import Order, OrderTypeEnum, BidAskEnum
from src.order_book import OrderBook


class BaseOrderBookTest(unittest.TestCase):
    """
    A base class for all order book tests, containing common setup
    and helper methods.
    """

    def setUp(self):
        """Ensures a fresh order book for each test."""
        self.order_book = OrderBook()

    def create_order(
        self, order_id, type_enum, side_enum, quantity, price=None, client="ClientA"
    ):
        """Helper to create orders for testing."""
        return Order(
            order_id=order_id,
            timestamp=datetime.now(),
            order_type_enum=type_enum,
            bid_ask_enum=side_enum,
            price=price,
            quantity=quantity,
            client=f"{client}{order_id}",
        )
