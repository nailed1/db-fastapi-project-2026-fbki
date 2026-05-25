-- 005_payment_status.sql
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20)
    NOT NULL DEFAULT 'Не оплачено'
    CHECK (payment_status IN ('Не оплачено', 'Оплачено', 'Возврат'));