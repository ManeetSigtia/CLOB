# High-Performance Centralized Limit Order Book (CLOB)

[![codecov](https://codecov.io/gh/ManeetSigtia/CLOB/graph/badge.svg?token=ATR3530NG4)](https://codecov.io/gh/ManeetSigtia/CLOB)

This project is a Python implementation of a Centralized Limit Order Book (CLOB), the core component of a modern financial exchange. It is architected for high performance, handling the placement and matching of various order types with a focus on low-latency, predictable operations.

The project's goal was to engineer a solution using efficient data structures that meet the demanding performance requirements of financial systems, particularly the need for high-speed order additions, executions, and—most critically—cancellations.

## Visual Demonstration

The animation below showcases the data structures in action, visualizing how orders are placed, cancelled, and how a market order sweeps the book.

![Order Book Animation](assets/order_book_visualised.gif)

## Table of Contents

- [Core Architecture](#core-architecture)
- [The Lazy Deletion Strategy for O(1) Cancellation](#the-lazy-deletion-strategy-for-o1-cancellation)
- [Design Challenges & Justifications](#design-challenges--justifications)
- [Testing Strategy & CI](#testing-strategy--ci)
- [Time Complexity Analysis](#time-complexity-analysis)

## Core Architecture

The performance of an order book is dictated by its ability to perform three actions quickly: **add** a new order, **cancel** an existing order, and **match/execute** incoming orders against resting ones. This design uses a hybrid data structure to optimize for these operations.

An order book consists of two sides: **bids** (buy orders) and **asks** (sell orders). The core challenge is to instantly find the best price on each side—the highest bid and the lowest ask—and to maintain a strict time priority for orders at the same price.

### The Data Structure Trinity: Heap, Dictionary, and Doubly Linked List

Each side of the active order book is built with a combination of three data structures working in concert:

1.  **Heap (Priority Queue) - `heapq`**: A **max-heap** for bids (to find the highest price) and a **min-heap** for asks (to find the lowest price) ensures that _peeking_ at the best price is an $O(1)$ operation. The max-heap is implemented by storing negated prices in Python's min-heap.
2.  **Dictionary (Hash Map) - `dict`**: A dictionary `price_to_list_map` provides an $O(1)$ mapping from a price level to the queue of orders at that price. This avoids any searching when adding a new order to an existing price level.
3.  **Doubly Linked List - `DoublyLinkedList`**: A custom doubly linked list maintains a strict **First-In, First-Out (FIFO)** queue for all orders at a single price level. Its crucial feature is enabling $O(1)$ insertion and, more importantly, $O(1)$ deletion from anywhere in the list.

## The Lazy Deletion Strategy for O(1) Cancellation

In real-world markets, particularly with algorithmic trading, the **order-to-trade ratio** is often very high. This means many more orders are placed and subsequently cancelled than are actually executed. Optimizing cancellation speed is therefore a primary architectural goal.

**The Solution: True O(1) Cancellation via Lazy Deletion**
This implementation achieves a guaranteed $O(1)$ cancellation time through a combination of fast lookups and "lazy" heap maintenance.

1.  **`id_to_order_map`**: A global dictionary mapping an `order_id` to its `Order` object in $O(1)$.
2.  **`order_to_node_map`**: A dictionary within each `DoublyLinkedList` mapping an `order_id` to its specific `Node` in the list, also in $O(1)$.

When an order is cancelled, we use these maps to find and remove the node from the linked list in $O(1)$. **Crucially, the heap is not modified at this time.** The price level, now possibly empty, remains in the heap as a "stale" entry. This guarantees the cancellation itself is always constant-time.

Stale, empty price levels are purged from the heap **only when necessary**. This cleanup logic is centralized in the `get_best_order()` method. Before this "getter" returns the state of the book, it first cleans any stale entries from the top of the heap. This ensures two things:

1.  The cancellation operation is never slowed down by cleanup tasks.
2.  The getter methods are the **single source of truth** and always return a correct, non-stale view of the book, regardless of what operation (a cancel or a match) caused the heap to become stale.

This design is a deliberate architectural choice that adheres to two key software engineering principles:

- **Single Responsibility Principle (SRP):** The `get_best_order()` method has one job: to reliably report the correct best order. To fulfill this promise, it must be responsible for handling any data inconsistencies (like stale entries) first. The "writer" functions (`cancel_order`, `_execute_match`) are correctly focused on their single responsibility of changing the state.
- **Don't Repeat Yourself (DRY):** By centralizing the cleanup logic in a single getter, the code is written once. The alternative would require duplicating the same cleanup loop in every function that could possibly change the best price, leading to a brittle and hard-to-maintain system.

## Design Challenges & Justifications

Any engineering design involves trade-offs. Here are some key choices made in this project and their rationale.

| Challenge & Question                                                                                                                       | Justification                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :----------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Why isn't `get_best_price` a true $O(1)$ operation?**<br/>"Shouldn't a high-performance system provide an instant, constant-time 'get'?" | This is the core architectural trade-off of the system. To achieve a true $O(1)$ `get`, the heap would need to be kept perfectly clean at all times. This would require cleaning the heap during cancellation, making the `cancel` operation a slow $O(P)$ in the worst case. In any real trading system, a **predictably fast $O(1)$ `cancel` is far more critical than a guaranteed $O(1)$ `get`**. This design correctly prioritizes the most time-sensitive operations, accepting a slightly slower (amortized $O(\log P))$ `get` in exchange for a lightning-fast `cancel`. |
| **Why the high memory footprint?**<br/>"Your design uses multiple dictionaries and custom objects. Isn't this memory-intensive?"           | This is a deliberate **space-for-time tradeoff**. In high-performance systems, latency is paramount. The memory overhead of a few extra pointers per order is a small price to pay to reduce key operations from a slow search $(O(N)$ or $O(\log N))$ to constant time $(O(1))$.                                                                                                                                                                                                                                                                                                |
| **Custom `DoublyLinkedList` vs. `collections.deque`?**<br/>"Why write your own list instead of using Python's highly optimized `deque`?"   | The key reason is **$O(1)$ internal node removal**. `collections.deque` is fast for additions/removals at the _ends_, but removing an element from the _middle_ is an $O(k)$ operation. My custom list, paired with a dictionary mapping IDs to nodes, allows for the removal of _any_ order in $O(1)$, which is essential for the fast cancellation guarantee.                                                                                                                                                                                                                  |
| **Using `float` for Price?**<br/>"Floating-point math is risky for financial applications. Why not use `Decimal`?"                         | This was a conscious simplification to focus on the **algorithmic complexity and data structure performance**. In a production system, using `Decimal` or scaled integers is non-negotiable. For this project, `float` was sufficient to demonstrate the matching engine's logic. The architecture is decoupled enough that swapping the numeric type would be a straightforward change.                                                                                                                                                                                         |

## Testing Strategy & CI

The project's correctness is validated by a comprehensive suite of **61 tests** and is maintained at **99.46% code coverage**. This rigor is enforced automatically through a **Continuous Integration (CI)** pipeline configured with GitHub Actions.

On every push or pull request, the CI pipeline automatically:

1.  Sets up the Python environment.
2.  Installs all dependencies.
3.  Runs the entire test suite using `unittest`'s discovery.
4.  Generates and uploads coverage reports to **Codecov** to track quality over time.

This automated process ensures that all functionality remains working as expected and that no new code is added without corresponding tests. The test suite is logically organized into subdirectories covering:

- **Placement & Priority**: Verifies order placement, price priority, and FIFO rules.
- **Order Matching**: Tests full/partial fills and sweeps for both market and limit orders.
- **Cancellation**: Validates simple cancels and edge cases like cancelling from the middle of a queue.
- **Complex Scenarios**: Ensures robustness by testing sequences of operations like cancels followed by matches.

## Time Complexity Analysis

Let $P$ be the number of unique price levels and $M$ be the number of orders/levels matched.

| Operation                        | Time Complexity           | Justification                                                                                                                                                                                                                       |
| :------------------------------- | :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Place Limit Order (No Match)** | $O(\log P)$               | Dominated by `heapq.heappush` if it's a new price level. If the price level already exists, it is $O(1)$.                                                                                                                           |
| **Place Order (With Match)**     | $O(M \cdot \log P)$       | The matching loop iterates $M$ times. Each time a price level is fully depleted, a `heappop` $(O(\log P))$ is called.                                                                                                               |
| **Cancel Order**                 | $O(1)$                    | **Key Strength.** Achieved via direct dictionary lookups and lazy deletion from the heap.                                                                                                                                           |
| **Get Best Bid/Ask Price/Order** | **Amortized** $O(\log P)$ | **Correct by Design.** While often $O(1)$, it includes the potential cost of cleaning up `k` stale price levels from the top of the heap, making its performance amortized. This is the trade-off for a guaranteed $O(1)$ `cancel`. |
