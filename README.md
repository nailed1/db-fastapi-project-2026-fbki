# Hotel Booking Management

Система управления бронированием отелей. Учебный проект по двум дисциплинам:
- **Информатика** — проектирование БД (11 таблиц, IDEF0, SQL-запросы, GUI)
- **Культура разработки ПО** — FastAPI, Poetry, Docker, Sphinx, тесты, TestPyPI

## Стек

| Слой | Технология |
|---|---|
| Backend | FastAPI + asyncpg |
| Frontend | HTMX + Jinja2 + Tailwind CSS |
| База данных | PostgreSQL 16 |
| Утилитная библиотека | `hotel_utils` (TestPyPI) |
| Документация | Sphinx + sphinx_rtd_theme |
| Тесты | pytest + pytest-asyncio |
| Контейнеризация | Docker + docker-compose |
| CI/CD | GitHub Actions |

## Быстрый старт

```bash
# 1. Зависимости
poetry install

# 2. Запустить PostgreSQL
make docker-up

# 3. Применить миграции
make migrate

# 4. Загрузить тестовые данные
make seed

# 5. Запустить сервер
make dev
# → http://localhost:8000
```

## Команды

```bash
make test          # запустить все тесты
make test-unit     # только unit-тесты (без БД)
make lint          # ruff + mypy
make fmt           # автоформатирование
make docs          # собрать Sphinx документацию
make lib-publish-test  # опубликовать hotel_utils на TestPyPI
```

## Структура проекта

```
├── app/                  # FastAPI приложение
│   ├── api/routes/       # маршруты (bookings, rooms, guests, staff)
│   ├── templates/        # Jinja2 + HTMX шаблоны
│   ├── db/               # migrate.py, seed.py
│   └── main.py
├── packages/
│   └── hotel_utils/      # утилитная библиотека → TestPyPI
│       └── src/hotel_utils/
│           ├── pricing.py
│           ├── loyalty.py
│           └── availability.py
├── migrations/           # SQL (001_init, 002_seed)
├── tests/
│   ├── unit/             # тесты hotel_utils (без БД)
│   └── integration/      # тесты FastAPI routes
├── docs/                 # Sphinx документация
├── diagrams/             # PlantUML (context, sequence, ERD)
├── docker/               # Dockerfile + docker-compose
├── Makefile
└── pyproject.toml        # Poetry
```

## Публикация библиотеки на TestPyPI

```bash
# Добавить токен
poetry config pypi-token.testpypi <TOKEN>

# Собрать и опубликовать
make lib-publish-test
```

## Диаграммы

Исходники PlantUML в `diagrams/`. Рендер:
- VS Code: расширение **PlantUML**
- Онлайн: https://www.plantuml.com/plantuml/uml/
