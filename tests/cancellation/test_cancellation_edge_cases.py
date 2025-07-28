from tests.base_test import BaseOrderBookTest, BidAskEnum, OrderTypeEnum


class TestEdgeCaseCancellation(BaseOrderBookTest):
    def test_cancel_non_existent_order(self):
        """Tests that cancelling a non-existent order_id does not crash."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 999)
        self.order_book.place_order(bid)
        self.order_book.cancel_order(999)
        self.order_book.place_order(ask)
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 10)

    def test_cancel_fully_filled_order(self):
        """Tests cancelling an order that has already been fully filled."""
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        self.order_book.place_order(bid)
        self.order_book.place_order(ask)
        self.assertIsNone(self.order_book.bid_orders.get_best_order())
        self.order_book.cancel_order(1)
        self.assertIsNone(self.order_book.bid_orders.get_best_order())

    def test_cancel_from_middle_of_queue(self):
        """Tests cancelling an order from the middle of a price level's queue."""
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        ask = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 999)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 45
        )
        self.order_book.cancel_order(2)
        self.order_book.place_order(ask)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 30
        )
        self.assertEqual(self.order_book.get_best_bid_order().order_id, 1)
        ask_match = self.create_order(5, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 25, 100)
        self.order_book.place_order(ask_match)
        self.assertEqual(self.order_book.get_best_bid_order().order_id, 3)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 5)
