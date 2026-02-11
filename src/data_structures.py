from __future__ import annotations
import heapq
from .core_types import Order


class Node:
    def __init__(
        self,
        prev: Node | None = None,
        next_node: Node | None = None,
        val: Order | None = None,
    ):
        self.prev = prev
        self.next_node = next_node
        self.val = val


class DoublyLinkedList:
    def __init__(self):
        self.order_id_to_node_map: dict[int, Node] = dict()
        self.head: Node = Node()
        self.tail: Node = Node()
        self.head.next_node = self.tail
        self.tail.prev = self.head

    def push(self, order: Order) -> None:
        new_node = Node(val=order)
        new_node.prev = self.tail.prev
        new_node.next_node = self.tail
        self.tail.prev.next_node = new_node
        self.tail.prev = new_node
        self.order_id_to_node_map[order.order_id] = new_node

    def remove(self, order: Order) -> None:
        node = self.order_id_to_node_map.get(order.order_id)
        if node is None:
            return
        previous_node = node.prev
        next_node = node.next_node
        previous_node.next_node = next_node
        next_node.prev = previous_node
        del self.order_id_to_node_map[order.order_id]

    def peek(self) -> Order | None:
        return self.head.next_node.val

    def is_empty(self) -> bool:
        return self.head.next_node == self.tail


class PriceLevelOrdersBase:
    def __init__(self):
        self.price_to_quantity_map: dict[float, float] = dict()
        self.price_to_list_map: dict[float, DoublyLinkedList] = dict()
        self.price_heap: list[float] = []

    # called once an order has undergone matching process and there is still remaining quantity, hence must be added to order book
    def add(self, order: Order) -> None:
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

    # called to cancel/fulfill a particular order (remove from dll but leave price on heap)
    def delete_order(self, order: Order) -> None:
        order_price = order.price
        if order_price not in self.price_to_list_map:
            return

        doubly_linked_list = self.price_to_list_map[order_price]
        doubly_linked_list.remove(order)
        self.price_to_quantity_map[order_price] -= order.quantity

        if doubly_linked_list.is_empty():
            del self.price_to_quantity_map[order_price]
            del self.price_to_list_map[order_price]

    # called when incoming order quantity < resting order quantity, so no change to heap
    def decrease_order_quantity(
        self, order_to_decrease: Order, incoming_order_quantity: float
    ) -> None:
        self.price_to_quantity_map[order_to_decrease.price] -= incoming_order_quantity
        order_to_decrease.quantity -= incoming_order_quantity

    def get_quantity_for_price(self, price: float) -> float:
        return self.price_to_quantity_map.get(price, 0)

    # cleans heap for stale prices and then returns best order
    def get_best_order(self) -> Order | None:
        self._delete_best_cancelled_orders()
        if not self.price_heap:
            return None
        best_price = self._real_price(self.price_heap[0])
        return self.price_to_list_map[best_price].peek()

    # cleans heap until a dll for a price level has orders
    def _delete_best_cancelled_orders(self) -> None:
        while self.price_heap:
            best_price = self._real_price(self.price_heap[0])
            doubly_linked_list = self.price_to_list_map.get(best_price)

            if doubly_linked_list is None or doubly_linked_list.is_empty():
                self.price_to_list_map.pop(best_price, None)
                self.price_to_quantity_map.pop(best_price, None)
                heapq.heappop(self.price_heap)
            else:
                return

    def _heap_key(self, price: float) -> float:
        raise NotImplementedError

    def _real_price(self, heap_key) -> float:
        raise NotImplementedError


class BidOrders(PriceLevelOrdersBase):
    def _heap_key(self, price: float) -> float:
        return -price

    def _real_price(self, heap_key) -> float:
        return -heap_key


class AskOrders(PriceLevelOrdersBase):
    def _heap_key(self, price: float) -> float:
        return price

    def _real_price(self, heap_key) -> float:
        return heap_key
