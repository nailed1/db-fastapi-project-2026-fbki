-- =============================================================================
-- Migration 003: Role-based auth, reviews, requests, schedules
-- =============================================================================

-- Expand staff roles to include Manager and Admin explicitly
ALTER TABLE staff DROP CONSTRAINT IF EXISTS staff_role_check;
ALTER TABLE staff ADD CONSTRAINT staff_role_check
    CHECK (role IN ('Администратор','Менеджер','Горничная','Уборщик','Сантехник','Бармен','Техник'));

-- Tourist login accounts (linked to guests)
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    guest_id      INT REFERENCES guests(id) ON DELETE CASCADE,
    login         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Reviews (require confirmed booking)
CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    booking_id  INT NOT NULL REFERENCES bookings(id),
    guest_id    INT NOT NULL REFERENCES guests(id),
    hotel_id    INT NOT NULL REFERENCES hotels(id),
    rating      INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (booking_id)   -- one review per booking
);

-- Service requests: Admin → Manager
CREATE TABLE IF NOT EXISTS service_requests (
    id          SERIAL PRIMARY KEY,
    admin_id    INT NOT NULL REFERENCES staff(id),
    manager_id  INT REFERENCES staff(id),
    hotel_id    INT NOT NULL REFERENCES hotels(id),
    description TEXT NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'Новый'
        CHECK (status IN ('Новый','В работе','Выполнен')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Replenishment requests: Cleaner → Manager
CREATE TABLE IF NOT EXISTS replenishment_requests (
    id          SERIAL PRIMARY KEY,
    staff_id    INT NOT NULL REFERENCES staff(id),
    hotel_id    INT NOT NULL REFERENCES hotels(id),
    item_name   VARCHAR(200) NOT NULL,
    quantity    INT NOT NULL DEFAULT 1,
    unit        VARCHAR(50) DEFAULT 'шт',
    status      VARCHAR(20) NOT NULL DEFAULT 'Новый'
        CHECK (status IN ('Новый','Одобрен','Отклонён','Выполнен')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Staff schedules
CREATE TABLE IF NOT EXISTS staff_schedules (
    id         SERIAL PRIMARY KEY,
    staff_id   INT NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    work_date  DATE NOT NULL,
    shift      VARCHAR(20) NOT NULL DEFAULT 'День'
        CHECK (shift IN ('Утро','День','Вечер','Ночь')),
    note       TEXT,
    UNIQUE (staff_id, work_date)
);

-- Add manager_id to staff for hierarchy
ALTER TABLE staff ADD COLUMN IF NOT EXISTS manager_id INT REFERENCES staff(id);

-- Update existing demo staff roles for RBAC demo
-- (плейсхолдеры паролей заменить через make seed или admin UI)
UPDATE staff SET role = 'Менеджер'      WHERE login = 'admin1';
UPDATE staff SET role = 'Администратор' WHERE login = 'admin2';
UPDATE staff SET role = 'Уборщик'       WHERE login = 'cleaner1';
UPDATE staff SET role = 'Уборщик'       WHERE login = 'cleaner2';
UPDATE staff SET role = 'Уборщик'       WHERE login = 'cleaner3';
UPDATE staff SET role = 'Менеджер'      WHERE login = 'admin3';

-- Demo tourist user (password: tourist123)
INSERT INTO users (guest_id, login, password_hash)
SELECT id, 'tourist1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMaJobMDKMqBkkWiHpJbDPsWm6'
FROM guests WHERE passport = '4500 123456'
ON CONFLICT DO NOTHING;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_service_req_hotel   ON service_requests(hotel_id);
CREATE INDEX IF NOT EXISTS idx_replenish_staff     ON replenishment_requests(staff_id);
CREATE INDEX IF NOT EXISTS idx_schedules_staff     ON staff_schedules(staff_id, work_date);
CREATE INDEX IF NOT EXISTS idx_reviews_hotel       ON reviews(hotel_id);
