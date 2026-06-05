-- =============================================================================
-- Migration 010: Reviews table
-- =============================================================================

CREATE TABLE IF NOT EXISTS reviews (
    id         SERIAL PRIMARY KEY,
    booking_id INT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    guest_id   INT NOT NULL REFERENCES guests(id),
    hotel_id   INT NOT NULL REFERENCES hotels(id),
    rating     INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment    TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (booking_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_hotel ON reviews(hotel_id);
CREATE INDEX IF NOT EXISTS idx_reviews_guest ON reviews(guest_id);
