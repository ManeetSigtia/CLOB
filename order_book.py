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

        if node is None:
            return

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
        self.price_to_quantity_map = dict()
        self.price_to_list_map = dict()
        self.price_heap = []

    def add(self, order):
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

    def delete_best_cancelled_orders(self):
        while self.price_heap:
            best_price = self._real_price(self.price_heap[0])
            doubly_linked_list = self.price_to_list_map[best_price]

            if not doubly_linked_list.is_empty():
                return

            del self.price_to_quantity_map[best_price]
            del self.price_to_list_map[best_price]
            heapq.heappop(self.price_heap)

    def delete_order(self, order):
        order_price = order.price
        doubly_linked_list = self.price_to_list_map[order_price]
        doubly_linked_list.remove(order)
        self.price_to_quantity_map[order_price] -= order.quantity

    def get_best_order(self):
        if not self.price_heap:
            return None
        best_price = self._real_price(self.price_heap[0])
        return self.price_to_list_map[best_price].peek()

    def get_quantity_for_price(self, price):
        return self.price_to_quantity_map.get(price, 0)

    def _heap_key(self, price):
        pass

    def _real_price(self, heap_key):
        pass


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
        self.id_to_order_map = dict()
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

    def get_quantity_for_price(self, price, order_type):
        """
        depending on the order_type, get the correct heap
        once we have the heap, we need to check if the price exists in the heap
        if the price does not exist, we return 0
        if we have the price, we need to look in the book's quantity map for that price and return the value

        this means when an order is placed, this map needs to be updated too.
        so, if an order is added to the book, we need to see if the price exists in that book
        if the price does not exist, the we set the key value pair straightaway
        if the price does exist, we retrieve the quantity entry from the map and add to it

        however, before anything is added, if a match is made:
        the while loop really helps here. we can just focus on 1 iteration. if any sort of matching is done, we update the respective books.
        it also helps that I am already updating the order itself, so if the order quantity falls to 0 because its been matched, we can check for this before creating an entry in the price to quantity map
        after each subtraction at the bid/ask heap level, if any of the quantities fall to 0, we need to delete that key value pair from the map
        """

        selected_book = (
            self.bid_orders if order_type == BidAskEnum.BID else self.ask_orders
        )
        return selected_book.get_quantity_for_price(price)

    def place_order(self, order: Order) -> None:
        self.bid_orders.delete_best_cancelled_orders()
        self.ask_orders.delete_best_cancelled_orders()

        if order.bid_ask_enum == BidAskEnum.BID:
            if order.order_type_enum == OrderTypeEnum.LIMIT:
                if not self.get_best_ask_order():
                    self.bid_orders.add(order)
                    self.id_to_order_map[order.order_id] = order
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
                        del self.id_to_order_map[best_ask_order.order_id]
                    elif order.quantity < best_ask_order.quantity:
                        # I dont like the fact that I am accessing the price to quantity map here, need a cleverer way to update this map
                        # I probably don't like it because its not happening in the other if elif blocks, its being handled in the pop
                        self.ask_orders.price_to_quantity_map[
                            best_ask_order.price
                        ] -= order.quantity
                        best_ask_order.quantity -= order.quantity
                        order.quantity = 0
                    else:
                        self.ask_orders.pop()
                        order.quantity -= best_ask_order.quantity
                        best_ask_order.quantity = 0
                        del self.id_to_order_map[best_ask_order.order_id]

                    self.ask_orders.delete_best_cancelled_orders()

                if order.quantity > 0:
                    self.bid_orders.add(order)
                    self.id_to_order_map[order.order_id] = order

        else:  # Ask order
            if order.order_type_enum == OrderTypeEnum.LIMIT:
                if not self.get_best_bid_order():
                    self.ask_orders.add(order)
                    self.id_to_order_map[order.order_id] = order
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
                        del self.id_to_order_map[best_bid_order.order_id]
                    elif order.quantity < best_bid_order.quantity:
                        self.bid_orders.price_to_quantity_map[
                            best_bid_order.price
                        ] -= order.quantity
                        best_bid_order.quantity -= order.quantity
                        order.quantity = 0
                    else:
                        self.bid_orders.pop()
                        order.quantity -= best_bid_order.quantity
                        best_bid_order.quantity = 0
                        del self.id_to_order_map[best_bid_order.order_id]

                    self.bid_orders.delete_best_cancelled_orders()

                if order.quantity > 0:
                    self.ask_orders.add(order)
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
