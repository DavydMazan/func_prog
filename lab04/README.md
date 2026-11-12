# Лабораторна робота 4 — варіант 6

Тема: рекурсія та мемоізація в Python. Варіант 6 аналізує вкладені списки й кортежі чисел: обчислює суму, кількість чисел і максимальну глибину контейнерів рекурсивно та ітеративно.

## Структура

```text
lab04/
├── report/                 # lab4.docx та lab4.pdf
├── tests/
│   ├── test_fib.py
│   ├── test_nested.py
│   ├── test_quicksort.py
│   └── test_tree.py
├── algorithms.py
├── benchmark.py
├── benchmark_results.json
├── main.py
├── mypy.ini
├── pyproject.toml
├── requirements.txt
└── test_results.txt
```

## Запуск

```bash
python main.py
pytest -q --durations=5
python benchmark.py
mypy algorithms.py main.py benchmark.py
black --check .
ruff check .
```

`algorithms.py` містить тришляховий quicksort із випадковим pivot, рекурсивні обходи дерева, ітеративні BFS/DFS, memoized Fibonacci, ітеративний Fibonacci та функції аналізу вкладених послідовностей. `_analyze_frozen` кешує підсумки незмінних піддерев; однакові підструктури можуть повторно використовувати результат.

## Ліміт рекурсії

CPython має обмеження глибини викликів, доступне через `sys.getrecursionlimit()`, і не виконує автоматичну tail-call optimization. Тому глибокий обхід вкладень виконується ітеративною функцією `analyze_nested_iterative`, яка використовує власний стек.

## Швидкий запуск

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
pytest -q --durations=5
python benchmark.py
mypy algorithms.py main.py benchmark.py
black --check .
ruff check .
```

## Складність

- Quicksort: середній час `O(n log n)`, гірший випадок `O(n²)`; випадковий pivot знижує ризик систематичного найгіршого розбиття.
- Обходи дерева: `O(n)` часу; рекурсивні обходи використовують стек висоти `O(h)`.
- Fibonacci: наївна рекурсія експоненційна, мемоізована `O(n)` за часом і пам’яттю, ітеративна `O(n)` за часом та `O(1)` додаткової пам’яті.
- Вкладена сума й кількість: `O(n)` часу. Рекурсивна версія має стек `O(d)`, ітеративна використовує власний стек, де `d` — максимальна глибина.

## Висновок

Рекурсивні версії коротко виражають поділ задачі на підзадачі. Кешування прискорює обчислення повторних підструктур, а ітеративна реалізація зберігає надійність на глибоких вкладеннях без збільшення стеку викликів.
