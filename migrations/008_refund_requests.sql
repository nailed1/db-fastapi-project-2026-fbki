CREATE TABLE IF NOT EXISTS refund_requests (
    id SERIAL PRIMARY KEY,
    booking_id INT REFERENCES bookings(id),
    guest_id INT REFERENCES guests(id),
    amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Новая'
        CHECK (status IN ('Новая', 'Одобрена', 'Отклонена')),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    manager_id INT REFERENCES staff(id)
);