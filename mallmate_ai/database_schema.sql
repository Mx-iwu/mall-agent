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

-- 5. stores table
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    floor TEXT NOT NULL,
    category TEXT NOT NULL,
    products TEXT,
    price_range TEXT,
    notes TEXT
);

-- 6. dining table
CREATE TABLE IF NOT EXISTS dining (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    floor TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    dishes TEXT,
    price_range TEXT,
    seating INTEGER,
    wait_time TEXT,
    rating DECIMAL(2,1),
    category TEXT NOT NULL
);

-- --- Massive Data Population ---

-- Fashion & Accessories (G, 1)
INSERT INTO stores (name, floor, category, products, price_range, notes) VALUES 
('Zara', 'G', 'Fashion', 'Dresses, jeans, shoes', 'NG₦8,000-45,000', '20% student discount'),
('H&M', 'G', 'Fashion', 'T-shirts, basics, kids', 'NG₦3,500-25,000', 'Buy 2 get 1 free tees'),
('Lumber Jacket', 'G', 'Fashion', 'Hoodies, joggers', 'NG₦7,000-28,000', 'Local Nigerian brands'),
('Shabby Chic', 'G', 'Fashion', 'Evening dresses, bags', 'NG₦12,000-55,000', 'Custom tailoring available'),
('Polo', '1', 'Fashion', 'Shirts, trousers, suits', 'NG₦15,000-75,000', 'Made-to-measure'),
('Forever 21', 'G', 'Fashion', 'Trendy outfits, accessories', 'NG₦4,000-20,000', 'Frequent flash sales'),
('Mango', 'G', 'Fashion', 'Workwear, outerwear', 'NG₦18,000-65,000', 'Outlet section 30% off'),
('Mr Price', 'G', 'Fashion', 'Complete outfits', 'NG₦2,000-12,000', 'Family bundles'),
('Next', '1', 'Fashion', 'Kids and maternity', 'NG₦5,000-30,000', 'School uniforms'),
('Bata', 'G', 'Fashion', 'Everyday shoes', 'NG₦3,000-15,000', 'Durable Nigerian favorites'),
('Redtag', 'G', 'Fashion', 'Abayas, hijabs', 'NG₦6,000-25,000', 'Prayer outfits'),
('Fisherman', '1', 'Accessories', 'Watches, belts, wallets', 'NG₦2,500-18,000', 'Engraving service'),
('Ray-Ban', '1', 'Accessories', 'Designer eyewear', 'NG₦25,000-120,000', 'Eye test service'),
('Swarovski', '1', 'Accessories', 'Crystal accessories', 'NG₦8,000-80,000', 'Gift wrapping'),
('Lovisa', 'G', 'Accessories', 'Fashion jewelry', 'NG₦1,500-12,000', '2 for NG₦5,000'),
('Milan''s', '1', 'Fashion', 'Bridal Wear', 'NG₦50,000-250,000', 'By appointment'),
('Aldo', '1', 'Fashion', 'Formal shoes, sandals', 'NG₦9,000-35,000', 'Leather maintenance kit'),
('Charles & Keith', '1', 'Fashion', 'Heels, handbags', 'NG₦10,000-40,000', 'Buy shoes get bag 50% off');

-- Sportswear (Floor 1)
INSERT INTO stores (name, floor, category, products, price_range, notes) VALUES 
('Nike', '1', 'Sports', 'Sneakers, sportswear', 'NG₦18,000-65,000', 'Nike Air Max 20% off'),
('Adidas', '1', 'Sports', 'Running gear, tracksuits', 'NG₦15,000-55,000', 'Predator boots launch'),
('Puma', '1', 'Sports', 'Casual sportswear', 'NG₦12,000-45,000', 'Football kits available'),
('Under Armour', '1', 'Sports', 'Performance wear', 'NG₦20,000-60,000', 'HeatGear summer collection'),
('Mountain Warehouse', '2', 'Sports', 'Outdoor gear', 'NG₦10,000-40,000', 'Hiking boots 25% off'),
('Decathlon', '1', 'Sports', 'All sports equipment', 'NG₦5,000-80,000', 'Bike service center'),
('Sports Direct', '1', 'Sports', 'Budget sportswear', 'NG₦4,000-25,000', 'Clearance sale'),
('Rebel Sports', '1', 'Sports', 'Team uniforms', 'NG₦8,000-35,000', 'Custom printing'),
('Foot Locker', '1', 'Sports', 'Premium sneakers', 'NG₦25,000-90,000', 'Limited editions'),
('Gym Shark', '1', 'Sports', 'Fitness apparel', 'NG₦12,000-40,000', 'Gym bags free with purchase');

