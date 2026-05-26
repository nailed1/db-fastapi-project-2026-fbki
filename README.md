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
| Оплата | YooKassa (webhook) |

## Жизненный цикл брони

```
Ожидает оплаты → [оплата YooKassa] → Подтверждено → [запрос возврата] → Ожидает возврата → Отменено
Ожидает оплаты → [отмена до оплаты] → Отменено
Подтверждено   → [завершение] → Завершено
```

Поле `payment_status`: `Не оплачено` → `Оплачено` → `Возврат`.

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
├── app/                          # FastAPI приложение
│   ├── api/
│   │   ├── routes/               # маршруты
│   │   │   ├── auth.py           # вход / регистрация
│   │   │   ├── bookings.py       # бронирования
│   │   │   ├── rooms.py          # номера
│   │   │   ├── guests.py         # гости
│   │   │   ├── staff.py          # персонал
│   │   │   ├── portal_admin.py   # портал администратора
│   │   │   ├── portal_manager.py # портал менеджера
│   │   │   ├── portal_staff.py   # портал горничной / техника
│   │   │   └── portal_tourist.py # портал туриста
│   │   └── dependencies.py       # общие зависимости маршрутов
│   ├── auth/                     # JWT-авторизация
│   │   ├── jwt.py                # выдача и проверка токенов
│   │   ├── flash.py              # flash-сообщения
│   │   └── dependencies.py       # current_user и проверка ролей
│   ├── db/                       # работа с БД
│   │   ├── migrate.py            # применение миграций
│   │   ├── seed.py               # загрузка тестовых данных
│   │   └── setup_passwords.py    # хеширование паролей персонала
│   ├── models/
│   │   └── schemas.py            # Pydantic-схемы
│   ├── templates/                # Jinja2 + HTMX шаблоны
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── layouts/
│   │   │   └── portal.html       # базовый лейаут портала
│   │   ├── auth/                 # login.html, register.html
│   │   ├── booking/              # list.html, create.html
│   │   ├── rooms/                # list.html
│   │   ├── guests/               # list.html, create.html
│   │   ├── manager/              # dashboard.html, cleaning.html
│   │   └── portal/               # дашборды по ролям
│   │       ├── admin/            # dashboard.html, users.html
│   │       ├── manager/          # dashboard.html, schedule.html
│   │       ├── staff/            # dashboard.html
│   │       └── tourist/          # dashboard.html, hotel.html, book.html,
│   │                             # booking_detail.html, review.html
│   ├── static/                   # статика (CSS, JS)
│   ├── config.py                 # настройки приложения
│   ├── database.py               # пул соединений asyncpg
│   └── main.py                   # точка входа FastAPI
├── packages/
│   └── hotel_utils/              # утилитная библиотека → TestPyPI
│       └── src/hotel_utils/
│           ├── pricing.py
│           ├── loyalty.py
│           └── availability.py
├── migrations/                   # SQL-миграции
│   ├── 001_init.sql              # схема БД (11 таблиц)
│   ├── 002_seed.sql              # тестовые данные
│   ├── 003_roles_auth.sql        # роли, авторизация, отзывы, расписания
│   ├── 004_coordinates.sql       # координаты отелей
│   ├── 005_payment_status.sql    # колонка payment_status в bookings
│   ├── 006_booking_status.sql    # ограничение статусов брони
│   ├── 007_payment_id.sql        # yookassa_payment_id в bookings
│   ├── 008_refund_requests.sql   # таблица запросов на возврат
│   └── 009_refund_status.sql     # статус 'Ожидает возврата' в bookings
├── tests/
│   ├── unit/                     # тесты hotel_utils (без БД)
│   └── integration/              # тесты FastAPI routes
├── docs/                         # Sphinx документация
├── diagrams/                     # PlantUML (context, sequence, ERD)
├── docker/                       # Dockerfile + docker-compose + entrypoint.sh
├── .github/workflows/            # CI (ci.yml) + публикация (publish.yml)
├── Makefile
└── pyproject.toml                # Poetry
```

## Диаграммы

Исходники PlantUML в `diagrams/`. Рендер:
- VS Code: расширение **PlantUML**
- Онлайн: https://www.plantuml.com/plantuml/uml/