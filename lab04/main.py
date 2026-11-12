"""Command-line demonstration for laboratory work 4, variant 6."""

from algorithms import (
    Node,
    analyze_nested,
    analyze_nested_iterative,
    analyze_nested_memoized,
    bfs_level_order,
    fib,
    fib_iter,
    quicksort,
)
from algorithms import NestedValue


def main() -> None:
    nested: NestedValue = [1, (2, [3, 4]), ((2, (3, 4)),), []]
    tree = Node(4, Node(2, Node(1), Node(3)), Node(6, None, Node(7)))
    fib.cache_clear()
    recursive = analyze_nested(nested)
    memoized = analyze_nested_memoized(nested)
    iterative = analyze_nested_iterative(nested)

    print("=== Рекурсія та мемоізація: варіант 6 ===")
    print(f"Вкладена структура (сума, кількість, глибина): {recursive}")
    print(f"Memoized результат: {memoized}")
    print(f"Iterative результат: {iterative}")
    print(f"Cache info для Fibonacci(30): {fib(30)}; {fib.cache_info()}")
    print(f"Fibonacci iterative(30): {fib_iter(30)}")
    print(f"Quicksort: {quicksort([8, 3, 3, -1, 5, 0])}")
    print(f"Обхід дерева BFS: {bfs_level_order(tree)}")


if __name__ == "__main__":
    main()
