USE fake_store;

SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL SELECT 'addresses', COUNT(*) FROM addresses
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'carts', COUNT(*) FROM carts
UNION ALL SELECT 'cart_items', COUNT(*) FROM cart_items
UNION ALL SELECT 'wishlists', COUNT(*) FROM wishlists
UNION ALL SELECT 'wishlist_items', COUNT(*) FROM wishlist_items
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews
UNION ALL SELECT 'coupons', COUNT(*) FROM coupons
UNION ALL SELECT 'roles', COUNT(*) FROM roles
UNION ALL SELECT 'user_roles', COUNT(*) FROM user_roles
UNION ALL SELECT 'payment_report_batches', COUNT(*) FROM payment_report_batches
UNION ALL SELECT 'payment_report_stage', COUNT(*) FROM payment_report_stage
UNION ALL SELECT 'file_processing_logs', COUNT(*) FROM file_processing_logs
UNION ALL SELECT 'audit_logs', COUNT(*) FROM audit_logs;

SELECT
    p.id,
    p.title,
    p.price,
    c.name AS category,
    p.rating_rate,
    p.rating_count
FROM products AS p
JOIN categories AS c ON c.id = p.category_id
ORDER BY p.id;

