# High-Performance Centralized Limit Order Book (CLOB)

[![codecov](https://codecov.io/gh/ManeetSigtia/CLOB/graph/badge.svg?token=ATR3530NG4)](https://codecov.io/gh/ManeetSigtia/CLOB)

This project is a Python implementation of a Centralized Limit Order Book (CLOB), the core component of a modern financial exchange. It is engineered for high performance, handling the placement and matching of limit and market orders with a focus on low-latency operations.

The project's goal was to architect a solution using efficient data structures that meet the demanding performance requirements of financial systems, particularly the need for high-speed order additions, executions, and cancellations.

---

## Core Architecture & Design Decisions

The performance of an order book is dictated by its ability to perform three actions quickly: **add** a new order, **cancel** an existing order, and **match/execute** incoming orders against resting ones. This design uses a hybrid data structure to optimize for these operations.

An order book consists of two sides: **bids** (buy orders) and **asks** (sell orders). The core challenge is to instantly find the best price on each side—the highest bid and the lowest ask—and to maintain a strict time priority for orders at the same price.

### The Data Structure Trinity: Heap, Dictionary, and Doubly Linked List

Each side of the order book is built with a combination of three data structures working in concert:

1.  **Heap (Priority Queue) - `heapq`**: A **max-heap** for bids (to find the highest price) and a **min-heap** for asks (to find the lowest price) ensures that finding the best price is an $O(1)$ operation. The max-heap is implemented by storing negated prices in Python's min-heap.
2.  **Dictionary (Hash Map) - `dict`**: A dictionary `price_to_list_map` provides an $O(1)$ mapping from a price level to the queue of orders at that price. This avoids any searching when adding a new order to an existing price level.
3.  **Doubly Linked List - `DoublyLinkedList`**: A custom doubly linked list maintains a strict **First-In, First-Out (FIFO)** queue for all orders at a single price level. Its crucial feature is enabling $O(1)$ insertion and, more importantly, $O(1)$ deletion from anywhere in the list.

---

## Key Optimization: True O(1) Order Cancellation

In real-world markets, particularly with algorithmic trading, the **order-to-trade ratio** is often very high. This means many more orders are placed and subsequently cancelled than are actually executed. Optimizing cancellation speed is therefore critical.

**The Challenge**: A naive cancellation would involve removing an order and, if it was the last at its price level, removing that price from the heap. A heap removal is an $O(\log P)$ operation (where P is the number of price levels), making this a performance bottleneck.

**The Solution: Lazy Deletion & Amortized Cleanup**
This implementation achieves true $O(1)$ cancellation through a combination of fast lookups and "lazy" heap maintenance.

1.  **`id_to_order_map`**: A global dictionary mapping an `order_id` to its `Order` object in $O(1)$.
2.  **`order_to_node_map`**: A dictionary within each `DoublyLinkedList` mapping an `order_id` to its specific `Node` in the list, also in $O(1)$.

When an order is cancelled, we use these maps to find and remove the node from the linked list in $O(1)$. **Crucially, the heap is not modified at this time.** The price level, now possibly empty, remains in the heap. This guarantees the cancellation itself is always constant-time.

Stale, empty price levels are purged from the top of the heap by the `delete_best_cancelled_orders` method. This cleanup is called just before major operations (like placing a new order), ensuring its cost is amortized and does not introduce latency during the cancellation itself.

---

## Design Challenges & Justifications

Any engineering design involves trade-offs. Here are some choices made in this project and their rationale.

| Challenge & Question | Justification |
| :--- | :--- |
| **High Memory Footprint?**<br/>"Your design uses multiple dictionaries and custom objects. Isn't this memory-intensive?" | This is a deliberate **space-for-time tradeoff**. In high-performance systems, latency is paramount. The memory overhead of a few extra pointers per order is a small price to pay to reduce key operations from a slow search $(O(N)$ or $O(\log N))$ to constant time $(O(1))$. |
| **Custom `DoublyLinkedList` vs. `collections.deque`?**<br/>"Why write your own list instead of using Python's highly optimized `deque`?" | The key reason is **$O(1)$ internal node removal**. `collections.deque` is fast for additions/removals at the *ends*, but removing an element from the *middle* is an $O(k)$ operation. My custom list, paired with a dictionary mapping IDs to nodes, allows for the removal of *any* order in $O(1)$, which is essential for the fast cancellation guarantee. |
| **Using `float` for Price?**<br/>"Floating-point math is risky for financial applications. Why not use `Decimal`?" | This was a conscious simplification to focus on the **algorithmic complexity and data structure performance**. In a production system, using `Decimal` or scaled integers is non-negotiable. For this project, `float` was sufficient to demonstrate the matching engine's logic. The architecture is decoupled enough that swapping the numeric type would be a straightforward change. |

---

## Testing Strategy & CI

The project's correctness is validated by a comprehensive suite of **59 tests** and is maintained at **99.46% code coverage**. This rigor is enforced automatically through a **Continuous Integration (CI)** pipeline configured with GitHub Actions.

On every push or pull request, the CI pipeline automatically:
1.  Sets up the Python environment.
2.  Installs all dependencies.
3.  Runs the entire test suite using `coverage`.
4.  Generates and uploads coverage reports to **Codecov** to track quality over time.

This automated process ensures that all functionality remains working as expected and that no new code is added without corresponding tests. The test suite covers:

* **Placement & Priority**: Verifies order placement, price priority, and FIFO rules.
* **Order Matching**: Tests full/partial fills and sweeps for both market and limit orders.
* **Cancellation**: Validates simple cancels and edge cases like cancelling from the middle of a queue.
* **Complex Scenarios**: Ensures robustness by testing sequences of operations like cancels followed by matches.

---

## Time Complexity Analysis

Let $P$ be the number of unique price levels and $M$ be the number of orders/levels matched.

| Operation | Time Complexity | Justification |
| :--- | :--- | :--- |
| **Place Limit Order (No Match)** | $O(\log P)$ | Dominated by `heapq.heappush` if it's a new price level. If the price level already exists, it is $O(1)$. |
| **Place Order (With Match)** | $O(M \cdot \log P)$ | The matching loop iterates $M$ times. Each time a price level is fully depleted, `heapq.heappop` $(O(\log P))$ is called. |
| **Cancel Order** | $O(1)$ | **Key Strength.** Achieved via direct dictionary lookups and lazy deletion from the heap. |
| **Get Best Bid/Ask Price/Order** | $O(1)$ | Peeking at the top of the heap and the head of the linked list are constant-time operations. |
