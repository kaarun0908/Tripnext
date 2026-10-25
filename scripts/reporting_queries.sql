-- ====================================================================
-- TripNest: Smart Tourist Booking System — SQL & DBMS Demonstrations
-- Database: SQLite 3 / Relational DBMS Compatible
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. INDEXES FOR HIGH PERFORMANCE SEARCH & BOOKING QUERIES
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_destinations_search ON destinations (name, region, category);
CREATE INDEX IF NOT EXISTS idx_bookings_user_status ON bookings (user_id, booking_status);
CREATE INDEX IF NOT EXISTS idx_room_reservations_date ON room_reservations (room_id, reservation_date, status);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments (payment_status);

-- --------------------------------------------------------------------
-- 2. VIEW 1: Customer Booking Summaries with Multi-Table Joins
-- Demonstrates: LEFT JOIN, INNER JOIN, COALESCE, CASE expressions
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS view_booking_summaries;
CREATE VIEW view_booking_summaries AS
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
    COALESCE(p.name, h.name || ' - ' || r.room_type) AS item_name,
    COALESCE(d_pkg.name, d_htl.name) AS destination_name,
    b.check_in,
    b.check_out,
    CAST((JULIANDAY(b.check_out) - JULIANDAY(b.check_in)) AS INTEGER) AS duration_days,
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

-- --------------------------------------------------------------------
-- 3. VIEW 2: Destination Popularity & Rating Performance View
-- Demonstrates: Multi-table JOIN, Aggregate functions (COUNT, AVG, SUM), GROUP BY
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS view_destination_popularity;
CREATE VIEW view_destination_popularity AS
SELECT 
    d.id AS destination_id,
    d.name AS destination_name,
    d.region,
    d.category,
    d.estimated_budget,
    COUNT(DISTINCT p.id) AS total_packages,
    COUNT(DISTINCT h.id) AS total_hotels,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(CASE WHEN b.booking_status = 'CONFIRMED' THEN b.total_amount ELSE 0 END), 0) AS total_confirmed_revenue,
    ROUND(AVG(COALESCE(rev.rating, 5.0)), 2) AS average_user_rating,
    COUNT(DISTINCT rev.id) AS review_count,
    COUNT(DISTINCT f.id) AS favourite_count
FROM destinations d
LEFT JOIN packages p ON d.id = p.destination_id
LEFT JOIN hotels h ON d.id = h.destination_id
LEFT JOIN bookings b ON (b.package_id = p.id OR b.room_id IN (SELECT id FROM rooms WHERE hotel_id = h.id))
LEFT JOIN reviews rev ON d.id = rev.destination_id
LEFT JOIN favourites f ON d.id = f.destination_id
GROUP BY d.id, d.name, d.region, d.category, d.estimated_budget;

-- --------------------------------------------------------------------
-- 4. VIEW 3: Monthly Booking Revenue Trends
-- Demonstrates: Date formatting, Aggregate functions, GROUP BY, ORDER BY
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS view_monthly_revenue_report;
CREATE VIEW view_monthly_revenue_report AS
SELECT 
    STRFTIME('%Y-%m', b.created_at) AS booking_month,
    COUNT(b.id) AS total_bookings_placed,
    COUNT(CASE WHEN b.booking_status = 'CONFIRMED' THEN 1 END) AS confirmed_bookings,
    COUNT(CASE WHEN b.booking_status = 'CANCELLED' THEN 1 END) AS cancelled_bookings,
    SUM(CASE WHEN pay.payment_status = 'SUCCESS' THEN pay.amount ELSE 0 END) AS net_revenue_collected,
    ROUND(AVG(b.total_amount), 2) AS avg_booking_value
FROM bookings b
LEFT JOIN payments pay ON b.id = pay.booking_id
GROUP BY STRFTIME('%Y-%m', b.created_at)
ORDER BY booking_month DESC;

-- --------------------------------------------------------------------
-- 5. COMPLEX QUERY: Top Performing Destinations with HAVING Clause
-- Demonstrates: GROUP BY with HAVING condition
-- --------------------------------------------------------------------
SELECT 
    d.name AS destination_name,
    d.category,
    COUNT(b.id) AS confirmed_orders,
    SUM(b.total_amount) AS gross_sales,
    MIN(b.total_amount) AS lowest_booking,
    MAX(b.total_amount) AS highest_booking
FROM destinations d
INNER JOIN packages p ON d.id = p.destination_id
INNER JOIN bookings b ON p.id = b.package_id
WHERE b.booking_status = 'CONFIRMED'
GROUP BY d.name, d.category
HAVING COUNT(b.id) >= 1
ORDER BY gross_sales DESC;

-- --------------------------------------------------------------------
-- 6. AUDIT TRAIL QUERY: Complete Status History for a Booking
-- Demonstrates: Audit accountability, Chronological ordering
-- --------------------------------------------------------------------
SELECT 
    b.booking_reference,
    h.old_status,
    h.new_status,
    u.full_name AS action_performed_by,
    u.role AS user_role,
    h.changed_at,
    h.remarks
FROM booking_status_history h
INNER JOIN bookings b ON h.booking_id = b.id
LEFT JOIN users u ON h.changed_by = u.id
ORDER BY h.changed_at DESC;
