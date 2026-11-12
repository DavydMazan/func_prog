# Лабораторна робота 5 — варіант 6

Проєкт демонструє ліниві генератори, `itertools` і обробку фінансових транзакцій. Функції обмежують споживання потоку запитаною кількістю значень, а нескінченні потоки не перетворюються повністю на списки.

## Швидкий запуск

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
pytest -q
mypy streams.py core.py main.py
black --check .
ruff check .
```

## Реалізація

- `streams.py`: нескінченні Fibonacci/naturals, `take`, `drop`, `sliding_window`, `moving_average`, а також ліниві обгортки для `takewhile`, `dropwhile`, `cycle` і `repeat`.
- `core.py`: відбір додатних сум, `accumulate` для поточного балансу та перші N сум ковзних вікон через `islice`/`starmap`.
- `main.py`: коротке відтворюване демо; вивід збережено у `demo_output.txt`.
- `tests/`: перевірки результатів, крайніх випадків і точного числа запитаних елементів.

Генератор зберігає внутрішню позицію та вичерпується після проходу. Для незалежного проходу створюйте його знову. Необмежені послідовності треба завжди обмежувати `take`/`islice` чи умовою завершення. `sliding_window` використовує `deque(maxlen=k)`, тому не матеріалізує все джерело.
