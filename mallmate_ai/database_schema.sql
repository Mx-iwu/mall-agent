-- Part C: Required Tables in Supabase

-- 1. deals table
CREATE TABLE IF NOT EXISTS deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_name TEXT NOT NULL,
    offer TEXT,
    discount TEXT,
    valid_until DATE
);

-- 2. events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name TEXT NOT NULL,
    location TEXT,
    time TEXT,
    description TEXT
);

-- 3. users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    last_activity TEXT,
    last_visit TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. customer_orders table
CREATE TABLE IF NOT EXISTS customer_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    item_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sample Data (Optional)
-- INSERT INTO deals (store_name, offer, discount, valid_until) VALUES ('Nike', '20% off Air Max', '20%', '2026-12-31');
-- INSERT INTO events (event_name, location, time, description) VALUES ('Predator boots launch', 'Adidas Store', '5:00 PM', 'Launch event for new Predator boots');
