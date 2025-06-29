# File: tests/scenarios/test_placement.py

from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestPlacement(BaseOrderBookTest):
    def test_place_bid_order(self):
        """Tests placing a single bid order on an empty book."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertIsNone(self.order_book.get_best_ask_price())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 10)

    def test_place_ask_order(self):
        """Tests placing a single ask order on an empty book."""
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertIsNone(self.order_book.get_best_bid_price())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 10)

    def test_place_multiple_bid_orders_at_same_price(self):
        """Tests FIFO ordering for multiple bid orders at the same price."""
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, qty, 99)
            )
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 60)

    def test_place_multiple_bid_orders_at_different_price(self):
        """Tests price priority for multiple bid orders at different prices."""
        prices = [99, 98, 100]
        for i, price in enumerate(prices, start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, price)
            )
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        for price in prices:
            self.assertEqual(
                self.order_book.get_quantity_for_price(price, BidAskEnum.BID), 10
            )

    def test_place_multiple_ask_orders_at_same_price(self):
        """Tests FIFO ordering for multiple ask orders at the same price."""
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, qty, 99)
            )
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 60)

    def test_place_multiple_ask_orders_at_different_price(self):
        """Tests price priority for multiple ask orders at different prices."""
        prices = [99, 98, 100]
        for i, price in enumerate(prices, start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, price)
            )
        self.assertEqual(self.order_book.get_best_ask_price(), 98)
        for price in prices:
            self.assertEqual(
                self.order_book.get_quantity_for_price(price, BidAskEnum.ASK), 10
            )

    def test_no_bid_order_execution_while_ask_order_exists(self):
        """Tests that no execution occurs when the bid price is below the ask price."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 10
        )

    def test_no_ask_order_execution_while_bid_order_exists(self):
        """Tests that no execution occurs when the ask price is above the bid price."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 10
        )
