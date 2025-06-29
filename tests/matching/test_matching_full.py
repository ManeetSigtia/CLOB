from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestFullMatching(BaseOrderBookTest):
    def test_limit_bid_order_execution_complete_clearance_while_ask_order_exists(self):
        """Tests a full match where a new limit bid clears a resting ask of the same size."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_limit_ask_order_execution_complete_clearance_while_bid_order_exists(self):
        """Tests a full match where a new limit ask clears a resting bid of the same size."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_market_bid_order_execution_complete_clearance_while_ask_order_exists(self):
        """Tests a full match where a new market bid clears a resting ask of the same size."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.MARKET, BidAskEnum.BID, 10)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_market_ask_order_execution_complete_clearance_while_bid_order_exists(self):
        """Tests a full match where a new market ask clears a resting bid of the same size."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.MARKET, BidAskEnum.ASK, 10)
        self.order_book.place_order(ask)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)
