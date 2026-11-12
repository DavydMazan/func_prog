# Лабораторна робота 3 — варіант 6

Незмінна модель бронювання готелю на Python. Сутності `Guest`, `Service` і `Booking` описані frozen dataclasses зі слотами. Послуги зберігаються в tuple, мітки — у frozenset, метадані — у MappingProxyType над свіжою копією словника.

## Структура

```text
lab03/
├── report/
│   ├── lab3.docx
│   └── lab3.pdf
├── tests/
│   ├── test_immutability.py
│   └── test_performance.py
├── baseline.py
├── benchmark.py
├── core.py
├── main.py
├── model.py
├── mypy.ini
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Запуск

```bash
python main.py
pytest -q --durations=5
python benchmark.py
mypy model.py core.py main.py baseline.py
black --check .
ruff check .
```

`baseline.py` існує лише для демонстраційного порівняння вартості створення й оновлення запису. У робочому ядрі зміни виконуються pure-функціями, які повертають нові об’єкти.

## Перевірка

Поточний запуск: 7 pytest-тестів пройшли; mypy і ruff завершилися без зауважень; black застосовано. На вимірюванні 20 000 операцій mutable baseline виконався за 0.0368 s, immutable update — за 0.1700 s. Це локальний мікрозамір із витратами на створення тестових записів, а не універсальне порівняння продуктивності.

## Висновок

Незмінна модель робить побічні зміни явними, спрощує тести й дає можливість хешувати бронювання. За це доводиться платити створенням нових об’єктів під час оновлення; вимірювання часу залежить від середовища та розміру даних.
