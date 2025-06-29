from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestPartialMatching(BaseOrderBookTest):
    def test_bigger_quantity_limit_bid_order_partial_execution_while_ask_order_exists(
        self,
    ):
        """Tests a partial match where a larger new limit bid clears a smaller resting ask."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 10)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.get_best_bid_order(), bid)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_smaller_quantity_limit_bid_order_partial_execution_while_ask_order_exists(
        self,
    ):
        """Tests a partial match where a new limit bid is fully filled by a larger resting ask."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 35, 99)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 15)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_order(), ask)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 15)

    def test_bigger_quantity_limit_ask_order_partial_execution_while_bid_order_exists(
        self,
    ):
        """Tests a partial match where a larger new limit ask clears a smaller resting bid."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 99)
        self.order_book.place_order(ask)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 20)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_order(), ask)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 20)

    def test_smaller_quantity_limit_ask_order_partial_execution_while_bid_order_exists(
        self,
    ):
        """Tests a partial match where a new limit ask is fully filled by a larger resting bid."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        self.assertEqual(bid.quantity, 20)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.get_best_bid_order(), bid)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_bigger_quantity_market_bid_order_partial_execution_while_ask_order_exists(
        self,
    ):
        """Tests a partial match where a larger new market bid clears a smaller resting ask."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.MARKET, BidAskEnum.BID, 20)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 10)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_smaller_quantity_market_bid_order_partial_execution_while_ask_order_exists(
        self,
    ):
        """Tests a partial match where a new market bid is fully filled by a larger resting ask."""
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 35, 99)
        self.order_book.place_order(ask)
        bid = self.create_order(2, OrderTypeEnum.MARKET, BidAskEnum.BID, 20)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 15)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_order(), ask)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 15)

    def test_bigger_quantity_market_ask_order_partial_execution_while_bid_order_exists(
        self,
    ):
        """Tests a partial match where a larger new market ask clears a smaller resting bid."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.MARKET, BidAskEnum.ASK, 30)
        self.order_book.place_order(ask)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 20)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

    def test_smaller_quantity_market_ask_order_partial_execution_while_bid_order_exists(
        self,
    ):
        """Tests a partial match where a new market ask is fully filled by a larger resting bid."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 99)
        self.order_book.place_order(bid)
        ask = self.create_order(2, OrderTypeEnum.MARKET, BidAskEnum.ASK, 10)
        self.order_book.place_order(ask)
        self.assertEqual(bid.quantity, 20)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.get_best_bid_order(), bid)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)
