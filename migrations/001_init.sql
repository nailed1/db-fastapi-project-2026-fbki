-- =============================================================================
-- Migration 001: Initial schema
-- Hotel booking management system
-- =============================================================================

-- Hotels (отделения)
CREATE TABLE IF NOT EXISTS hotels (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    address       TEXT NOT NULL,
    director_name VARCHAR(200) NOT NULL,
    overbooking_limit INT NOT NULL DEFAULT 10
);

-- Room categories (категории номеров)
CREATE TABLE IF NOT EXISTS room_categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,   -- Standard, Lux, President
    base_price  NUMERIC(10, 2) NOT NULL,
    capacity    INT NOT NULL DEFAULT 2
);

-- Rooms (номера)
CREATE TABLE IF NOT EXISTS rooms (
    id             SERIAL PRIMARY KEY,
    hotel_id       INT NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    category_id    INT NOT NULL REFERENCES room_categories(id),
    room_number    INT NOT NULL,
    cleaning_status VARCHAR(20) NOT NULL DEFAULT 'Clean'
        CHECK (cleaning_status IN ('Clean', 'Dirty', 'Cleaning')),
    room_condition  VARCHAR(20) NOT NULL DEFAULT 'Исправно'
        CHECK (room_condition IN ('Исправно', 'Ремонт')),
    UNIQUE (hotel_id, room_number)
);

-- Guests (клиенты)
CREATE TABLE IF NOT EXISTS guests (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(300) NOT NULL,
    passport        VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(30),
    email           VARCHAR(200),
    loyalty_tier    VARCHAR(20) NOT NULL DEFAULT 'Silver'
        CHECK (loyalty_tier IN ('Silver', 'Gold', 'Platinum')),
    total_spend     NUMERIC(12, 2) NOT NULL DEFAULT 0
);

-- Guest preferences reference (справочник предпочтений)
CREATE TABLE IF NOT EXISTS guest_preferences (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE  -- Без ковролина, Высокий этаж, Вид на море
);

-- Guest ↔ preference many-to-many
CREATE TABLE IF NOT EXISTS guest_pref_link (
    guest_id      INT NOT NULL REFERENCES guests(id) ON DELETE CASCADE,
    preference_id INT NOT NULL REFERENCES guest_preferences(id) ON DELETE CASCADE,
    PRIMARY KEY (guest_id, preference_id)
);

-- Staff (персонал)
CREATE TABLE IF NOT EXISTS staff (
    id           SERIAL PRIMARY KEY,
    hotel_id     INT NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    full_name    VARCHAR(300) NOT NULL,
    role         VARCHAR(50) NOT NULL
        CHECK (role IN ('Администратор', 'Горничная', 'Техник')),
    login        VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL
);

-- Bookings (бронирование)
CREATE TABLE IF NOT EXISTS bookings (
    id           SERIAL PRIMARY KEY,
    guest_id     INT NOT NULL REFERENCES guests(id),
    room_id      INT NOT NULL REFERENCES rooms(id),
    staff_id     INT REFERENCES staff(id),
    check_in     DATE NOT NULL,
    check_out    DATE NOT NULL,
    total_price  NUMERIC(12, 2) NOT NULL DEFAULT 0,
    status       VARCHAR(20) NOT NULL DEFAULT 'Подтверждено'
        CHECK (status IN ('Подтверждено', 'Отменено', 'Завершено')),
    CHECK (check_out > check_in)
);

-- Services (услуги)
CREATE TABLE IF NOT EXISTS services (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,  -- Завтрак, SPA, Пакет Романтик
    price      NUMERIC(10, 2) NOT NULL,
    is_package BOOLEAN NOT NULL DEFAULT FALSE
);

-- Service orders (заказы услуг)
CREATE TABLE IF NOT EXISTS service_orders (
    id          SERIAL PRIMARY KEY,
    booking_id  INT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    service_id  INT NOT NULL REFERENCES services(id),
    quantity    INT NOT NULL DEFAULT 1,
    ordered_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Audit log (лог аудита)
CREATE TABLE IF NOT EXISTS audit_log (
    id           SERIAL PRIMARY KEY,
    staff_id     INT REFERENCES staff(id),
    table_name   VARCHAR(100) NOT NULL,
    old_value    TEXT,
    new_value    TEXT,
    changed_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- Indexes for common queries
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_rooms_hotel    ON rooms(hotel_id);
CREATE INDEX IF NOT EXISTS idx_rooms_category ON rooms(category_id);
CREATE INDEX IF NOT EXISTS idx_bookings_guest ON bookings(guest_id);
CREATE INDEX IF NOT EXISTS idx_bookings_room  ON bookings(room_id);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(check_in, check_out);
CREATE INDEX IF NOT EXISTS idx_audit_staff    ON audit_log(staff_id);
CREATE INDEX IF NOT EXISTS idx_audit_table    ON audit_log(table_name);
