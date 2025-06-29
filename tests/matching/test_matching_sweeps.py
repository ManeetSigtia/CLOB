from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestSweepMatching(BaseOrderBookTest):
    def test_partial_execution_across_multiple_ask_orders_with_limit_bid(self):
        """Tests a limit bid executing against multiple resting asks at different prices."""
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 102)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 101)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 25, 102)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.ask_orders.get_best_order()
        self.assertIsNotNone(remaining_ask)
        self.assertEqual(remaining_ask.price, 102)
        self.assertEqual(remaining_ask.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 5)

    def test_partial_execution_across_multiple_bid_orders_with_limit_ask(self):
        """Tests a limit ask executing against multiple resting bids at different prices."""
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 101)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 25, 101)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        remaining_bid = self.order_book.bid_orders.get_best_order()
        self.assertIsNotNone(remaining_bid)
        self.assertEqual(remaining_bid.price, 101)
        self.assertEqual(remaining_bid.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 5)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)

    def test_limit_bid_clears_one_level_and_partially_fills_next(self):
        """
        Tests that a large limit bid clears the best ask level completely, then
        partially fills the next level, respecting price and time priority.
        """
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101)
        ask3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)
        bid = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 40, 102)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask1.quantity, 0)
        self.assertEqual(ask2.quantity, 0)
        self.assertEqual(ask3.quantity, 5)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.get_best_ask_order()
        self.assertEqual(remaining_ask.order_id, ask3.order_id)
        self.assertEqual(remaining_ask.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 5)

    def test_limit_ask_clears_one_level_and_partially_fills_next(self):
        """
        Symmetrical test: A large limit ask clears the best bid level completely,
        then partially fills the next level.
        """
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 102)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 101)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)
        ask = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 40, 101)
        self.order_book.place_order(ask)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(bid1.quantity, 0)
        self.assertEqual(bid2.quantity, 0)
        self.assertEqual(bid3.quantity, 5)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        remaining_bid = self.order_book.get_best_bid_order()
        self.assertEqual(remaining_bid.order_id, bid3.order_id)
        self.assertEqual(remaining_bid.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 0)

    def test_large_limit_bid_clears_all_asks_and_becomes_new_best_bid(self):
        """
        Tests that a massive limit bid clears the entire ask side of the book
        and its remainder is correctly placed as the new best bid.
        """
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        ask3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 103)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)
        bid = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 100, 103)
        self.order_book.place_order(bid)
        self.assertEqual(ask1.quantity, 0)
        self.assertEqual(ask2.quantity, 0)
        self.assertEqual(ask3.quantity, 0)
        self.assertEqual(bid.quantity, 40)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 103)
        remaining_bid = self.order_book.get_best_bid_order()
        self.assertEqual(remaining_bid.quantity, 40)
        self.assertEqual(remaining_bid.order_id, bid.order_id)
        self.assertEqual(
            self.order_book.get_quantity_for_price(103, BidAskEnum.BID), 40
        )
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(103, BidAskEnum.ASK), 0)

    def test_large_limit_ask_clears_all_bids_and_becomes_new_best_ask(self):
        """
        Symmetrical test: A massive limit ask clears the entire bid side
        and its remainder becomes the new best ask.
        """
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 98)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 97)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)
        ask = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 100, 97)
        self.order_book.place_order(ask)
        self.assertEqual(bid1.quantity, 0)
        self.assertEqual(bid2.quantity, 0)
        self.assertEqual(bid3.quantity, 0)
        self.assertEqual(ask.quantity, 40)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 97)
        remaining_ask = self.order_book.get_best_ask_order()
        self.assertEqual(remaining_ask.quantity, 40)
        self.assertEqual(remaining_ask.order_id, ask.order_id)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(98, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(97, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(97, BidAskEnum.ASK), 40)

    def test_partial_execution_across_multiple_ask_orders_with_market_bid(self):
        """Tests a market bid executing against multiple resting asks at different prices."""
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 102)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 101)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        bid = self.create_order(3, OrderTypeEnum.MARKET, BidAskEnum.BID, 25)
        self.order_book.place_order(bid)
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.ask_orders.get_best_order()
        self.assertIsNotNone(remaining_ask)
        self.assertEqual(remaining_ask.price, 102)
        self.assertEqual(remaining_ask.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 5)

    def test_partial_execution_across_multiple_bid_orders_with_market_ask(self):
        """Tests a market ask executing against multiple resting bids at different prices."""
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 101)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        ask = self.create_order(3, OrderTypeEnum.MARKET, BidAskEnum.ASK, 25)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        remaining_bid = self.order_book.bid_orders.get_best_order()
        self.assertIsNotNone(remaining_bid)
        self.assertEqual(remaining_bid.price, 101)
        self.assertEqual(remaining_bid.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 5)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)

    def test_market_bid_clears_one_level_and_partially_fills_next(self):
        """
        Tests that a large market bid clears the best ask level completely, then
        partially fills the next level, respecting price and time priority.
        """
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101)
        ask3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)
        bid = self.create_order(4, OrderTypeEnum.MARKET, BidAskEnum.BID, 40)
        self.order_book.place_order(bid)
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask1.quantity, 0)
        self.assertEqual(ask2.quantity, 0)
        self.assertEqual(ask3.quantity, 5)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.get_best_ask_order()
        self.assertEqual(remaining_ask.order_id, ask3.order_id)
        self.assertEqual(remaining_ask.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 5)

    def test_market_ask_clears_one_level_and_partially_fills_next(self):
        """
        Symmetrical test: A large market ask clears the best bid level completely,
        then partially fills the next level.
        """
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 102)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 101)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)
        ask = self.create_order(4, OrderTypeEnum.MARKET, BidAskEnum.ASK, 40)
        self.order_book.place_order(ask)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(bid1.quantity, 0)
        self.assertEqual(bid2.quantity, 0)
        self.assertEqual(bid3.quantity, 5)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        remaining_bid = self.order_book.get_best_bid_order()
        self.assertEqual(remaining_bid.order_id, bid3.order_id)
        self.assertEqual(remaining_bid.quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 0)

    def test_large_market_bid_clears_all_asks_and_does_not_become_new_best_bid(self):
        """
        Tests that a massive market bid clears the entire ask side of the book
        and its remainder is correctly placed as the new best bid.
        """
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        ask3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 103)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)
        bid = self.create_order(4, OrderTypeEnum.MARKET, BidAskEnum.BID, 100)
        self.order_book.place_order(bid)
        self.assertEqual(ask1.quantity, 0)
        self.assertEqual(ask2.quantity, 0)
        self.assertEqual(ask3.quantity, 0)
        self.assertEqual(bid.quantity, 40)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_quantity_for_price(103, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(103, BidAskEnum.ASK), 0)

    def test_large_market_ask_clears_all_bids_and_does_not_become_new_best_ask(self):
        """
        Symmetrical test: A massive market ask clears the entire bid side
        and its remainder becomes the new best ask.
        """
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 98)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 97)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)
        ask = self.create_order(4, OrderTypeEnum.MARKET, BidAskEnum.ASK, 100)
        self.order_book.place_order(ask)
        self.assertEqual(bid1.quantity, 0)
        self.assertEqual(bid2.quantity, 0)
        self.assertEqual(bid3.quantity, 0)
        self.assertEqual(ask.quantity, 40)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(98, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(97, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(97, BidAskEnum.ASK), 0)
