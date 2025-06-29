# File: order_book.py

from .core_types import Order, OrderTypeEnum, BidAskEnum
from .data_structures import BidOrders, AskOrders, PriceLevelOrdersBase


class OrderBook:
    def __init__(self):
        self.id_to_order_map = dict()
        self.bid_orders = BidOrders()
        self.ask_orders = AskOrders()

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

    def get_quantity_for_price(self, price: float, order_type: BidAskEnum) -> float:
        selected_book = (
            self.bid_orders if order_type == BidAskEnum.BID else self.ask_orders
        )
        return selected_book.get_quantity_for_price(price)

    def _match_order(
        self, order: Order, opposite_book: PriceLevelOrdersBase, price_match_condition
    ):
        while order.quantity > 0:
            best_opposite_order = opposite_book.get_best_order()
            if best_opposite_order is None or not price_match_condition(
                order.price, best_opposite_order.price
            ):
                break
            if order.quantity == best_opposite_order.quantity:
                opposite_book.pop()
                order.quantity = 0
                best_opposite_order.quantity = 0
                del self.id_to_order_map[best_opposite_order.order_id]
            elif order.quantity < best_opposite_order.quantity:
                opposite_book.decrease_order_quantity(
                    best_opposite_order, order.quantity
                )
                order.quantity = 0
            else:
                opposite_book.pop()
                order.quantity -= best_opposite_order.quantity
                best_opposite_order.quantity = 0
                del self.id_to_order_map[best_opposite_order.order_id]
            opposite_book.delete_best_cancelled_orders()

    def place_order(self, order: Order) -> None:
        self.bid_orders.delete_best_cancelled_orders()
        self.ask_orders.delete_best_cancelled_orders()
        if order.order_type_enum != OrderTypeEnum.LIMIT:
            return
        if order.bid_ask_enum == BidAskEnum.BID:
            home_book = self.bid_orders
            opposite_book = self.ask_orders
            price_match_condition = (
                lambda order_price, book_price: order_price >= book_price
            )
        else:
            home_book = self.ask_orders
            opposite_book = self.bid_orders
            price_match_condition = (
                lambda order_price, book_price: order_price <= book_price
            )
        self._match_order(order, opposite_book, price_match_condition)
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
        del self.id_to_order_map[order_id]
