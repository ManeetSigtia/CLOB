import unittest
from datetime import datetime
from order_book import Order, OrderBook, OrderTypeEnum, BidAskEnum


class TestOrderBook(unittest.TestCase):

    def setUp(self):
        self.order_book = OrderBook()

    def create_order(
        self, order_id, type_enum, side_enum, price, quantity, client="ClientA"
    ):
        return Order(
            order_id=order_id,
            timestamp=datetime.now(),
            order_type_enum=type_enum,
            bid_ask_enum=side_enum,
            price=price,
            quantity=quantity,
            client=client,
        )

    def create_order(
        self, order_id, type_enum, side_enum, quantity, price=None, client="ClientA"
    ):
        return Order(
            order_id=order_id,
            timestamp=datetime.now(),
            order_type_enum=type_enum,
            bid_ask_enum=side_enum,
            price=price,
            quantity=quantity,
            client=client,
        )

    def test_place_bid_order(self):
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 0)

    def test_place_ask_order(self):
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)

    def test_place_multiple_bid_orders_at_same_price(self):
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, qty, 99)
            )
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 10)

    def test_place_multiple_bid_orders_at_different_price(self):
        prices = [99, 98, 100]
        for i, price in enumerate(prices, start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, price)
            )
        self.assertEqual(self.order_book.get_best_bid_price(), 100)

    def test_place_multiple_ask_orders_at_same_price(self):
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, qty, 99)
            )
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_place_multiple_ask_orders_at_different_price(self):
        prices = [99, 98, 100]
        for i, price in enumerate(prices, start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, price)
            )
        self.assertEqual(self.order_book.get_best_ask_price(), 98)

    def test_no_bid_order_execution_while_ask_order_exists(self):
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(ask)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_no_ask_order_execution_while_bid_order_exists(self):
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        self.order_book.place_order(bid)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_bid_order_execution_complete_clearance_while_ask_order_exists(self):
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(ask)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)
        self.assertEqual(self.order_book.get_best_ask_price(), 0)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.bid_orders.get_best_order())
        self.assertIsNone(self.order_book.ask_orders.get_best_order())

    def test_ask_order_execution_complete_clearance_while_bid_order_exists(self):
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(bid)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)
        self.assertEqual(self.order_book.get_best_ask_price(), 0)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.bid_orders.get_best_order())
        self.assertIsNone(self.order_book.ask_orders.get_best_order())

    def test_bigger_quantity_bid_order_partial_execution_while_ask_order_exists(self):
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(ask)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 0)
        self.assertEqual(bid.quantity, 10)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.bid_orders.get_best_order(), bid)
        self.assertIsNone(self.order_book.ask_orders.get_best_order())

    def test_smaller_quantity_bid_order_partial_execution_while_ask_order_exists(self):
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 35, 99)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(ask)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 15)
        self.assertIsNone(self.order_book.bid_orders.get_best_order())
        self.assertEqual(self.order_book.ask_orders.get_best_order(), ask)

    def test_bigger_quantity_ask_order_partial_execution_while_bid_order_exists(self):
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 99)
        self.order_book.place_order(bid)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 20)
        self.assertIsNone(self.order_book.bid_orders.get_best_order())
        self.assertEqual(self.order_book.ask_orders.get_best_order(), ask)

    def test_smaller_quantity_ask_order_partial_execution_while_bid_order_exists(self):
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 99)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(bid)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 0)
        self.assertEqual(bid.quantity, 20)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.bid_orders.get_best_order(), bid)
        self.assertIsNone(self.order_book.ask_orders.get_best_order())


if __name__ == "__main__":
    unittest.main()
