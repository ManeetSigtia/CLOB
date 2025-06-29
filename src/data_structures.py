# File: data_structures.py

import heapq
from .core_types import Order


class Node:
    def __init__(self, prev=None, next_node=None, val=None):
        self.prev = prev
        self.next_node = next_node
        self.val = val


class DoublyLinkedList:
    def __init__(self):
        self.order_to_node_map = dict()
        self.head = Node()
        self.tail = Node()
        self.head.next_node = self.tail
        self.tail.prev = self.head

    def push(self, order: Order):
        new_node = Node(val=order)
        new_node.prev = self.tail.prev
        new_node.next_node = self.tail
        self.tail.prev.next_node = new_node
        self.tail.prev = new_node
        self.order_to_node_map[order.order_id] = new_node

    def remove(self, order: Order):
        node = self.order_to_node_map.get(order.order_id)
        if node is None:
            return
        previous_node = node.prev
        next_node = node.next_node
        previous_node.next_node = next_node
        next_node.prev = previous_node
        del self.order_to_node_map[order.order_id]

    def peek(self):
        return self.head.next_node.val

    def is_empty(self):
        return self.head.next_node == self.tail


class PriceLevelOrdersBase:
    def __init__(self):
        self.price_to_quantity_map = dict()
        self.price_to_list_map = dict()
        self.price_heap = []

    def add(self, order: Order):
        price = order.price
        heap_price = self._heap_key(price)
        if price in self.price_to_list_map:
            self.price_to_quantity_map[price] += order.quantity
            doubly_linked_list = self.price_to_list_map[price]
            doubly_linked_list.push(order)
        else:
            self.price_to_quantity_map[price] = order.quantity
            doubly_linked_list = DoublyLinkedList()
            doubly_linked_list.push(order)
            self.price_to_list_map[price] = doubly_linked_list
            heapq.heappush(self.price_heap, heap_price)

    def pop(self):
        if not self.price_heap:
            return None
        best_price = self._real_price(self.price_heap[0])
        doubly_linked_list = self.price_to_list_map[best_price]
        order = doubly_linked_list.peek()
        self.price_to_quantity_map[best_price] -= order.quantity
        doubly_linked_list.remove(order)
        if doubly_linked_list.is_empty():
            del self.price_to_quantity_map[best_price]
            del self.price_to_list_map[best_price]
            heapq.heappop(self.price_heap)
        return order

    def decrease_order_quantity(
        self, order_to_decrease: Order, incoming_order_quantity: float
    ):
        self.price_to_quantity_map[order_to_decrease.price] -= incoming_order_quantity
        order_to_decrease.quantity -= incoming_order_quantity

    def delete_best_cancelled_orders(self):
        while self.price_heap:
            best_price = self._real_price(self.price_heap[0])
            doubly_linked_list = self.price_to_list_map[best_price]
            if not doubly_linked_list.is_empty():
                return
            del self.price_to_quantity_map[best_price]
            del self.price_to_list_map[best_price]
            heapq.heappop(self.price_heap)

    def delete_order(self, order: Order):
        order_price = order.price
        if order_price in self.price_to_list_map:
            doubly_linked_list = self.price_to_list_map[order_price]
            doubly_linked_list.remove(order)
            self.price_to_quantity_map[order_price] -= order.quantity

    def get_best_order(self) -> Order | None:
        if not self.price_heap:
            return None
        best_price = self._real_price(self.price_heap[0])
        return self.price_to_list_map[best_price].peek()

    def get_quantity_for_price(self, price: float) -> float:
        return self.price_to_quantity_map.get(price, 0)

    def _heap_key(self, price: float):
        raise NotImplementedError

    def _real_price(self, heap_key):
        raise NotImplementedError


class BidOrders(PriceLevelOrdersBase):
    def _heap_key(self, price: float):
        return -price

    def _real_price(self, heap_key):
        return -heap_key


class AskOrders(PriceLevelOrdersBase):
    def _heap_key(self, price: float):
        return price

    def _real_price(self, heap_key):
        return heap_key
