-- ====================================================================
-- TripNest — Smart Tourist Booking System - schema.sql
-- Run with: mysql -u root -p < schema.sql
-- Creates: database, 13 tables, 10 indexes, 2 triggers,
--          3 views, 1 stored procedure, seed data
-- ====================================================================

DROP DATABASE IF EXISTS tripnest_db;
CREATE DATABASE tripnest_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tripnest_db;

-- --------------------------------------------------------------------
-- 1. USERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE users (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    phone          VARCHAR(20),
    password_hash  VARCHAR(255) NOT NULL,
    role           ENUM('customer', 'admin') DEFAULT 'customer' NOT NULL,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 2. DESTINATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE destinations (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(100) NOT NULL,
    country           VARCHAR(100) NOT NULL DEFAULT 'India',
    region            VARCHAR(100) NOT NULL,
    category          VARCHAR(50) NOT NULL,
    description       TEXT NOT NULL,
    image_url         VARCHAR(500) NOT NULL,
    estimated_budget  DECIMAL(10, 2) NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dest_budget CHECK (estimated_budget >= 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 3. ATTRACTIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE attractions (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    destination_id       INT NOT NULL,
    name                 VARCHAR(150) NOT NULL,
    description          TEXT NOT NULL,
    entry_fee            DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    opening_information  VARCHAR(200),
    CONSTRAINT fk_attraction_dest FOREIGN KEY (destination_id) 
        REFERENCES destinations (id) ON DELETE CASCADE,
    CONSTRAINT chk_entry_fee CHECK (entry_fee >= 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 4. PACKAGES TABLE
-- --------------------------------------------------------------------
CREATE TABLE packages (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    destination_id    INT NOT NULL,
    name              VARCHAR(150) NOT NULL,
    description       TEXT NOT NULL,
    duration_days     INT NOT NULL,
    price_per_person  DECIMAL(10, 2) NOT NULL,
    inclusions        VARCHAR(500) NOT NULL,
    image_url         VARCHAR(500),
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_package_dest FOREIGN KEY (destination_id) 
        REFERENCES destinations (id) ON DELETE CASCADE,
    CONSTRAINT chk_package_days CHECK (duration_days > 0),
    CONSTRAINT chk_package_price CHECK (price_per_person >= 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 5. PACKAGE ITINERARIES TABLE
-- --------------------------------------------------------------------
CREATE TABLE package_itineraries (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    package_id   INT NOT NULL,
    day_number   INT NOT NULL,
    title        VARCHAR(150) NOT NULL,
    description  TEXT NOT NULL,
    CONSTRAINT fk_itinerary_pkg FOREIGN KEY (package_id) 
        REFERENCES packages (id) ON DELETE CASCADE,
    CONSTRAINT chk_itin_day CHECK (day_number > 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 6. HOTELS TABLE
-- --------------------------------------------------------------------
CREATE TABLE hotels (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    destination_id  INT NOT NULL,
    name            VARCHAR(150) NOT NULL,
    address         VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    amenities       VARCHAR(500) NOT NULL,
    rating          DECIMAL(3, 2) NOT NULL DEFAULT 4.50,
    image_url       VARCHAR(500),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hotel_dest FOREIGN KEY (destination_id) 
        REFERENCES destinations (id) ON DELETE CASCADE,
    CONSTRAINT chk_hotel_rating CHECK (rating >= 1.0 AND rating <= 5.0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 7. ROOMS TABLE
-- --------------------------------------------------------------------
CREATE TABLE rooms (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id         INT NOT NULL,
    room_type        VARCHAR(100) NOT NULL,
    capacity         INT NOT NULL DEFAULT 2,
    price_per_night  DECIMAL(10, 2) NOT NULL,
    total_rooms      INT NOT NULL DEFAULT 5,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_room_hotel FOREIGN KEY (hotel_id) 
        REFERENCES hotels (id) ON DELETE CASCADE,
    CONSTRAINT chk_room_capacity CHECK (capacity > 0),
    CONSTRAINT chk_room_price CHECK (price_per_night >= 0),
    CONSTRAINT chk_room_total CHECK (total_rooms >= 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 8. BOOKINGS TABLE
-- --------------------------------------------------------------------
CREATE TABLE bookings (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(30) NOT NULL UNIQUE,
    user_id           INT NOT NULL,
    package_id        INT NULL,
    room_id           INT NULL,
    check_in          DATE NOT NULL,
    check_out         DATE NOT NULL,
    number_of_guests  INT NOT NULL,
    total_amount      DECIMAL(10, 2) NOT NULL,
    booking_status    ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED') DEFAULT 'PENDING' NOT NULL,
    special_requests  TEXT,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_user FOREIGN KEY (user_id) 
        REFERENCES users (id),
    CONSTRAINT fk_booking_package FOREIGN KEY (package_id) 
        REFERENCES packages (id) ON DELETE SET NULL,
    CONSTRAINT fk_booking_room FOREIGN KEY (room_id) 
        REFERENCES rooms (id) ON DELETE SET NULL,
    CONSTRAINT chk_booking_dates CHECK (check_out > check_in),
    CONSTRAINT chk_booking_guests CHECK (number_of_guests > 0),
    CONSTRAINT chk_booking_amount CHECK (total_amount >= 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 9. PAYMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE payments (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    booking_id             INT NOT NULL UNIQUE,
    amount                 DECIMAL(10, 2) NOT NULL,
    payment_method         VARCHAR(50) NOT NULL,
    transaction_reference  VARCHAR(60) NOT NULL UNIQUE,
    payment_status         ENUM('PENDING', 'SUCCESS', 'FAILED') DEFAULT 'PENDING' NOT NULL,
    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id) 
        REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT chk_payment_amount CHECK (amount >= 0)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 10. REVIEWS TABLE
-- --------------------------------------------------------------------
CREATE TABLE reviews (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    destination_id  INT NULL,
    hotel_id        INT NULL,
    booking_id      INT NULL,
    rating          TINYINT NOT NULL,
    comment_text    TEXT NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_user FOREIGN KEY (user_id) 
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_review_dest FOREIGN KEY (destination_id) 
        REFERENCES destinations (id) ON DELETE SET NULL,
    CONSTRAINT fk_review_hotel FOREIGN KEY (hotel_id) 
        REFERENCES hotels (id) ON DELETE SET NULL,
    CONSTRAINT fk_review_booking FOREIGN KEY (booking_id) 
        REFERENCES bookings (id) ON DELETE SET NULL,
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 11. FAVOURITES TABLE
-- --------------------------------------------------------------------
CREATE TABLE favourites (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    destination_id  INT NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fav_user FOREIGN KEY (user_id) 
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_fav_dest FOREIGN KEY (destination_id) 
        REFERENCES destinations (id) ON DELETE CASCADE,
    CONSTRAINT uq_user_dest_fav UNIQUE (user_id, destination_id)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 12. BOOKING STATUS HISTORY (AUDIT TRAIL)
-- --------------------------------------------------------------------
CREATE TABLE booking_status_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL,
    old_status  VARCHAR(20),
    new_status  VARCHAR(20) NOT NULL,
    changed_by  INT NULL,
    changed_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks     VARCHAR(500),
    CONSTRAINT fk_bsh_booking FOREIGN KEY (booking_id) 
        REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_bsh_changer FOREIGN KEY (changed_by) 
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 13. ROOM RESERVATIONS (INVENTORY ALLOCATION)
-- --------------------------------------------------------------------
CREATE TABLE room_reservations (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    booking_id        INT NOT NULL,
    room_id           INT NOT NULL,
    reservation_date  DATE NOT NULL,
    status            ENUM('ACTIVE', 'RELEASED') DEFAULT 'ACTIVE' NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_res_booking FOREIGN KEY (booking_id) 
        REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_res_room FOREIGN KEY (room_id) 
        REFERENCES rooms (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- INDEXES FOR QUERY OPTIMIZATION
-- --------------------------------------------------------------------
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_dest_search ON destinations (name, region, category);
CREATE INDEX idx_hotel_search ON hotels (name, destination_id);
CREATE INDEX idx_package_search ON packages (name, destination_id);
CREATE INDEX idx_booking_ref ON bookings (booking_reference);
CREATE INDEX idx_booking_status ON bookings (user_id, booking_status);
CREATE INDEX idx_payments_ref ON payments (transaction_reference);
CREATE INDEX idx_payments_status ON payments (payment_status);
CREATE INDEX idx_room_res_date ON room_reservations (room_id, reservation_date, status);
CREATE INDEX idx_review_target ON reviews (destination_id, hotel_id);

-- --------------------------------------------------------------------
-- VIEWS
-- --------------------------------------------------------------------
CREATE OR REPLACE VIEW view_booking_summaries AS
SELECT 
    b.id AS booking_id,
    b.booking_reference,
    u.full_name AS customer_name,
    u.email AS customer_email,
    u.phone AS customer_phone,
    CASE 
        WHEN b.package_id IS NOT NULL THEN 'Package'
        WHEN b.room_id IS NOT NULL THEN 'Hotel Room'
        ELSE 'Other'
    END AS booking_type,
    COALESCE(p.name, CONCAT(h.name, ' - ', r.room_type)) AS item_name,
    COALESCE(d_pkg.name, d_htl.name) AS destination_name,
    b.check_in,
    b.check_out,
    DATEDIFF(b.check_out, b.check_in) AS duration_days,
    b.number_of_guests,
    b.total_amount,
    b.booking_status,
    pay.payment_status,
    pay.payment_method,
    pay.transaction_reference,
    b.created_at
FROM bookings b
INNER JOIN users u ON b.user_id = u.id
LEFT JOIN packages p ON b.package_id = p.id
LEFT JOIN destinations d_pkg ON p.destination_id = d_pkg.id
LEFT JOIN rooms r ON b.room_id = r.id
LEFT JOIN hotels h ON r.hotel_id = h.id
LEFT JOIN destinations d_htl ON h.destination_id = d_htl.id
LEFT JOIN payments pay ON b.id = pay.booking_id;

CREATE OR REPLACE VIEW view_destination_stats AS
SELECT 
    d.id AS destination_id,
    d.name AS destination_name,
    d.region,
    d.category,
    d.estimated_budget,
    COUNT(DISTINCT p.id) AS total_packages,
    COUNT(DISTINCT h.id) AS total_hotels,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(CASE WHEN b.booking_status = 'CONFIRMED' THEN b.total_amount ELSE 0 END), 0) AS total_revenue
FROM destinations d
LEFT JOIN packages p ON d.id = p.destination_id
LEFT JOIN hotels h ON d.id = h.destination_id
LEFT JOIN bookings b ON (b.package_id = p.id)
GROUP BY d.id, d.name, d.region, d.category, d.estimated_budget;

-- --------------------------------------------------------------------
-- TRIGGER: Audit status change
-- --------------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER trg_booking_status_audit
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF OLD.booking_status <> NEW.booking_status THEN
        INSERT INTO booking_status_history (
            booking_id, old_status, new_status, changed_by, changed_at, remarks
        ) VALUES (
            OLD.id, OLD.booking_status, NEW.booking_status, NEW.user_id, NOW(), 'Updated via Database Trigger'
        );
    END IF;
END$$
DELIMITER ;

-- --------------------------------------------------------------------
-- SEED DATA (INDIAN TOURISM)
-- --------------------------------------------------------------------
-- Users
INSERT INTO users (full_name, email, phone, password_hash, role)
VALUES 
('TripNest Administrator', 'admin@tripnest.com', '+91 9876543210', 'pbkdf2:sha256:1000000$dummyhash$admin', 'admin'),
('Priya Sharma', 'priya.sharma@example.com', '+91 9811122334', 'pbkdf2:sha256:1000000$dummyhash$customer', 'customer');

-- Destinations
INSERT INTO destinations (name, country, region, category, description, image_url, estimated_budget)
VALUES 
('Ooty', 'India', 'Tamil Nadu', 'Hill Station', 'Queen of Hill Stations in the Nilgiri Mountains with tea plantations and lake.', 'https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80', 15000.00),
('Munnar', 'India', 'Kerala', 'Hill Station', 'South Indias tea capital with rolling green hills and Eravikulam National Park.', 'https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1200&q=80', 16500.00),
('Goa', 'India', 'Goa', 'Beach', 'Tropical coastal paradise with golden sand beaches, Portuguese churches, and night markets.', 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80', 22000.00),
('Jaipur', 'India', 'Rajasthan', 'Heritage', 'The royal Pink City with Amber Fort, Hawa Mahal, and Rajput palaces.', 'https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80', 19000.00),
('Mysuru', 'India', 'Karnataka', 'Heritage', 'Cultural capital of Karnataka, celebrated for its spectacular Mysore Palace and royal silk.', 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80', 12000.00),
('Manali', 'India', 'Himachal Pradesh', 'Hill Station', 'Himalayan paradise surrounded by snow-capped peaks, pine forests, and adventure sports.', 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80', 21000.00),
('Kodaikanal', 'India', 'Tamil Nadu', 'Hill Station', 'Princess of Hill Stations with misty cliffs, serene Kodai lake, and cool forest trails.', 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80', 14000.00),
('Alleppey (Alappuzha)', 'India', 'Kerala', 'Backwaters', 'Venice of the East, famed for palm-fringed backwaters and thatched houseboats.', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80', 18000.00);

-- Attractions
INSERT INTO attractions (destination_id, name, description, entry_fee, opening_information)
VALUES 
(1, 'Government Botanical Garden', 'Sprawling 55-acre terraced garden featuring exotic flora.', 50.00, '07:00 AM - 06:30 PM'),
(1, 'Doddabetta Peak', 'Highest peak in the Nilgiris with panoramic telescope house view.', 30.00, '09:00 AM - 06:00 PM'),
(5, 'Mysore Palace', 'Illuminated royal palace of the Wadiyar dynasty.', 100.00, '10:00 AM - 05:30 PM');

-- Packages
INSERT INTO packages (destination_id, name, description, duration_days, price_per_person, inclusions)
VALUES 
(1, 'Enchanting Nilgiris Explorer', 'Complete 4-day tour of Ooty, Coonoor tea estates, and Toy Train ride.', 4, 13999.00, '4-Star Hotel, Breakfast, Toy Train Pass, Sightseeing Cab'),
(2, 'Emerald Munnar Tea Odyssey', 'Plantation villa stay, Eravikulam safari, and tea museum tour.', 4, 14500.00, 'Villa Stay, Meals, Wildlife Safari, Spice Tour');

-- Hotels & Rooms
INSERT INTO hotels (destination_id, name, address, description, amenities, rating)
VALUES 
(1, 'Savoy - IHCL SeleQtions Ooty', '77 Sylks Road, Ooty', 'Colonial heritage luxury hotel with garden fireplaces and fine dining.', 'WiFi, Fireplace, Spa, Restaurant, Valet', 4.80),
(5, 'Radisson Blu Plaza Hotel Mysore', 'MG Road, Mysuru', 'Luxury property overlooking Chamundi Hills with pool and spa.', 'Pool, Spa, WiFi, Gymnasium, Restaurant', 4.70);

INSERT INTO rooms (hotel_id, room_type, capacity, price_per_night, total_rooms)
VALUES 
(1, 'Colonial Heritage Room', 2, 8500.00, 6),
(1, 'Executive Valley Suite', 3, 14500.00, 4),
(2, 'Deluxe Hill View Room', 2, 6500.00, 10);

-- Bookings & Payments
INSERT INTO bookings (booking_reference, user_id, package_id, check_in, check_out, number_of_guests, total_amount, booking_status)
VALUES 
('TN-2026-SQL001', 2, 1, '2026-11-15', '2026-11-19', 2, 27998.00, 'CONFIRMED');

INSERT INTO payments (booking_id, amount, payment_method, transaction_reference, payment_status)
VALUES 
(1, 27998.00, 'UPI Demo', 'TXN-UPIDEMO-SQL001', 'SUCCESS');
