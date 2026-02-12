from .core_types import Order, OrderTypeEnum, BidAskEnum
from .data_structures import BidOrders, AskOrders, PriceLevelOrdersBase
from typing import Callable


class OrderBook:
    def __init__(self):
        self.id_to_order_map: dict[int, Order] = dict()
        self.bid_orders: BidOrders = BidOrders()
        self.ask_orders: AskOrders = AskOrders()

    def place_order(self, order: Order) -> None:
        if order.order_type_enum == OrderTypeEnum.MARKET:
            if order.bid_ask_enum == BidAskEnum.BID:
                opposite_book = self.ask_orders
            else:
                opposite_book = self.bid_orders

            self._match_market_order(order, opposite_book)
        elif order.order_type_enum == OrderTypeEnum.LIMIT:
            if order.bid_ask_enum == BidAskEnum.BID:
                home_book, opposite_book = self.bid_orders, self.ask_orders
                price_match_condition = (
                    lambda order_price, book_price: order_price >= book_price
                )
            else:
                home_book, opposite_book = self.ask_orders, self.bid_orders
                price_match_condition = (
                    lambda order_price, book_price: order_price <= book_price
                )

            self._match_limit_order(order, opposite_book, price_match_condition)

            if order.quantity > 0:
                home_book.add(order)
                self.id_to_order_map[order.order_id] = order

    def cancel_order(self, order_id: int) -> None:
        if order_id not in self.id_to_order_map:
            return
        cancelled_order = self.id_to_order_map[order_id]
        selected_book = (
            self.bid_orders
            if cancelled_order.bid_ask_enum == BidAskEnum.BID
            else self.ask_orders
        )
        selected_book.delete_order(cancelled_order)
        self.id_to_order_map.pop(order_id, None)

    def get_best_bid_order(self) -> Order | None:
        return self.bid_orders.get_best_order()

    def get_best_ask_order(self) -> Order | None:
        return self.ask_orders.get_best_order()

    def get_best_bid_price(self) -> float | None:
        order = self.get_best_bid_order()
        return order.price if order else None

    def get_best_ask_price(self) -> float | None:
        order = self.get_best_ask_order()
        return order.price if order else None

    def get_quantity_for_price(self, price: float, bid_ask_type: BidAskEnum) -> float:
        selected_book = (
            self.bid_orders if bid_ask_type == BidAskEnum.BID else self.ask_orders
        )
        return selected_book.get_quantity_for_price(price)

    def _match_limit_order(
        self,
        order: Order,
        opposite_book: PriceLevelOrdersBase,
        price_match_condition: Callable[[float, float], bool],
    ) -> None:
        while order.quantity > 0:
            best_opposite_order = opposite_book.get_best_order()
            if best_opposite_order is None or not price_match_condition(
                order.price, best_opposite_order.price
            ):
                return

            self._execute_match(order, best_opposite_order, opposite_book)

    def _match_market_order(
        self, order: Order, opposite_book: PriceLevelOrdersBase
    ) -> None:
        while order.quantity > 0:
            best_opposite_order = opposite_book.get_best_order()
            if best_opposite_order is None:
                return

            self._execute_match(order, best_opposite_order, opposite_book)

    def _execute_match(
        self,
        incoming_order: Order,
        best_opposite_order: Order,
        opposite_book: PriceLevelOrdersBase,
    ) -> None:
        trade_quantity = min(incoming_order.quantity, best_opposite_order.quantity)
        if incoming_order.quantity >= best_opposite_order.quantity:
            opposite_book.delete_order(best_opposite_order)
            incoming_order.quantity -= trade_quantity
            best_opposite_order.quantity = 0
            self.id_to_order_map.pop(best_opposite_order.order_id, None)
        else:
            opposite_book.decrease_order_quantity(best_opposite_order, trade_quantity)
            incoming_order.quantity = 0
