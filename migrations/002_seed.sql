-- =============================================================================
-- Migration 002: Seed data (15-30 records per relevant table)
-- =============================================================================

-- Hotels
INSERT INTO hotels (name, address, director_name, overbooking_limit) VALUES
    ('Гранд Отель Центр',      'ул. Ленина, 1, Москва',           'Петров Иван Сергеевич',    10),
    ('Бизнес Отель Аэропорт',  'Аэропортовое шоссе, 5, Москва',   'Сидорова Анна Петровна',   15),
    ('Отель у Моря',           'Набережная, 12, Сочи',             'Козлов Дмитрий Андреевич', 5)
ON CONFLICT DO NOTHING;

-- Room categories
INSERT INTO room_categories (name, base_price, capacity) VALUES
    ('Standard',   3500.00, 2),
    ('Lux',        7000.00, 2),
    ('President', 15000.00, 4),
    ('Economy',    2000.00, 1)
ON CONFLICT DO NOTHING;

-- Rooms
INSERT INTO rooms (hotel_id, category_id, room_number, cleaning_status, room_condition) VALUES
    -- Гранд Отель Центр
    (1, 1, 101, 'Clean',    'Исправно'),
    (1, 1, 102, 'Dirty',    'Исправно'),
    (1, 2, 201, 'Clean',    'Исправно'),
    (1, 2, 202, 'Cleaning', 'Исправно'),
    (1, 3, 301, 'Clean',    'Исправно'),
    (1, 4, 001, 'Clean',    'Ремонт'),
    -- Бизнес Отель Аэропорт
    (2, 1, 110, 'Clean',    'Исправно'),
    (2, 1, 111, 'Clean',    'Исправно'),
    (2, 2, 210, 'Dirty',    'Исправно'),
    (2, 3, 310, 'Clean',    'Исправно'),
    -- Отель у Моря
    (3, 1, 101, 'Clean',    'Исправно'),
    (3, 2, 201, 'Clean',    'Исправно'),
    (3, 3, 301, 'Clean',    'Исправно')
ON CONFLICT DO NOTHING;

-- Guest preferences
INSERT INTO guest_preferences (name) VALUES
    ('Без ковролина'),
    ('Высокий этаж'),
    ('Вид на море'),
    ('Тихий номер'),
    ('Детская кроватка'),
    ('Гипоаллергенное постельное')
ON CONFLICT DO NOTHING;

-- Guests
INSERT INTO guests (full_name, passport, phone, email, loyalty_tier, total_spend) VALUES
    ('Иванов Алексей Николаевич',   '4500 123456', '+7-900-111-2233', 'ivanov@mail.ru',    'Gold',     45000.00),
    ('Смирнова Ольга Викторовна',   '4501 654321', '+7-900-222-3344', 'smirnova@mail.ru',  'Silver',   12000.00),
    ('Козлов Дмитрий Петрович',     '4502 111222', '+7-900-333-4455', 'kozlov@gmail.com',  'Platinum', 120000.00),
    ('Новикова Екатерина Ивановна', '4503 333444', '+7-900-444-5566', 'novikova@yandex.ru','Silver',    5000.00),
    ('Морозов Сергей Андреевич',    '4504 555666', '+7-900-555-6677', 'morozov@mail.ru',   'Gold',     55000.00),
    ('Васильева Наталья Сергеевна', '4505 777888', '+7-900-666-7788', 'vasileva@inbox.ru', 'Silver',    8000.00),
    ('Павлов Михаил Юрьевич',       '4506 999000', '+7-900-777-8899', 'pavlov@gmail.com',  'Platinum', 200000.00),
    ('Захарова Анастасия Олеговна', '4507 121314', '+7-900-888-9900', 'zaharova@mail.ru',  'Silver',    2000.00),
    ('Степанов Виктор Николаевич',  '4508 151617', '+7-901-100-2000', 'stepanov@yandex.ru','Gold',     38000.00),
    ('Федорова Мария Александровна','4509 181920', '+7-901-200-3000', 'fedorova@gmail.com','Silver',   15000.00)
ON CONFLICT DO NOTHING;

-- Guest ↔ preference links
INSERT INTO guest_pref_link (guest_id, preference_id) VALUES
    (1, 2), (1, 4),
    (2, 1),
    (3, 3), (3, 2),
    (4, 5),
    (5, 4),
    (7, 1), (7, 6)
ON CONFLICT DO NOTHING;

-- Staff (password_hash is bcrypt of "password123" for demo purposes)
INSERT INTO staff (hotel_id, full_name, role, login, password_hash) VALUES
    (1, 'Николаева Юлия Сергеевна',  'Администратор', 'admin1',   '$2b$12$placeholder_hash_admin1'),
    (1, 'Громова Светлана Ивановна',  'Горничная',     'cleaner1', '$2b$12$placeholder_hash_cleaner1'),
    (1, 'Борисов Павел Николаевич',   'Техник',        'tech1',    '$2b$12$placeholder_hash_tech1'),
    (2, 'Орлова Ирина Петровна',      'Администратор', 'admin2',   '$2b$12$placeholder_hash_admin2'),
    (2, 'Зайцева Алина Олеговна',     'Горничная',     'cleaner2', '$2b$12$placeholder_hash_cleaner2'),
    (3, 'Лебедев Константин Юрьевич','Администратор', 'admin3',   '$2b$12$placeholder_hash_admin3'),
    (3, 'Тихонова Валерия Андреевна', 'Горничная',     'cleaner3', '$2b$12$placeholder_hash_cleaner3')
