# File: tests/scenarios/test_cancellation_scenarios.py

from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestCancellationScenarios(BaseOrderBookTest):
    def test_cancel_unmatched_order_after_opposite_side_is_placed(self):
        """Tests cancelling a bid after a non-matching ask has been placed."""
        bid_to_cancel = self.create_order(
            1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100
        )
        ask_non_matching = self.create_order(
            2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101
        )
        self.order_book.place_order(bid_to_cancel)
        self.order_book.place_order(ask_non_matching)
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.order_book.cancel_order(1)
        dummy_ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 0)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 15
        )

    def test_cancel_unmatched_ask_after_opposite_side_is_placed(self):
        """Tests cancelling an ask after a non-matching bid has been placed."""
        ask_to_cancel = self.create_order(
            1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101
        )
        bid_non_matching = self.create_order(
            2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100
        )
        self.order_book.place_order(ask_to_cancel)
        self.order_book.place_order(bid_non_matching)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.order_book.cancel_order(1)
        dummy_bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 15
        )

    def test_cancel_then_repopulate_price_level_and_match_bid(self):
        """Tests that a price level can be emptied, repopulated, and then matched."""
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        self.order_book.place_order(bid1)
        self.order_book.cancel_order(1)
        dummy_ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)
        self.assertIsNone(self.order_book.get_best_bid_order())
        bid2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        ask_match = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 100)
        self.order_book.place_order(bid2)
        self.order_book.place_order(ask_match)
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 5)

    def test_cancel_then_repopulate_price_level_and_match_ask(self):
        """Tests that a price level can be emptied, repopulated, and then matched."""
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        self.order_book.place_order(ask1)
        self.order_book.cancel_order(1)
        dummy_bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)
        self.assertIsNone(self.order_book.get_best_ask_order())
        ask2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 100)
        bid_match = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        self.order_book.place_order(ask2)
        self.order_book.place_order(bid_match)
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(self.order_book.get_best_ask_order().quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 5)

    def test_cancel_then_sweep_book_bid(self):
        """Tests a book sweep after a cancel and addition of new orders."""
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        self.order_book.place_order(bid1)
        self.order_book.cancel_order(1)
        dummy_ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)
        bid2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        bid3 = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 99)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)
        ask_sweep = self.create_order(5, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 100, 99)
        self.order_book.place_order(ask_sweep)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_order().quantity, 50)

    def test_cancel_then_sweep_book_ask(self):
        """Tests a book sweep after a cancel and addition of new orders."""
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        self.order_book.place_order(ask1)
        self.order_book.cancel_order(1)
        dummy_bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)
        ask2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 100)
        ask3 = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 101)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)
        bid_sweep = self.create_order(5, OrderTypeEnum.LIMIT, BidAskEnum.BID, 100, 101)
        self.order_book.place_order(bid_sweep)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 50)

    def test_cancel_middle_price_level_and_partially_fill_bid(self):
        """Tests cancelling a whole price level from the middle of the bid book."""
        for i in range(2):
            self.order_book.place_order(
                self.create_order(i + 1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
            )
        for i in range(3):
            self.order_book.place_order(
                self.create_order(i + 3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 101)
            )
        self.order_book.place_order(
            self.create_order(6, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        )
        self.order_book.cancel_order(3)
        self.order_book.cancel_order(4)
        self.order_book.cancel_order(5)
        dummy_ask = self.create_order(7, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_best_bid_price(), 102)
        ask_small = self.create_order(8, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 102)
        self.order_book.place_order(ask_small)
        self.assertEqual(self.order_book.get_best_bid_price(), 102)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 5)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 20
        )

    def test_cancel_middle_price_level_and_sweep_bid(self):
        """Tests sweeping the bid book after cancelling a middle price level."""
        for i in range(2):
            self.order_book.place_order(
                self.create_order(i + 1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
            )
        for i in range(3):
            self.order_book.place_order(
                self.create_order(i + 3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 101)
            )
        self.order_book.place_order(
            self.create_order(6, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        )
        for i in range(3):
            self.order_book.cancel_order(i + 3)
        ask_sweep = self.create_order(8, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 50, 100)
        self.order_book.place_order(ask_sweep)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(self.order_book.get_best_ask_order().quantity, 10)

    def test_cancel_middle_price_level_and_partially_fill_ask(self):
        """Tests cancelling a whole price level from the middle of the ask book."""
        for i in range(2):
            self.order_book.place_order(
                self.create_order(i + 1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
            )
        for i in range(3):
            self.order_book.place_order(
                self.create_order(i + 3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101)
            )
        self.order_book.place_order(
            self.create_order(6, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        )
        self.order_book.cancel_order(3)
        self.order_book.cancel_order(4)
        self.order_book.cancel_order(5)
        dummy_bid = self.create_order(7, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        bid_small = self.create_order(8, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        self.order_book.place_order(bid_small)
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 5)
        self.assertEqual(
            self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 20
        )

    def test_cancel_middle_price_level_and_sweep_ask(self):
        """Tests sweeping the ask book after cancelling a middle price level."""
        for i in range(2):
            self.order_book.place_order(
                self.create_order(i + 1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
            )
        for i in range(3):
            self.order_book.place_order(
                self.create_order(i + 3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101)
            )
        self.order_book.place_order(
            self.create_order(6, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        )
        self.order_book.cancel_order(3)
        self.order_book.cancel_order(4)
        self.order_book.cancel_order(5)
        dummy_bid = self.create_order(7, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)
        bid_sweep = self.create_order(8, OrderTypeEnum.LIMIT, BidAskEnum.BID, 50, 102)
        self.order_book.place_order(bid_sweep)
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 102)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 10)
