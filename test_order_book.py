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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 10)

    def test_place_ask_order(self):
        """Tests placing a single ask order on an empty book."""
        # Action: Place one ask order.
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 99)
        self.order_book.place_order(ask)

        # Expected Outcome: The ask should be the best ask, and the bid side should be empty.
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(self.order_book.get_best_bid_price(), 0)

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 10)

    def test_place_multiple_bid_orders_at_same_price(self):
        """Tests FIFO ordering for multiple bid orders at the same price."""
        # Setup: Place multiple bids at the same price.
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.BID, qty, 99)
            )

        # Expected Outcome: The first order placed (quantity 10) should be the best order.
        self.assertEqual(self.order_book.bid_orders.get_best_order().quantity, 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 60)

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
        for price in prices:
            self.assertEqual(
                self.order_book.get_quantity_for_price(price, BidAskEnum.BID), 10
            )

    def test_place_multiple_ask_orders_at_same_price(self):
        """Tests FIFO ordering for multiple ask orders at the same price."""
        # Setup: Place multiple asks at the same price.
        for i, qty in enumerate([10, 30, 20], start=1):
            self.order_book.place_order(
                self.create_order(i, OrderTypeEnum.LIMIT, BidAskEnum.ASK, qty, 99)
            )

        # Expected Outcome: The first order placed (quantity 10) should be the best order.
        self.assertEqual(self.order_book.ask_orders.get_best_order().quantity, 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 60)

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
        for price in prices:
            self.assertEqual(
                self.order_book.ask_orders.get_quantity_for_price(price), 10
            )

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 10
        )

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 10
        )

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 10)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 15)

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 20)

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 20)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.ASK), 0)

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

        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 5)

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

        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 5)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)

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
        self.assertEqual(bid.quantity, 0)
        self.assertEqual(ask1.quantity, 0)
        self.assertEqual(ask2.quantity, 0)
        self.assertEqual(ask3.quantity, 5)

        # The book should have no bids and only the remainder of ask3.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 102)
        remaining_ask = self.order_book.get_best_ask_order()
        self.assertEqual(remaining_ask.order_id, ask3.order_id)
        self.assertEqual(remaining_ask.quantity, 5)

        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 5)

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

        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 5)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 0)

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

        self.assertEqual(
            self.order_book.get_quantity_for_price(103, BidAskEnum.BID), 40
        )
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(103, BidAskEnum.ASK), 0)

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

        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(98, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(97, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(97, BidAskEnum.ASK), 40)

    """
    create the other way around test for the following also:
    test cases:
    - have just 1 bid order and cancel it
    - have 1 bid order and cancel it and then pass in 1 ask order
    - have 2 bid orders, and then cancel the best one, and then pass 1 ask order
    - have 2 bid orders, and then cancel the worse one, and then pass 1 ask order
    - have 1 bid order, pass an ask order, and try to cancel the bid order
    - have 1 bid order, cancel it, pass in 1 more bid order at same price, and pass 1 ask order
    - have 1 bid order, cancel it, pass in 1 bid order at same price and 1 worse price, and pass 1 huge ask order that sweeps the book
    - have 6 bid orders, 2 at each price level, cancel the best 4, and then pass through an ask order, and then another ask order
    - have 6 bid orders, 2 at best price, 3 at price after, and 1 at worst price, and then cancel the 3 bid orders at middle level, and then pass in ask orders and see what happens (might require 2 tests, 1 where ask order is small and the other where the ask order clears the entire bid order book)
    """

    def test_cancel_single_bid_order(self):
        """Tests cancelling the only bid order on the book."""
        # Setup: Place one bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 999)
        self.order_book.place_order(bid)

        # Action: Cancel the order.
        self.order_book.cancel_order(1)
        self.order_book.place_order(ask)

        # Expected Outcome: The bid side of the book should be empty.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 0)

    def test_cancel_single_ask_order(self):
        """Tests cancelling the only ask order on the book."""
        # Setup: Place one ask order.
        ask = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 1)
        self.order_book.place_order(ask)

        # Action: Cancel the order.
        self.order_book.cancel_order(1)
        self.order_book.place_order(bid)

        # Expected Outcome: The ask side of the book should be empty.
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 0)

    def test_cancel_best_of_two_bids(self):
        """Tests cancelling the best bid order when two are present."""
        # Setup: Place two bid orders at different prices.
        bid_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 999)
        self.order_book.place_order(bid_worse)
        self.order_book.place_order(bid_best)

        # Action: Cancel the best bid (order_id 2).
        self.order_book.cancel_order(2)
        self.order_book.place_order(ask)

        # Expected Outcome: The new best bid should be the remaining order.
        self.assertEqual(self.order_book.get_best_bid_price(), 99)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 10)

    def test_cancel_best_of_two_asks(self):
        """Tests cancelling the best ask order when two are present."""
        # Setup: Place two ask orders at different prices.
        ask_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 100)
        bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 1)
        self.order_book.place_order(ask_worse)
        self.order_book.place_order(ask_best)

        # Action: Cancel the best ask (order_id 2).
        self.order_book.cancel_order(2)
        self.order_book.place_order(bid)

        # Expected Outcome: The new best ask should be the remaining order.
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 0)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 10
        )

    def test_cancel_worse_of_two_bids(self):
        """Tests cancelling a non-best bid order."""
        # Setup: Place two bid orders at different prices.
        bid_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 99)
        bid_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 999)
        self.order_book.place_order(bid_worse)
        self.order_book.place_order(bid_best)

        # Action: Cancel the worse bid (order_id 1).
        self.order_book.cancel_order(1)
        self.order_book.place_order(ask)

        # Expected Outcome: The best bid should be unaffected.
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 15
        )
        self.assertEqual(self.order_book.get_quantity_for_price(99, BidAskEnum.BID), 0)

    def test_cancel_worse_of_two_asks(self):
        """Tests cancelling a non-best ask order."""
        # Setup: Place two ask orders at different prices.
        ask_worse = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 101)
        ask_best = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 100)
        bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 1)
        self.order_book.place_order(ask_worse)
        self.order_book.place_order(ask_best)

        # Action: Cancel the worse ask (order_id 1).
        self.order_book.cancel_order(1)
        self.order_book.place_order(bid)

        # Expected Outcome: The best ask should be unaffected.
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 15
        )
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)

    def test_cancel_non_existent_order(self):
        """Tests that cancelling a non-existent order_id does not crash."""
        # Setup: Place a bid order.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 999)
        self.order_book.place_order(bid)

        # Action: Attempt to cancel an order_id that does not exist.
        self.order_book.cancel_order(999)
        self.order_book.place_order(ask)

        # Expected Outcome: The book state should be unchanged.
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 10)

    def test_cancel_fully_filled_order(self):
        """Tests cancelling an order that has already been fully filled."""
        # Setup: Place a bid and an ask that will fully match.
        bid = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        dummy_ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        self.order_book.place_order(bid)
        self.order_book.place_order(ask)  # This triggers the match
        self.assertIsNone(
            self.order_book.bid_orders.get_best_order()
        )  # Confirm match happened

        # Action: Attempt to cancel the original bid (order_id 1) which is now filled.
        self.order_book.cancel_order(1)
        self.order_book.place_order(dummy_ask)

        # Expected Outcome: The book remains empty, no errors are raised.
        self.assertIsNone(self.order_book.bid_orders.get_best_order())

    def test_cancel_from_middle_of_queue(self):
        """Tests cancelling an order from the middle of a price level's queue."""
        # Setup: Place three bids at the same price.
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

        # Action: Cancel the middle order (order_id 2).
        self.order_book.cancel_order(2)
        self.order_book.place_order(ask)

        # Expected Outcome: The total quantity at the price level is reduced.
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 30
        )
        # The first order in is still the best order.
        self.assertEqual(self.order_book.get_best_bid_order().order_id, 1)

        # Action 2: Place an ask to test FIFO integrity.
        ask = self.create_order(5, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 25, 100)
        self.order_book.place_order(ask)

        # Expected Outcome 2: The ask fills the first order (10) and partially fills the third (15/20).
        self.assertEqual(self.order_book.get_best_bid_order().order_id, 3)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 5)

    def test_cancel_unmatched_order_after_opposite_side_is_placed(self):
        """Tests cancelling a bid after a non-matching ask has been placed."""
        # Setup: Place a bid and a non-matching ask.
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

        # Action: Cancel the original bid.
        self.order_book.cancel_order(1)
        # Trigger with a dummy order that won't execute.
        dummy_ask = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)

        # Expected Outcome: The bid should be gone, and the asks should remain.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 101)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 0)
        self.assertEqual(
            self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 15
        )

    def test_cancel_unmatched_ask_after_opposite_side_is_placed(self):
        """Tests cancelling an ask after a non-matching bid has been placed."""
        # Setup: Place an ask and a non-matching bid.
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

        # Action: Cancel the original ask.
        self.order_book.cancel_order(1)
        # Trigger with a dummy order that won't execute.
        dummy_bid = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)

        # Expected Outcome: The ask should be gone, and the bids should remain.
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 15
        )

    def test_cancel_then_repopulate_price_level_and_match_bid(self):
        """Tests that a price level can be emptied, repopulated, and then matched."""
        # Setup: Place a single bid.
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        self.order_book.place_order(bid1)

        # Action 1: Cancel the bid, emptying the price level.
        self.order_book.cancel_order(1)
        dummy_ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)
        self.assertIsNone(self.order_book.get_best_bid_order())

        # Action 2: Add a new bid at the same price and an ask to match it.
        bid2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        ask_match = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 100)
        self.order_book.place_order(bid2)
        self.order_book.place_order(ask_match)

        # Expected outcome: The new bid should be partially filled.
        self.assertEqual(self.order_book.get_best_bid_price(), 100)
        self.assertEqual(self.order_book.get_best_bid_order().quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 5)

    def test_cancel_then_repopulate_price_level_and_match_ask(self):
        """Tests that a price level can be emptied, repopulated, and then matched."""
        # Setup: Place a single ask.
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        self.order_book.place_order(ask1)

        # Action 1: Cancel the ask, emptying the price level.
        self.order_book.cancel_order(1)
        dummy_bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)
        self.assertIsNone(self.order_book.get_best_ask_order())

        # Action 2: Add a new ask at the same price and a bid to match it.
        ask2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 100)
        bid_match = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        self.order_book.place_order(ask2)
        self.order_book.place_order(bid_match)

        # Expected outcome: The new ask should be partially filled.
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(self.order_book.get_best_ask_order().quantity, 5)
        self.assertEqual(self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 5)

    def test_cancel_then_sweep_book_bid(self):
        """Tests a book sweep after a cancel and addition of new orders."""
        # Setup: Place a bid.
        bid1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 100)
        self.order_book.place_order(bid1)

        # Action 1: Cancel the bid.
        self.order_book.cancel_order(1)
        dummy_ask = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)

        # Action 2: Place two new bids.
        bid2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        bid3 = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.BID, 30, 99)
        self.order_book.place_order(bid2)
        self.order_book.place_order(bid3)

        # Action 3: A huge ask sweeps the book.
        ask_sweep = self.create_order(5, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 100, 99)
        self.order_book.place_order(ask_sweep)

        # Expected outcome: The bid book is cleared and the remaining ask is on the book.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 99)
        self.assertEqual(
            self.order_book.get_best_ask_order().quantity, 50
        )  # 100 - (20+30)

    def test_cancel_then_sweep_book_ask(self):
        """Tests a book sweep after a cancel and addition of new orders."""
        # Setup: Place an ask.
        ask1 = self.create_order(1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
        self.order_book.place_order(ask1)

        # Action 1: Cancel the ask.
        self.order_book.cancel_order(1)
        dummy_bid = self.create_order(2, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)

        # Action 2: Place two new asks.
        ask2 = self.create_order(3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 100)
        ask3 = self.create_order(4, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 30, 101)
        self.order_book.place_order(ask2)
        self.order_book.place_order(ask3)

        # Action 3: A huge bid sweeps the book.
        bid_sweep = self.create_order(5, OrderTypeEnum.LIMIT, BidAskEnum.BID, 100, 101)
        self.order_book.place_order(bid_sweep)

        # Expected outcome: The ask book is cleared and the remaining bid is on the book.
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 101)
        self.assertEqual(
            self.order_book.get_best_bid_order().quantity, 50
        )  # 100 - (20+30)

    def test_cancel_middle_price_level_and_partially_fill_bid(self):
        """Tests cancelling a whole price level from the middle of the bid book."""
        # Setup: 6 bids across 3 price levels (102, 101, 100).
        for i in range(2):
            self.order_book.place_order(
                self.create_order(i + 1, OrderTypeEnum.LIMIT, BidAskEnum.BID, 10, 102)
            )  # Best
        for i in range(3):
            self.order_book.place_order(
                self.create_order(i + 3, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 101)
            )  # Middle
        self.order_book.place_order(
            self.create_order(6, OrderTypeEnum.LIMIT, BidAskEnum.BID, 20, 100)
        )  # Worst

        # Action 1: Cancel the 3 orders in the middle price level (101).
        self.order_book.cancel_order(3)
        self.order_book.cancel_order(4)
        self.order_book.cancel_order(5)
        dummy_ask = self.create_order(7, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 5, 999)
        self.order_book.place_order(dummy_ask)

        # Expected outcome 1: Price level 101 should be gone.
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.BID), 0)
        self.assertEqual(self.order_book.get_best_bid_price(), 102)

        # Action 2: Place a small ask that only fills the best level.
        ask_small = self.create_order(8, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 102)
        self.order_book.place_order(ask_small)

        # Expected outcome 2: The best level is partially filled, worst level is untouched.
        self.assertEqual(self.order_book.get_best_bid_price(), 102)
        self.assertEqual(
            self.order_book.get_quantity_for_price(102, BidAskEnum.BID), 5
        )  # 20-15
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.BID), 20
        )

    def test_cancel_middle_price_level_and_sweep_bid(self):
        """Tests sweeping the bid book after cancelling a middle price level."""
        # Setup: 6 bids across 3 price levels (102, 101, 100).
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

        # Action 1: Cancel the 3 orders in the middle price level (101).
        for i in range(3):
            self.order_book.cancel_order(i + 3)

        # Action 2: Place a huge ask that sweeps the remaining levels.
        ask_sweep = self.create_order(
            8, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 50, 100
        )  # Price hits all remaining
        self.order_book.place_order(ask_sweep)

        # Expected outcome 2: The bid book is empty, remainder of ask is on book.
        self.assertIsNone(self.order_book.get_best_bid_order())
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(
            self.order_book.get_best_ask_order().quantity, 10
        )  # 50 - (20+20)

    def test_cancel_middle_price_level_and_partially_fill_ask(self):
        """Tests cancelling a whole price level from the middle of the ask book."""
        # Setup: 6 asks across 3 price levels (100, 101, 102).
        for i in range(2):
            self.order_book.place_order(
                self.create_order(i + 1, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 10, 100)
            )  # Best
        for i in range(3):
            self.order_book.place_order(
                self.create_order(i + 3, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 15, 101)
            )  # Middle
        self.order_book.place_order(
            self.create_order(6, OrderTypeEnum.LIMIT, BidAskEnum.ASK, 20, 102)
        )  # Worst

        # Action 1: Cancel the 3 orders in the middle price level (101).
        self.order_book.cancel_order(3)
        self.order_book.cancel_order(4)
        self.order_book.cancel_order(5)
        dummy_bid = self.create_order(7, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)

        # Expected outcome 1: Price level 101 should be gone.
        self.assertEqual(self.order_book.get_quantity_for_price(101, BidAskEnum.ASK), 0)
        self.assertEqual(self.order_book.get_best_ask_price(), 100)

        # Action 2: Place a small bid that only fills the best level.
        bid_small = self.create_order(8, OrderTypeEnum.LIMIT, BidAskEnum.BID, 15, 100)
        self.order_book.place_order(bid_small)

        # Expected outcome 2: The best level is partially filled, worst level is untouched.
        self.assertEqual(self.order_book.get_best_ask_price(), 100)
        self.assertEqual(
            self.order_book.get_quantity_for_price(100, BidAskEnum.ASK), 5
        )  # 20-15
        self.assertEqual(
            self.order_book.get_quantity_for_price(102, BidAskEnum.ASK), 20
        )

    def test_cancel_middle_price_level_and_sweep_ask(self):
        """Tests sweeping the ask book after cancelling a middle price level."""
        # Setup: 6 asks across 3 price levels (100, 101, 102).
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

        # Action 1: Cancel the 3 orders in the middle price level (101).
        self.order_book.cancel_order(3)
        self.order_book.cancel_order(4)
        self.order_book.cancel_order(5)
        dummy_bid = self.create_order(7, OrderTypeEnum.LIMIT, BidAskEnum.BID, 5, 1)
        self.order_book.place_order(dummy_bid)

        # Action 2: Place a huge bid that sweeps the remaining levels.
        bid_sweep = self.create_order(
            8, OrderTypeEnum.LIMIT, BidAskEnum.BID, 50, 102
        )  # Price hits all remaining
        self.order_book.place_order(bid_sweep)

        # Expected outcome 2: The ask book is empty, remainder of bid is on book.
        self.assertIsNone(self.order_book.get_best_ask_order())
        self.assertEqual(self.order_book.get_best_bid_price(), 102)
        self.assertEqual(
            self.order_book.get_best_bid_order().quantity, 10
        )  # 50 - (20+20)


if __name__ == "__main__":
    unittest.main()