ON CONFLICT DO NOTHING;

-- Bookings
INSERT INTO bookings (guest_id, room_id, staff_id, check_in, check_out, total_price, status) VALUES
    (1,  3, 1, '2025-05-01', '2025-05-05', 32760.00, 'Завершено'),
    (2,  1, 1, '2025-05-10', '2025-05-12', 7000.00,  'Завершено'),
    (3,  5, 1, '2025-06-01', '2025-06-07', 122850.00,'Подтверждено'),
    (4,  2, 1, '2025-06-15', '2025-06-17', 9100.00,  'Подтверждено'),
    (5,  7, 4, '2025-07-01', '2025-07-10', 49140.00, 'Подтверждено'),
    (6,  8, 4, '2025-07-05', '2025-07-08', 13650.00, 'Подтверждено'),
    (7,  9, 4, '2025-08-01', '2025-08-07', 55692.00, 'Подтверждено'),
    (8, 11, 6, '2025-08-10', '2025-08-14', 18200.00, 'Подтверждено'),
    (9,  3, 1, '2025-04-01', '2025-04-03', 11900.00, 'Завершено'),
    (10, 1, 1, '2025-04-20', '2025-04-22',  5950.00, 'Завершено'),
    (1,  5, 1, '2025-09-10', '2025-09-15', 75000.00, 'Подтверждено'),
    (3, 13, 6, '2025-10-01', '2025-10-05', 60000.00, 'Подтверждено')
ON CONFLICT DO NOTHING;

-- Services
INSERT INTO services (name, price, is_package) VALUES
    ('Завтрак',        500.00,  FALSE),
    ('Обед',           800.00,  FALSE),
    ('Ужин',           900.00,  FALSE),
    ('SPA',           3000.00,  FALSE),
    ('Трансфер',      2000.00,  FALSE),
    ('Пакет Романтик',8000.00,  TRUE),
    ('Пакет Семейный',6000.00,  TRUE),
    ('Уборка',         300.00,  FALSE),
    ('Прачечная',      200.00,  FALSE)
ON CONFLICT DO NOTHING;

-- Service orders
INSERT INTO service_orders (booking_id, service_id, quantity, ordered_at) VALUES
    (1, 1, 4, '2025-05-01 09:00:00'),
    (1, 4, 1, '2025-05-02 14:00:00'),
    (2, 1, 2, '2025-05-10 09:00:00'),
    (3, 6, 1, '2025-06-01 10:00:00'),
    (3, 1, 7, '2025-06-02 09:00:00'),
    (4, 1, 2, '2025-06-15 09:00:00'),
    (5, 5, 1, '2025-07-01 08:00:00'),
    (5, 1, 9, '2025-07-01 09:00:00'),
    (7, 4, 2, '2025-08-02 15:00:00'),
    (7, 1, 6, '2025-08-01 09:00:00')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Typical SQL queries for the informatics report
-- =============================================================================

-- 1. Simple: All confirmed bookings
-- SELECT b.id, g.full_name, h.name AS hotel, r.room_number, b.check_in, b.check_out
-- FROM bookings b
-- JOIN guests g ON g.id = b.guest_id
-- JOIN rooms r  ON r.id = b.room_id
-- JOIN hotels h ON h.id = r.hotel_id
-- WHERE b.status = 'Подтверждено';

-- 2. Calculated: Total revenue per hotel
-- SELECT h.name, SUM(b.total_price) AS revenue
-- FROM bookings b
-- JOIN rooms r  ON r.id = b.room_id
-- JOIN hotels h ON h.id = r.hotel_id
-- WHERE b.status != 'Отменено'
-- GROUP BY h.name ORDER BY revenue DESC;

-- 3. Parametric: Rooms available for a date range (no overlapping confirmed bookings)
-- SELECT r.id, r.room_number, rc.name AS category, rc.base_price
-- FROM rooms r
-- JOIN room_categories rc ON rc.id = r.category_id
-- WHERE r.hotel_id = :hotel_id
--   AND r.room_condition = 'Исправно'
--   AND r.id NOT IN (
--       SELECT room_id FROM bookings
--       WHERE status = 'Подтверждено'
--         AND check_in  < :check_out
--         AND check_out > :check_in
--   );

-- 4. Top guests by spend
-- SELECT full_name, loyalty_tier, total_spend
-- FROM guests ORDER BY total_spend DESC LIMIT 10;

-- 5. Cleaning task list for staff
-- SELECT r.room_number, r.cleaning_status, h.name AS hotel
-- FROM rooms r
-- JOIN hotels h ON h.id = r.hotel_id
-- WHERE r.cleaning_status IN ('Dirty', 'Cleaning')
-- ORDER BY h.name, r.room_number;
