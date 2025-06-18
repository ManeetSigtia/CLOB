import unittest
from datetime import datetime
from order_book import Order, OrderBook, OrderTypeEnum, BidAskEnum


class TestOrderBook(unittest.TestCase):

    def setUp(self):
        """Ensures a fresh order book for each test."""
        self.order_book = OrderBook()

    # Note: Removed redundant create_order method. This one is used for all tests.
    def create_order(
        self, order_id, type_enum, side_enum, quantity, price=None, client="ClientA"
    ):
        """Helper to create orders, matching the signature from your example."""
        return Order(
            order_id=order_id,
            timestamp=datetime.now(),
            order_type_enum=type_enum,
            bid_ask_enum=side_enum,
            price=price,
            quantity=quantity,
            client=f"{client}{order_id}",
        )

    def test_place_bid_order(self):
        """Tests placing a single bid order on an empty book."""
        # Action: Place one bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)

        # Expected Outcome: The bid should be the best bid, and the ask side should be empty.
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 0)

    def test_place_ask_order(self):
        """Tests placing a single ask order on an empty book."""
        # Action: Place one ask order.
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)

        # Expected Outcome: The ask should be the best ask, and the bid side should be empty.
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)

    def test_place_multiple_bid_orders_at_same_price(self):
        """Tests FIFO ordering for multiple bid orders at the same price."""
        # Setup: Place multiple bids at the same price.
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, qty, 99)
            )

        # Expected Outcome: The first order placed (quantity 10) should be the best order.
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 10)

    def test_place_multiple_bid_orders_at_different_price(self):
        """Tests price priority for multiple bid orders at different prices."""
        # Setup: Place multiple bids at different prices.
        prices = [99, 98, 100]
        for i, price in enumerate(prices, start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, price)
            )

        # Expected Outcome: The highest bid price (100) should be the best bid.
        self.assertEqual(self.order_book.get_best_bid_price(), 100)

    def test_place_multiple_ask_orders_at_same_price(self):
        """Tests FIFO ordering for multiple ask orders at the same price."""
        # Setup: Place multiple asks at the same price.
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, qty, 99)
            )

        # Expected Outcome: The first order placed (quantity 10) should be the best order.
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_place_multiple_ask_orders_at_different_price(self):
        """Tests price priority for multiple ask orders at different prices."""
        # Setup: Place multiple asks at different prices.
        prices = [99, 98, 100]
        for i, price in enumerate(prices, start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, price)
            )

        # Expected Outcome: The lowest ask price (98) should be the best ask.
        self.assertEqual(self.order_book.get_best_ask_price(), 98)

    def test_no_bid_order_execution_while_ask_order_exists(self):
        """Tests that no execution occurs when the bid price is below the ask price."""
        # Setup: Place an ask order.
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        self.order_book.place_order(ask)

        # Action: Place a bid order with a price lower than the existing ask.
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)

        # Expected Outcome: Both orders should remain on the book without execution.
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_no_ask_order_execution_while_bid_order_exists(self):
        """Tests that no execution occurs when the ask price is above the bid price."""
        # Setup: Place a bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)

        # Action: Place an ask order with a price higher than the existing bid.
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        self.order_book.place_order(ask)

        # Expected Outcome: Both orders should remain on the book without execution.
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 20)
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)

    def test_bid_order_execution_complete_clearance_while_ask_order_exists(self):
        """Tests a full match where a new bid clears a resting ask of the same size."""
        # Setup: Place a resting ask order.
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)

        # Action: Place a bid of the same price and quantity.
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)

        # Expected Outcome: Both orders are fully executed and the book is empty.
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())

    def test_ask_order_execution_complete_clearance_while_bid_order_exists(self):
        """Tests a full match where a new ask clears a resting bid of the same size."""
        # Setup: Place a resting bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)

        # Action: Place an ask of the same price and quantity.
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)

        # Expected Outcome: Both orders are fully executed and the book is empty.
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 0)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertIsNone(self.order_book.get_best_ask_order())

    def test_bigger_quantity_bid_order_partial_execution_while_ask_order_exists(self):
        """Tests a partial match where a larger new bid clears a smaller resting ask."""
        # Setup: Place a small resting ask order.
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)

        # Action: Place a larger bid at the same price.
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)

        # Expected Outcome: The ask is cleared, and the bid's remainder is placed on the book.
        self.assertEqual(bid.quantity, 10)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.get_best_bid_order(), bid)
        self.assertIsNone(self.order_book.get_best_ask_order())

    def test_smaller_quantity_bid_order_partial_execution_while_ask_order_exists(self):
        """Tests a partial match where a new bid is fully filled by a larger resting ask."""
        # Setup: Place a large resting ask order.
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 35, 99)
        self.order_book.place_order(ask)

        # Action: Place a smaller bid at the same price.
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 99)
        self.order_book.place_order(bid)

        # Expected Outcome: The bid is cleared, and the ask remains with reduced quantity.
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 15)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_order(), ask)

    def test_bigger_quantity_ask_order_partial_execution_while_bid_order_exists(self):
        """Tests a partial match where a larger new ask clears a smaller resting bid."""
        # Setup: Place a small resting bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        self.order_book.place_order(bid)

        # Action: Place a larger ask at the same price.
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 99)
        self.order_book.place_order(ask)

        # Expected Outcome: The bid is cleared, and the ask's remainder is placed on the book.
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask.quantity, 20)
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_order(), ask)

    def test_smaller_quantity_ask_order_partial_execution_while_bid_order_exists(self):
        """Tests a partial match where a new ask is fully filled by a larger resting bid."""
        # Setup: Place a large resting bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 99)
        self.order_book.place_order(bid)

        # Action: Place a smaller ask at the same price.
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)

        # Expected Outcome: The ask is cleared, and the bid remains with reduced quantity.
        self.assertEqual(bid.quantity, 20)
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(self.order_book.get_best_bid_order(), bid)
        self.assertIsNone(self.order_book.get_best_ask_order())

    def test_partial_execution_across_multiple_ask_orders_with_bid(self):
        """Tests a bid executing against multiple resting asks at different prices."""
        # Setup: Place two ask orders at different price levels. Best price is 101.
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 102)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 101)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)

        # Action: Place a bid that can clear the best ask and partially fill the next.
        bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 25, 102)
        self.order_book.place_order(bid)

        # Expected Outcome: The best ask (ask2) is cleared, and the next ask (ask1) is partially filled.
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.ask_orders.get_best_order()
        self.assertIsNotNone(remaining_ask)
        self.assertEqual(remaining_ask.price, 102)
        self.assertEqual(
            remaining_ask.quantity, 5
        )  # 10 (original) - 5 (remaining from bid)

    def test_partial_execution_across_multiple_bid_orders_with_ask(self):
        """Tests an ask executing against multiple resting bids at different prices."""
        # Setup: Place two bid orders at different price levels. Best price is 102.
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 101)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)

        # Action: Place an ask that can clear the best bid and partially fill the next.
        ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 25, 101)
        self.order_book.place_order(ask)

        # Expected Outcome: The best bid (bid2) is cleared, and the next bid (bid1) is partially filled.
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        remaining_bid = self.order_book.bid_orders.get_best_order()
        self.assertIsNotNone(remaining_bid)
        self.assertEqual(remaining_bid.price, 101)
        self.assertEqual(
            remaining_bid.quantity, 5
        )  # 20 (original) - 15 (remaining from ask)

    def test_bid_clears_one_level_and_partially_fills_next(self):
        """
        Tests that a large bid clears the best ask level completely, then
        partially fills the next level, respecting price and time priority.
        """
        # Setup: Three resting ask orders across two price levels.
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101)
        ask3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)

        # Action: A large bid comes in that can cross both levels.
        bid = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 40, 102)
        self.order_book.place_order(bid)

        # Expected Outcome: The first two asks are cleared, the third is partially filled.
        self.assertEqual(bid.quantity, 0, "Incoming bid should be fully filled")
        self.assertEqual(
            ask1.quantity, 0, "First ask at best price should be fully filled"
        )
        self.assertEqual(
            ask2.quantity, 0, "Second ask at best price should be fully filled"
        )
        self.assertEqual(
            ask3.quantity, 5, "Ask at second-best price should be partially filled"
        )

        # The book should have no bids and only the remainder of ask3.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.get_best_ask_order()
        self.assertEqual(remaining_ask.order_id, ask3.order_id)
        self.assertEqual(remaining_ask.quantity, 5)

    def test_ask_clears_one_level_and_partially_fills_next(self):
        """
        Symmetrical test: A large ask clears the best bid level completely,
        then partially fills the next level.
        """
        # Setup: Three resting bid orders across two price levels.
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 102)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 101)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)

        # Action: A large ask comes in that can cross both levels.
        ask = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 40, 101)
        self.order_book.place_order(ask)

        # Expected Outcome: The first two bids are cleared, the third is partially filled.
        self.assertEqual(ask.quantity, 0)
        self.assertEqual(bid1.quantity, 0)
        self.assertEqual(bid2.quantity, 0)
        self.assertEqual(bid3.quantity, 5)

        # The book should have no asks and only the remainder of bid3.
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        remaining_bid = self.order_book.get_best_bid_order()
        self.assertEqual(remaining_bid.order_id, bid3.order_id)
        self.assertEqual(remaining_bid.quantity, 5)

    def test_large_bid_clears_all_asks_and_becomes_new_best_bid(self):
        """
        Tests that a massive bid clears the entire ask side of the book
        and its remainder is correctly placed as the new best bid.
        """
        # Setup: Several resting asks at different price levels.
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        ask3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 103)
        self.order_book.place_order(ask1)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)

        # Action: A bid large enough to clear all asks is placed.
        bid = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 100, 103)
        self.order_book.place_order(bid)

        # Expected Outcome: All asks are cleared and the bid's remainder becomes the best bid.
        self.assertEqual(ask1.quantity, 0)
        self.assertEqual(ask2.quantity, 0)
        self.assertEqual(ask3.quantity, 0)
        self.assertEqual(bid.quantity, 40)

        # The ask book should be empty, and the bid book should contain the remainder.
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 103)
        remaining_bid = self.order_book.get_best_bid_order()
        self.assertEqual(remaining_bid.quantity, 40)
        self.assertEqual(remaining_bid.order_id, bid.order_id)

    def test_large_ask_clears_all_bids_and_becomes_new_best_ask(self):
        """
        Symmetrical test: A massive ask clears the entire bid side
        and its remainder becomes the new best ask.
        """
        # Setup: Several resting bids at different price levels.
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid2 = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 98)
        bid3 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 97)
        self.order_book.place_order(bid1)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)

        # Action: An ask large enough to clear all bids is placed.
        ask = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 100, 97)
        self.order_book.place_order(ask)

        # Expected Outcome: All bids are cleared and the ask's remainder becomes the best ask.
        self.assertEqual(bid1.quantity, 0)
        self.assertEqual(bid2.quantity, 0)
        self.assertEqual(bid3.quantity, 0)
        self.assertEqual(ask.quantity, 40)

        # The bid book should be empty, and the ask book should contain the remainder.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 97)
        remaining_ask = self.order_book.get_best_ask_order()
        self.assertEqual(remaining_ask.quantity, 40)
        self.assertEqual(remaining_ask.order_id, ask.order_id)


if __name__ == "__main__":
    unittest.main()
