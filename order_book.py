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

    def peek(self):
        return self.head.next.val

    def is_empty(self):
        return self.head.next == self.tail


class BidOrders:
    def __init__(self):
        """
        This class stores a heap data structure
        Each Node of the Heap will store the price and then a doubly linked list

        get_best_order function will return the first element from the doubly linked list in the first node of the heap. Without deleting
        how do i store the doubly linked list and the price key value pair

        the add method will, based on the price of the order, add it to the corresponding doubly linked list to the end
        if the price of the new order is more than the current max, the heap will be updated.
        limit orders always have a price

        for pop method, find the largest price, and then find the doubly linked list associated to it
        remove the first node from this linked list
        """
        self.price_map = (
            dict()
        )  # simulates a queue of orders for that price (new orders added to the back)
        self.price_heap = []  # max_heap

        pass

    def add(self, order: Order):
        order_price = order.price

        if order_price in self.price_map:
            doubly_linked_list = self.price_map[order_price]
            doubly_linked_list.push(order)
        else:
            doubly_linked_list = DoublyLinkedList()
            doubly_linked_list.push(order)
            self.price_map[order_price] = doubly_linked_list
            heapq.heappush(self.price_heap, -order_price)

    def get_best_order(self) -> Order:
        if not self.price_heap:
            return None
        best_price = -self.price_heap[0]
        doubly_linked_list = self.price_map[best_price]
        return doubly_linked_list.peek()


class AskOrders:
    def __init__(self):
        self.price_map = (
            dict()
        )  # key: price, value: doubly linked list. simulates a queue of orders for that price (new orders added to the back)
        self.price_heap = []  # min_heap

    def add(self, order: Order):
        order_price = order.price

        if order_price in self.price_map:
            doubly_linked_list = self.price_map[order_price]
            doubly_linked_list.push(order)
        else:
            doubly_linked_list = DoublyLinkedList()
            doubly_linked_list.push(order)
            self.price_map[order_price] = doubly_linked_list
            heapq.heappush(self.price_heap, order_price)

    def get_best_order(self) -> Order:
        if not self.price_heap:
            return None
        best_price = self.price_heap[0]
        doubly_linked_list = self.price_map[best_price]
        return doubly_linked_list.peek()


class OrderBook:
    def __init__(self):
        self.best_ask_price = 0
        self.best_bid_price = 0
        self.bid_orders = BidOrders()
        self.ask_orders = AskOrders()

    def place_order(self, order: Order) -> None:
        """
        if a bid order comes in, you need to check the ask heap
        if the price of the bid order is 6 and the lowest ask order price is 5, then at the price of 5 we need to clear the ask heap
            in terms of quantities:
                if we bid 50 shares, and we have 60 available on the ask side:
                    the ask order should fall to 10 for that price
                if we bid 50 shares, and we have 50 available for that price
                    the ask order should be deleted
                    if no more orders exist at that price, the next smallest price should move up
                if we bid 50 shares, and we we have 20 available for that price
                    the ask order should be popped, and the next ask order should be compared
                    if the price on the next one is more, then this needs to be added to bid order book
        """
        if order.order_type_enum == OrderTypeEnum.LIMIT:
            if order.bid_ask_enum == BidAskEnum.BID:
                best_ask_order = self.ask_orders.get_best_order()
                if not best_ask_order:
                    self.bid_orders.add(order)
                    self.best_bid_price = self.bid_orders.get_best_order().price
                    return

                while order.quantity > 0 and self.best_ask_price <= order.price:
                    if order.quantity == best_ask_order.quantity:
                        self.ask_orders.pop()
                        order.quantity = 0
                    elif order.quantity < best_ask_order.quantity:
                        best_ask_order.quantity -= order.quantity
                        order.quantity = 0
                    else:
                        order_quantity -= best_ask_order.quantity
                        self.ask_orders.pop()
                        if self.ask_orders:
                            best_ask_order = self.ask_orders.get_best_order()
                            self.best_ask_price = best_ask_order.price
                        else:
                            self.bid_orders.add(order)
                            self.best_bid_price = self.bid_orders.get_best_order().price

            else:  # order.bid_ask_enum == BidAskEnum.ASK
                best_bid_order = self.bid_orders.get_best_order()
                if not best_bid_order:
                    self.ask_orders.add(order)
                    self.best_ask_price = self.ask_orders.get_best_order().price
                    return

                while order.quantity > 0 and order.price <= self.best_bid_price:
                    if order.quantity == best_bid_order.quantity:
                        self.bid_orders.pop()
                        order.quantity = 0
                    elif order.quantity < best_bid_order.quantity:
                        best_bid_order.quantity -= order.quantity
                        order.quantity = 0
                    else:
                        order_quantity -= best_bid_order.quantity
                        self.bid_orders.pop()
                        if self.bid_orders:
                            best_bid_order = self.bid_orders.get_best_order()
                            self.best_bid_price = best_bid_order.price
                        else:
                            self.ask_orders.add(order)
                            self.best_ask_price = self.ask_orders.get_best_order().price

    def cancel_order(self, order_id: int) -> None:
        pass
