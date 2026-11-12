# Лабораторна робота №2

## Функції вищого порядку, lambda та композиція

Реалізовано функціональний конвеєр формування рейтингу книг: обчислення середньої оцінки, множник для вибраного жанру, фільтр за мінімальним рейтингом, сортування та Top-N. Вхідні записи не змінюються.

### Структура

- `core.py` — чисті трансформації книг, `compose`, `pipe`, `juxt`, Top-N та `reduce`-агрегація.
- `app.py` — CLI та робота з JSON.
- `tests/test_core.py` — тести конвеєра й чистих функцій.
- `sample_data.json` — демонстраційні книжкові дані.
- `report/` — звіт у PDF та редагованому DOCX.

### Запуск (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python app.py --data sample_data.json --top 3 --boost-genre Fantasy --factor 1.1 --min-rating 3.5
```

Перевірки стилю та типів:

```powershell
black --check .
ruff check .
mypy core.py app.py
```

