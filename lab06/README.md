# Лабораторна робота 6 — варіант 6

Проєкт демонструє замикання та параметризовані декоратори для симуляції повторних спроб файлової операції. Зовнішні залежності — годинник, sleep, генератор джиттера та logger — можна замінити детермінованими функціями у тестах.

## Швидкий запуск

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
pytest -q
mypy closures.py decorators.py app.py
black --check .
ruff check .
```

## Складові

- `closures.py`: `make_counter`, `make_logger` і closure-backed статистика повторів.
- `decorators.py`: `timed`, `retries`, `cached` з TTL/повною/точковою інвалідацією, а також `retry_statistics`.
- `app.py`: файлова операція симулюється функцією; реальний диск і очікування не використовуються.
- `tests/`: замінюють clock, sleep, random та logger; перевіряють нормальні результати, винятки, TTL, інвалідацію і `functools.wraps`.

Порядок у демонстрації: `cached` не використовується для файлового retry виклику; для самої операції `retries` обгорнутий статистикою та таймінгом. Повторні спроби фіксуються hook-функцією, а зовнішній декоратор статистики записує успішний чи невдалий виклик.