-- Electronics (Floor 2)
INSERT INTO stores (name, floor, category, products, price_range, notes) VALUES 
('Samsung Store', '2', 'Electronics', 'Galaxy S25, QLED TVs', 'NG₦85,000-1,200,000', 'Official service center'),
('Slot Systems', '2', 'Electronics', 'Phones/Accessories', 'NG₦45,000-950,000', 'Trade-in available'),
('Hisense', '2', 'Electronics', 'Fridges, ACs', 'NG₦150,000-850,000', 'Home appliances'),
('LG', '2', 'Electronics', 'OLED TVs, washers', 'NG₦120,000-1,500,000', 'Latest tech display'),
('Tecno', '2', 'Electronics', 'Budget Smartphones', 'NG₦35,000-120,000', 'Local favorite'),
('Infinix', '2', 'Electronics', 'Gaming Phones', 'NG₦40,000-140,000', 'Note, Zero series'),
('Game', '2', 'Electronics', 'Consoles, Accessories', 'NG₦450,000-950,000', 'PS5, Xbox in stock'),
('iStore', '2', 'Electronics', 'Apple Products', 'NG₦650,000-2,500,000', 'Authorized Apple Reseller'),
('Soundcore', '2', 'Electronics', 'Audio Gear', 'NG₦15,000-85,000', 'Wireless speakers'),
('HP', '2', 'Electronics', 'Laptops', 'NG₦280,000-1,200,000', 'Pavilion, Omen gaming'),
('Dell', '2', 'Electronics', 'Business Laptops', 'NG₦450,000-1,800,000', 'XPS, Latitude series'),
('Sony', '2', 'Electronics', 'Cameras/PlayStation', 'NG₦750,000-2,200,000', 'Alpha cameras');

-- Dining - Food Court (Floor 1)
INSERT INTO dining (name, floor, cuisine, dishes, price_range, seating, wait_time, rating, category) VALUES 
('Dragon Wok', '1', 'Chinese', 'Fried rice, dim sum', 'NG₦1,200-3,500', 120, '5-10 min', 4.4, 'Food Court'),
('Pizza Hub', '1', 'Italian', 'Margherita pizza', 'NG₦1,800-4,200', 80, '8-12 min', 4.3, 'Food Court'),
('Sushi Bar', '1', 'Japanese', 'California rolls, ramen', 'NG₦2,000-5,000', 60, '10-15 min', 4.6, 'Food Court'),
('Chicken Republic', '1', 'Fast Food', 'Spicy wings, rice bowl', 'NG₦900-2,500', 100, '3-7 min', 4.2, 'Food Court'),
('Fish Bar', '1', 'Local', 'Grilled tilapia', 'NG₦2,200-4,800', 70, '10-15 min', 4.5, 'Food Court'),
('Thai Express', '1', 'Thai', 'Pad Thai, green curry', 'NG₦1,800-4,000', 50, '8-12 min', 4.3, 'Food Court'),
('Shawarma Plus', '1', 'Middle Eastern', 'Chicken shawarma', 'NG₦800-2,200', 90, '4-8 min', 4.1, 'Food Court'),
('Moi Moi Express', '1', 'Nigerian', 'Moi moi, akara', 'NG₦500-1,500', 40, '2-5 min', 4.0, 'Food Court'),
('Ice Cream World', '1', 'Desserts', 'Sundae, milkshakes', 'NG₦700-2,000', 30, '1-3 min', 4.4, 'Food Court'),
('Juice Bar', '1', 'Fresh Juices', 'Smoothies, pineapple', 'NG₦800-2,500', 25, '2-4 min', 4.5, 'Food Court');

-- Premium Dining (Floor 3)
INSERT INTO dining (name, floor, cuisine, dishes, price_range, seating, wait_time, rating, category) VALUES 
('Ocean Basket', '3', 'Seafood', 'Platter for two', 'NG₦8,000-25,000', 100, '15-25 min', 4.7, 'Premium'),
('The Grill House', '3', 'Steakhouse', 'T-bone steak', 'NG₦10,000-35,000', 80, '20-30 min', 4.6, 'Premium'),
('Mama Cass', '3', 'Nigerian', 'Pounded yam, Egusi', 'NG₦6,000-18,000', 120, '10-15 min', 4.5, 'Premium'),
('Nando''s', '3', 'Peri-Peri Chicken', 'Quarter chicken', 'NG₦3,500-9,000', 90, '10-15 min', 4.4, 'Premium'),
('California Pizza Kitchen', '3', 'Californian', 'BBQ Chicken Pizza', 'NG₦4,500-12,000', 70, '12-18 min', 4.3, 'Premium');

-- Quick Service (Ground Floor)
INSERT INTO dining (name, floor, cuisine, dishes, price_range, seating, wait_time, rating, category) VALUES 
('Domino''s Pizza', 'G', 'Pizza', 'Meat Lovers', 'NG₦2,500-6,000', 40, '10-15 min', 4.2, 'Quick Service'),
('KFC', 'G', 'Fried Chicken', 'Zinger Burger', 'NG₦1,500-4,000', 60, '5-10 min', 4.1, 'Quick Service'),
('Spar Express', 'G', 'Sandwiches', 'Club Sandwich', 'NG₦800-2,200', 20, '2-5 min', 4.0, 'Quick Service'),
('Coffee Republic', 'G', 'Coffee', 'Cappuccino', 'NG₦1,200-3,500', 30, '3-5 min', 4.4, 'Quick Service');
