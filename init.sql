-- Initialize database schema for beauty booking system

-- Create table for available time slots
CREATE TABLE IF NOT EXISTS available_slots (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time_slot TIME NOT NULL,
    manicure_type VARCHAR(20) NOT NULL CHECK (manicure_type IN ('Classical', 'Japanese', 'Gel', 'Extensions')),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, time_slot, manicure_type)
);

-- Create table for bookings
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    booking_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    manicure_type VARCHAR(20) NOT NULL CHECK (manicure_type IN ('Classical', 'Japanese', 'Gel', 'Extensions')),
    date DATE NOT NULL,
    time_slot TIME,
    status VARCHAR(20) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_available_slots_date ON available_slots(date);
CREATE INDEX IF NOT EXISTS idx_available_slots_manicure_type ON available_slots(manicure_type);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_booking_id ON bookings(booking_id);

-- Insert initial available slots for the next 2 weeks (weekdays only)
-- This is a seed script - in production, you'd manage this differently
DO $$
DECLARE
    current_date DATE;
    time_slots TIME[] := ARRAY['10:00'::TIME, '12:00'::TIME, '14:00'::TIME, '16:00'::TIME, '18:00'::TIME];
    manicure_types VARCHAR[] := ARRAY['Classical', 'Japanese', 'Gel', 'Extensions'];
    slot_date DATE;
    slot_time TIME;
    m_type VARCHAR;
BEGIN
    FOR i IN 0..13 LOOP
        slot_date := CURRENT_DATE + i;
        -- Only weekdays (Monday = 1, Friday = 5)
        IF EXTRACT(DOW FROM slot_date) BETWEEN 1 AND 5 THEN
            FOREACH slot_time IN ARRAY time_slots LOOP
                FOREACH m_type IN ARRAY manicure_types LOOP
                    INSERT INTO available_slots (date, time_slot, manicure_type, is_available)
                    VALUES (slot_date, slot_time, m_type, TRUE)
                    ON CONFLICT (date, time_slot, manicure_type) DO NOTHING;
                END LOOP;
            END LOOP;
        END IF;
    END LOOP;
END $$;

