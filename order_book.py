import datetime
from dataclasses import dataclass
import heapq
from enum import StrEnum, auto


class OrderTypeEnum(StrEnum):
    LIMIT = auto()
    MARKET = auto()
    TRIGGER = auto()


class BidAskEnum(StrEnum):
    BID = auto()
    ASK = auto()


@dataclass
class Order:
    order_id: int
    timestamp: datetime
    order_type_enum: OrderTypeEnum
    bid_ask_enum: BidAskEnum
    price: float | None
    quantity: float
    client: str


class Node:
    def __init__(self, prev=None, nxt=None, val=None):
        self.prev = prev
        self.next = nxt
        self.val = val


class DoublyLinkedList:
    def __init__(self):
        self.order_to_node_map = dict()
        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

    def push(self, order: Order):
        # create new node
        new_node = Node(val=order)

        # update node pointers
        new_node.prev = self.tail.prev
        new_node.next = self.tail

        # update neighbouring pointers
        self.tail.prev.next = new_node
        self.tail.prev = new_node

        self.order_to_node_map[order.order_id] = new_node

    def remove(self, order: Order):
        node = self.order_to_node_map[order.order_id]

        previous_node = node.prev
        next_node = node.next

        previous_node.next = next_node
        next_node.prev = previous_node

        del self.order_to_node_map[order.order_id]

    def peek(self):
        return self.head.next.val

    def is_empty(self):
        return self.head.next == self.tail


class PriceLevelOrdersBase:
    def __init__(self):
        self.price_map = dict()
        self.price_heap = []

    def add(self, order):
        price = order.price
        heap_price = self._heap_key(price)

        if price in self.price_map:
            doubly_linked_list = self.price_map[price]
            doubly_linked_list.push(order)
        else:
            doubly_linked_list = DoublyLinkedList()
            doubly_linked_list.push(order)
            self.price_map[price] = doubly_linked_list
            heapq.heappush(self.price_heap, heap_price)

    def pop(self):
        if not self.price_heap:
            return None

        best_price = self._real_price(self.price_heap[0])
        doubly_linked_list = self.price_map[best_price]
        order = doubly_linked_list.peek()
        doubly_linked_list.remove(order)

        if doubly_linked_list.is_empty():
            del self.price_map[best_price]
            heapq.heappop(self.price_heap)

        return order

    def get_best_order(self):
        if not self.price_heap:
            return None
        best_price = self._real_price(self.price_heap[0])
        return self.price_map[best_price].peek()

    def _heap_key(self, price):
        raise NotImplementedError

    def _real_price(self, heap_key):
        raise NotImplementedError


class BidOrders(PriceLevelOrdersBase):
    def _heap_key(self, price):
        return -price

    def _real_price(self, heap_key):
        return -heap_key


class AskOrders(PriceLevelOrdersBase):
    def _heap_key(self, price):
        return price

    def _real_price(self, heap_key):
        return heap_key


class OrderBook:
    def __init__(self):
        self.bid_orders = BidOrders()
        self.ask_orders = AskOrders()

    def get_best_bid_order(self):
        return self.bid_orders.get_best_order()

    def get_best_ask_order(self):
        return self.ask_orders.get_best_order()

    def get_best_bid_price(self):
        order = self.get_best_bid_order()
        return order.price if order else 0

    def get_best_ask_price(self):
        order = self.get_best_ask_order()
        return order.price if order else 0

    def place_order(self, order: Order) -> None:
        if order.order_type_enum == OrderTypeEnum.LIMIT:
            if order.bid_ask_enum == BidAskEnum.BID:
                if not self.get_best_ask_order():
                    self.bid_orders.add(order)
                    return

                while (
                    order.quantity > 0
                    and self.get_best_ask_price() != 0
                    and order.price >= self.get_best_ask_price()
                ):
                    best_ask_order = self.get_best_ask_order()  # Moved inside loop

                    if best_ask_order is None:
                        break  # Defensive: nothing left to match

                    if order.quantity == best_ask_order.quantity:
                        self.ask_orders.pop()
                        order.quantity = 0
                        best_ask_order.quantity = 0
                    elif order.quantity < best_ask_order.quantity:
                        best_ask_order.quantity -= order.quantity
                        order.quantity = 0
                    else:
                        order.quantity -= best_ask_order.quantity
                        best_ask_order.quantity = 0
                        self.ask_orders.pop()

                if order.quantity > 0:
                    self.bid_orders.add(order)

            else:  # Ask order
                if not self.get_best_bid_order():
                    self.ask_orders.add(order)
                    return

                while (
                    order.quantity > 0
                    and self.get_best_bid_price() != 0
                    and order.price <= self.get_best_bid_price()
                ):
                    best_bid_order = self.get_best_bid_order()  # Moved inside loop

                    if best_bid_order is None:
                        break  # Defensive: nothing left to match

                    if order.quantity == best_bid_order.quantity:
                        self.bid_orders.pop()
                        order.quantity = 0
                        best_bid_order.quantity = 0
                    elif order.quantity < best_bid_order.quantity:
                        best_bid_order.quantity -= order.quantity
                        order.quantity = 0
                    else:
                        order.quantity -= best_bid_order.quantity
                        best_bid_order.quantity = 0
                        self.bid_orders.pop()

                    best_bid_order = self.get_best_bid_order()

                if order.quantity > 0:
                    self.ask_orders.add(order)

    def cancel_order(self, order_id: int) -> None:
        # TODO: implement cancel logic considering empty price levels and heap updates
        pass
