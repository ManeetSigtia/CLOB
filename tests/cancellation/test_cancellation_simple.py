from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestSimpleCancellation(BaseOrderBookTest):
    def test_cancel_single_bid_order(self):
        """Tests cancelling the only bid order on the book."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 999)
        self.order_book.place_order(bid)
        self.order_book.cancel_order(1)
        self.order_book.place_order(ask)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 0)

    def test_cancel_single_ask_order(self):
        """Tests cancelling the only ask order on the book."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 1)
        self.order_book.place_order(ask)
        self.order_book.cancel_order(1)
        self.order_book.place_order(bid)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 0)

    def test_cancel_best_of_two_bids(self):
        """Tests cancelling the best bid order when two are present."""
        bid_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 999)
        self.order_book.place_order(bid_worse)
        self.order_book.place_order(bid_best)
        self.order_book.cancel_order(2)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 10)

    def test_cancel_best_of_two_asks(self):
        """Tests cancelling the best ask order when two are present."""
        ask_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 100)
        bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 1)
        self.order_book.place_order(ask_worse)
        self.order_book.place_order(ask_best)
        self.order_book.cancel_order(2)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 0)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 10
        )

    def test_cancel_worse_of_two_bids(self):
        """Tests cancelling a non-best bid order."""
        bid_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 999)
        self.order_book.place_order(bid_worse)
        self.order_book.place_order(bid_best)
        self.order_book.cancel_order(1)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 15
        )
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)

    def test_cancel_worse_of_two_asks(self):
        """Tests cancelling a non-best ask order."""
        ask_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 100)
        bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 1)
        self.order_book.place_order(ask_worse)
        self.order_book.place_order(ask_best)
        self.order_book.cancel_order(1)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 15
        )
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
