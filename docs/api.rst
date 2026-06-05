API Reference
=============

Полный список эндпоинтов **не дублируется** в Sphinx — он генерируется из кода
FastAPI (OpenAPI) при запущенном сервере.

Источник правды
---------------

После ``make dev`` откройте:

* **Swagger UI** — http://localhost:8000/docs
* **ReDoc** — http://localhost:8000/redoc
* **OpenAPI JSON** — http://localhost:8000/openapi.json

Там актуальные методы, параметры и схемы ответов для всех роутеров
(``/auth``, ``/bookings``, ``/portal/*``, webhook оплаты и т.д.).

Sphinx в этом проекте
---------------------

* :doc:`overview` — обзор и роли
* :doc:`hotel_utils` — утилитная библиотека (automodule из кода)
* :doc:`diagrams` — диаграммы
