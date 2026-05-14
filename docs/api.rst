API Reference
=============

FastAPI автоматически генерирует интерактивную документацию по адресу
``http://localhost:8000/docs`` (Swagger UI) и ``/redoc``.

Маршруты
--------

Бронирования
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Метод
     - URL
     - Описание
   * - GET
     - ``/bookings/``
     - Список всех бронирований
   * - GET
     - ``/bookings/new``
     - Форма создания бронирования
   * - POST
     - ``/bookings/``
     - Создать бронирование
   * - GET
     - ``/bookings/available-rooms``
     - Доступные номера (query: hotel_id, check_in, check_out)
   * - POST
     - ``/bookings/{id}/cancel``
     - Отменить бронирование

Гости
~~~~~

.. list-table::
   :header-rows: 1

   * - Метод
     - URL
     - Описание
   * - GET
     - ``/guests/``
     - Список гостей
   * - GET
     - ``/guests/new``
     - Форма добавления гостя
   * - POST
     - ``/guests/``
     - Создать гостя

Номера
~~~~~~

.. list-table::
   :header-rows: 1

   * - Метод
     - URL
     - Описание
   * - GET
     - ``/rooms/``
     - Список номеров с фильтрами
   * - POST
     - ``/rooms/{id}/cleaning``
     - Обновить статус уборки

Менеджер
~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Метод
     - URL
     - Описание
   * - GET
     - ``/manager/dashboard``
     - Дашборд со статистикой
   * - GET
     - ``/manager/cleaning``
     - Задания горничным
