import unittest
from datetime import datetime

from order_book import Order, OrderBook, OrderTypeEnum, BidAskEnum


class TestOrderBook(unittest.TestCase):

    def setUp(self):
        self.order_book = OrderBook()

    def test_place_bid_order(self):
        bid_order = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=10,
            client="ClientA",
        )
        self.order_book.place_order(bid_order)

        self.assertEqual(self.order_book.best_bid_price, 99)
        self.assertEqual(self.order_book.best_ask_price, 0)

    def test_place_ask_order(self):
        ask_order = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientB",
        )
        self.order_book.place_order(ask_order)

        self.assertEqual(self.order_book.best_ask_price, 99)
        self.assertEqual(self.order_book.best_bid_price, 0)

    def test_place_multiple_bid_orders_at_same_price(self):
        bid_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=10,
            client="ClientA",
        )
        bid_order_2 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=30,
            client="ClientA",
        )
        bid_order_3 = Order(
            order_id=3,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=20,
            client="ClientA",
        )

        self.order_book.place_order(bid_order_1)
        self.order_book.place_order(bid_order_2)
        self.order_book.place_order(bid_order_3)

        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 10)

    def test_place_multiple_bid_orders_at_different_price(self):
        bid_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=10,
            client="ClientA",
        )
        bid_order_2 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=98.0,
            quantity=10,
            client="ClientA",
        )
        bid_order_3 = Order(
            order_id=3,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=100.0,
            quantity=10,
            client="ClientA",
        )

        self.order_book.place_order(bid_order_1)
        self.order_book.place_order(bid_order_2)
        self.order_book.place_order(bid_order_3)

        self.assertEqual(self.order_book.best_bid_price, 100.0)

    def test_place_multiple_ask_orders_at_same_price(self):
        ask_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientA",
        )
        ask_order_2 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=30,
            client="ClientA",
        )
        ask_order_3 = Order(
            order_id=3,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=20,
            client="ClientA",
        )

        self.order_book.place_order(ask_order_1)
        self.order_book.place_order(ask_order_2)
        self.order_book.place_order(ask_order_3)

        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_place_multiple_ask_orders_at_different_price(self):
        ask_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientA",
        )
        ask_order_2 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=98.0,
            quantity=10,
            client="ClientA",
        )
        ask_order_3 = Order(
            order_id=3,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=100.0,
            quantity=10,
            client="ClientA",
        )

        self.order_book.place_order(ask_order_1)
        self.order_book.place_order(ask_order_2)
        self.order_book.place_order(ask_order_3)

        self.assertEqual(self.order_book.best_ask_price, 98.0)

    def test_no_bid_order_execution_while_ask_order_exists(self):
        ask_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=101.0,
            quantity=10,
            client="ClientA",
        )
        bid_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=20,
            client="ClientA",
        )

        self.order_book.place_order(ask_order_1)
        self.order_book.place_order(bid_order_1)

        self.assertEqual(self.order_book.best_bid_price, 99.0)
        self.assertEqual(self.order_book.best_ask_price, 101.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_no_ask_order_execution_while_bid_order_exists(self):
        bid_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=20,
            client="ClientA",
        )

        ask_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=101.0,
            quantity=10,
            client="ClientA",
        )

        self.order_book.place_order(bid_order_1)
        self.order_book.place_order(ask_order_1)

        self.assertEqual(self.order_book.best_bid_price, 99.0)
        self.assertEqual(self.order_book.best_ask_price, 101.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_bid_order_execution_complete_clearance_while_ask_order_exists(self):
        ask_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        bid_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        self.order_book.place_order(ask_order_1)
        self.order_book.place_order(bid_order_1)

        self.assertEqual(self.order_book.best_bid_price, 0.0)
        self.assertEqual(self.order_book.best_ask_price, 0.0)

        self.assertEqual(bid_order_1.quantity, 0.0)
        self.assertEqual(ask_order_1.quantity, 0.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order(), None)
        self.assertEqual(self.order_book.ask_orders.get_best_order(), None)

    def test_ask_order_execution_complete_clearance_while_bid_order_exists(self):
        bid_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        ask_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        self.order_book.place_order(bid_order_1)
        self.order_book.place_order(ask_order_1)

        self.assertEqual(self.order_book.best_bid_price, 0.0)
        self.assertEqual(self.order_book.best_ask_price, 0.0)

        self.assertEqual(bid_order_1.quantity, 0.0)
        self.assertEqual(ask_order_1.quantity, 0.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order(), None)
        self.assertEqual(self.order_book.ask_orders.get_best_order(), None)

    def test_bigger_quantity_bid_order_partial_execution_while_ask_order_exists(self):
        ask_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        bid_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=20,
            client="ClientA",
        )

        self.order_book.place_order(ask_order_1)
        self.order_book.place_order(bid_order_1)

        self.assertEqual(self.order_book.best_bid_price, 99.0)
        self.assertEqual(self.order_book.best_ask_price, 0.0)

        self.assertEqual(bid_order_1.quantity, 10.0)
        self.assertEqual(ask_order_1.quantity, 0.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order(), bid_order_1)
        self.assertEqual(self.order_book.ask_orders.get_best_order(), None)

    def test_smaller_quantity_bid_order_partial_execution_while_ask_order_exists(self):
        ask_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=35,
            client="ClientA",
        )

        bid_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=20,
            client="ClientA",
        )

        self.order_book.place_order(ask_order_1)
        self.order_book.place_order(bid_order_1)

        self.assertEqual(self.order_book.best_bid_price, 0.0)
        self.assertEqual(self.order_book.best_ask_price, 99.0)

        self.assertEqual(bid_order_1.quantity, 0.0)
        self.assertEqual(ask_order_1.quantity, 15.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order(), None)
        self.assertEqual(self.order_book.ask_orders.get_best_order(), ask_order_1)

    def test_bigger_quantity_ask_order_partial_execution_while_bid_order_exists(self):
        bid_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        ask_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=30,
            client="ClientA",
        )

        self.order_book.place_order(bid_order_1)
        self.order_book.place_order(ask_order_1)

        self.assertEqual(self.order_book.best_bid_price, 0.0)
        self.assertEqual(self.order_book.best_ask_price, 99.0)

        self.assertEqual(bid_order_1.quantity, 0.0)
        self.assertEqual(ask_order_1.quantity, 20.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order(), None)
        self.assertEqual(self.order_book.ask_orders.get_best_order(), ask_order_1)

    def test_smaller_quantity_ask_order_partial_execution_while_bid_order_exists(self):
        bid_order_1 = Order(
            order_id=1,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.BID,
            price=100.0,
            quantity=30,
            client="ClientA",
        )

        ask_order_1 = Order(
            order_id=2,
            timestamp=datetime.now(),
            order_type_enum=OrderTypeEnum.LIMIT,
            bid_ask_enum=BidAskEnum.ASK,
            price=99.0,
            quantity=10,
            client="ClientA",
        )

        self.order_book.place_order(bid_order_1)
        self.order_book.place_order(ask_order_1)

        self.assertEqual(self.order_book.best_bid_price, 100.0)
        self.assertEqual(self.order_book.best_ask_price, 0.0)

        self.assertEqual(bid_order_1.quantity, 20.0)
        self.assertEqual(ask_order_1.quantity, 0.0)

        self.assertEqual(self.order_book.bid_orders.get_best_order(), bid_order_1)
        self.assertEqual(self.order_book.ask_orders.get_best_order(), None)


if __name__ == "__main__":
    unittest.main(verbosity=1)
