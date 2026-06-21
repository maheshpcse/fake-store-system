-- Generated from MongoDB collections by scripts/generate_mysql_seed_sql.py.

-- WARNING: this resets local Fake Store data before inserting the sample records.

USE fake_store;

SET NAMES utf8mb4;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE audit_logs;

TRUNCATE TABLE file_processing_logs;

TRUNCATE TABLE payments;

TRUNCATE TABLE payment_report_stage;

TRUNCATE TABLE payment_report_batches;

TRUNCATE TABLE reviews;

TRUNCATE TABLE order_items;

TRUNCATE TABLE orders;

TRUNCATE TABLE coupons;

TRUNCATE TABLE wishlist_items;

TRUNCATE TABLE wishlists;

TRUNCATE TABLE cart_items;

TRUNCATE TABLE carts;

TRUNCATE TABLE products;

TRUNCATE TABLE categories;

TRUNCATE TABLE addresses;

TRUNCATE TABLE refresh_tokens;

TRUNCATE TABLE user_roles;

TRUNCATE TABLE roles;

TRUNCATE TABLE users;

SET FOREIGN_KEY_CHECKS = 1;

START TRANSACTION;

INSERT INTO roles (id, name, description) VALUES
    (1, 'customer', 'Regular store customer'),
    (2, 'admin', 'Store administrator');


INSERT INTO users (id, mongo_id, email, username, password_hash, first_name, last_name, phone, street, street_number, city, zipcode, latitude, longitude, is_active) VALUES
    (1, '624b3368da7674e0d99d15b3', 'john@gmail.com', 'johnd', '$2b$12$4KJKA5bMEb0zUNo5Kq1IvuwR5yRfBaxsxcWS.aEd.3XkwHhmacJKm', 'john', 'doe', '1-570-236-7033', 'new road', 7682, 'kilcoole', '12926-3874', '-37.3159', '81.1496', 1),
    (2, '624b3368da7674e0d99d15b4', 'morrison@gmail.com', 'mor_2314', '$2b$12$fAGKgIw2fI1ZmGbE83jKwOOSvi9ke4XYaI/keU292hfMnzJ3emI2q', 'david', 'morrison', '1-570-236-7033', 'Lovers Ln', 7267, 'kilcoole', '12926-3874', '-37.3159', '81.1496', 1),
    (3, '624b3368da7674e0d99d15b5', 'kevin@gmail.com', 'kevinryan', '$2b$12$roEF4aYvlRT7jcZwXMizdep.t7MQZVPKAMS/F0SaI0LxxcCDR9kNS', 'kevin', 'ryan', '1-567-094-1345', 'Frances Ct', 86, 'Cullman', '29567-1452', '40.3467', '-30.1310', 1),
    (4, '624b3368da7674e0d99d15b6', 'don@gmail.com', 'donero', '$2b$12$jhgI5EWaf3WXwgAgfngaW.78k4SoXw8qWaxah2U9wel2mbGdb.n2m', 'don', 'romer', '1-765-789-6734', 'Hunters Creek Dr', 6454, 'San Antonio', '98234-1734', '50.3467', '-20.1310', 1),
    (5, '624b3368da7674e0d99d15b7', 'derek@gmail.com', 'derek', '$2b$12$enG2exSdio1tOu0fHlsdLujFOHJZVP16YXNQ6W38GunPtC0Vq49c.', 'derek', 'powell', '1-956-001-1945', 'adams St', 245, 'san Antonio', '80796-1234', '40.3467', '-40.1310', 1),
    (6, '624b3368da7674e0d99d15b8', 'david_r@gmail.com', 'david_r', '$2b$12$Hcjlz7UqiNkVUVqetUqDBuffQ59Nir2fPANdlvUKiwxyRNc.8Dsx.', 'david', 'russell', '1-678-345-9856', 'prospect st', 124, 'el paso', '12346-0456', '20.1677', '-10.6789', 1),
    (7, '624b3368da7674e0d99d15b9', 'miriam@gmail.com', 'snyder', '$2b$12$DDdpXjWxjt8wcIK0NBfyAO0/FMf7Q6hYhVWltxU/pL44IwIKd5Xie', 'miriam', 'snyder', '1-123-943-0563', 'saddle st', 1342, 'fresno', '96378-0245', '10.3456', '20.6419', 1),
    (8, '624b3368da7674e0d99d15ba', 'william@gmail.com', 'hopkins', '$2b$12$xd42Tbk7iQPSxlE7q9Luu.TKCzvVN1.YLtk9bWJqrpIQUkWnE83X6', 'william', 'hopkins', '1-478-001-0890', 'vally view ln', 1342, 'mesa', '96378-0245', '50.3456', '10.6419', 1),
    (9, '624b3368da7674e0d99d15bb', 'kate@gmail.com', 'kate_h', '$2b$12$5pbk7l/BV1Zdzu33/tjME.HrhMVZXhF0C1ShpxpnJhLENxPECDrnW', 'kate', 'hale', '1-678-456-1934', 'avondale ave', 345, 'miami', '96378-0245', '40.12456', '20.5419', 1),
    (10, '624b3368da7674e0d99d15bc', 'jimmie@gmail.com', 'jimmie_k', '$2b$12$Msg3n6ODKKj57I7yXLkXc.11YplWGS.WqpLLkivTb7K0DBAoKkpUG', 'jimmie', 'klein', '1-104-001-4567', 'oak lawn ave', 526, 'fort wayne', '10256-4532', '30.24788', '-20.545419', 1);


INSERT INTO user_roles (user_id, role_id) VALUES
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
    (6, 1),
    (7, 1),
    (8, 1),
    (9, 1),
    (10, 1);


INSERT INTO addresses (id, mongo_id, user_id, label, full_name, phone, street, city, state, zipcode, country, is_default, created_at) VALUES
    (1, '6a3191bc7c3aa60fe91face6', 5, 'home', 'Derek Powell', '1-956-001-1945', 'adams St', 'San Antonio', 'Texas', '80796-1234', 'USA', 1, '2023-02-10 10:00:00'),
    (2, '6a3191bc7c3aa60fe91face7', 5, 'office', 'Derek Powell', '1-956-001-1945', '100 Main Blvd', 'San Antonio', 'Texas', '80796-5678', 'USA', 0, '2023-03-15 14:30:00'),
    (3, '6a3191bc7c3aa60fe91face8', 7, 'home', 'Miriam Snyder', '1-123-943-0563', 'saddle st', 'Fresno', 'California', '96378-0245', 'USA', 1, '2023-01-20 08:00:00'),
    (4, '6a3191bc7c3aa60fe91face9', 3, 'home', 'Kevin Ryan', '1-567-094-1245', 'new road', 'Culver City', 'California', '93567-1234', 'USA', 1, '2023-04-01 12:00:00'),
    (5, '6a3191bc7c3aa60fe91facea', 8, 'home', 'William Hopkins', '1-890-234-5678', 'elm street', 'Mesa', 'Arizona', '85201-4321', 'USA', 1, '2023-05-10 09:00:00');


INSERT INTO categories (id, mongo_id, name, description, image, is_active, created_at) VALUES
    (1, '6a3191bc7c3aa60fe91face1', 'electronics', 'Electronic gadgets and devices', 'https://fakestoreapi.com/img/category-electronics.jpg', 1, '2023-01-01 00:00:00'),
    (2, '6a3191bc7c3aa60fe91face2', 'men''s clothing', 'Clothing and apparel for men', 'https://fakestoreapi.com/img/category-mens.jpg', 1, '2023-01-01 00:00:00'),
    (3, '6a3191bc7c3aa60fe91face3', 'women''s clothing', 'Clothing and apparel for women', 'https://fakestoreapi.com/img/category-womens.jpg', 1, '2023-01-01 00:00:00'),
    (4, '6a3191bc7c3aa60fe91face4', 'jewelery', 'Rings, necklaces, bracelets and more', 'https://fakestoreapi.com/img/category-jewelery.jpg', 1, '2023-01-01 00:00:00'),
    (5, '6a3191bc7c3aa60fe91face5', 'home & kitchen', 'Home appliances and kitchen essentials', 'https://fakestoreapi.com/img/category-home.jpg', 0, '2023-06-15 00:00:00');


INSERT INTO products (id, mongo_id, category_id, title, description, price, image, rating_rate, rating_count, stock_quantity, is_active) VALUES
    (1, '624b332eda7674e0d99d159f', 2, 'Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops', 'Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday', 109.95, 'https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg', 3.9, 120, 100, 1),
    (2, '624b332eda7674e0d99d15a0', 2, 'Mens Casual Premium Slim Fit T-Shirts ', 'Slim-fitting style, contrast raglan long sleeve, three-button henley placket, light weight & soft fabric for breathable and comfortable wearing. And Solid stitched shirts with round neck made for durability and a great fit for casual fashion wear and diehard baseball fans. The Henley style round neckline includes a three-button placket.', 22.3, 'https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_.jpg', 4.1, 259, 100, 1),
    (3, '624b332eda7674e0d99d15a1', 2, 'Mens Cotton Jacket', 'great outerwear jackets for Spring/Autumn/Winter, suitable for many occasions, such as working, hiking, camping, mountain/rock climbing, cycling, traveling or other outdoors. Good gift choice for you or your family member. A warm hearted love to Father, husband or son in this thanksgiving or Christmas Day.', 55.99, 'https://fakestoreapi.com/img/71li-ujtlUL._AC_UX679_.jpg', 4.7, 500, 100, 1),
    (4, '624b332eda7674e0d99d15a2', 2, 'Mens Casual Slim Fit', 'The color could be slightly different between on the screen and in practice. / Please note that body builds vary by person, therefore, detailed size information should be reviewed below on the product description.', 15.99, 'https://fakestoreapi.com/img/71YXzeOuslL._AC_UY879_.jpg', 2.1, 430, 100, 1),
    (5, '624b332eda7674e0d99d15a3', 4, 'John Hardy Women''s Legends Naga Gold & Silver Dragon Station Chain Bracelet', 'From our Legends Collection, the Naga was inspired by the mythical water dragon that protects the ocean''s pearl. Wear facing inward to be bestowed with love and abundance, or outward for protection.', 695, 'https://fakestoreapi.com/img/71pWzhdJNwL._AC_UL640_QL65_ML3_.jpg', 4.6, 400, 100, 1),
    (6, '624b332eda7674e0d99d15a4', 4, 'Solid Gold Petite Micropave ', 'Satisfaction Guaranteed. Return or exchange any order within 30 days.Designed and sold by Hafeez Center in the United States. Satisfaction Guaranteed. Return or exchange any order within 30 days.', 168, 'https://fakestoreapi.com/img/61sbMiUnoGL._AC_UL640_QL65_ML3_.jpg', 3.9, 70, 100, 1),
    (7, '624b332eda7674e0d99d15a5', 4, 'White Gold Plated Princess', 'Classic Created Wedding Engagement Solitaire Diamond Promise Ring for Her. Gifts to spoil your love more for Engagement, Wedding, Anniversary, Valentine''s Day...', 9.99, 'https://fakestoreapi.com/img/71YAIFU48IL._AC_UL640_QL65_ML3_.jpg', 3, 400, 100, 1),
    (8, '624b332eda7674e0d99d15a6', 4, 'Pierced Owl Rose Gold Plated Stainless Steel Double', 'Rose Gold Plated Double Flared Tunnel Plug Earrings. Made of 316L Stainless Steel', 10.99, 'https://fakestoreapi.com/img/51UDEzMJVpL._AC_UL640_QL65_ML3_.jpg', 1.9, 100, 100, 1),
    (9, '624b332eda7674e0d99d15a7', 1, 'WD 2TB Elements Portable External Hard Drive - USB 3.0 ', 'USB 3.0 and USB 2.0 Compatibility Fast data transfers Improve PC Performance High Capacity; Compatibility Formatted NTFS for Windows 10, Windows 8.1, Windows 7; Reformatting may be required for other operating systems; Compatibility may vary depending on user’s hardware configuration and operating system', 64, 'https://fakestoreapi.com/img/61IBBVJvSDL._AC_SY879_.jpg', 3.3, 203, 100, 1),
    (10, '624b332eda7674e0d99d15a8', 1, 'SanDisk SSD PLUS 1TB Internal SSD - SATA III 6 Gb/s', 'Easy upgrade for faster boot up, shutdown, application load and response (As compared to 5400 RPM SATA 2.5” hard drive; Based on published specifications and internal benchmarking tests using PCMark vantage scores) Boosts burst write performance, making it ideal for typical PC workloads The perfect balance of performance and reliability Read/write speeds of up to 535MB/s/450MB/s (Based on internal testing; Performance may vary depending upon drive capacity, host device, OS and application.)', 109, 'https://fakestoreapi.com/img/61U7T1koQqL._AC_SX679_.jpg', 2.9, 470, 100, 1),
    (11, '624b332eda7674e0d99d15a9', 1, 'Silicon Power 256GB SSD 3D NAND A55 SLC Cache Performance Boost SATA III 2.5', '3D NAND flash are applied to deliver high transfer speeds Remarkable transfer speeds that enable faster bootup and improved overall system performance. The advanced SLC Cache Technology allows performance boost and longer lifespan 7mm slim design suitable for Ultrabooks and Ultra-slim notebooks. Supports TRIM command, Garbage Collection technology, RAID, and ECC (Error Checking & Correction) to provide the optimized performance and enhanced reliability.', 109, 'https://fakestoreapi.com/img/71kWymZ+c+L._AC_SX679_.jpg', 4.8, 319, 100, 1),
    (12, '624b332eda7674e0d99d15aa', 1, 'WD 4TB Gaming Drive Works with Playstation 4 Portable External Hard Drive', 'Expand your PS4 gaming experience, Play anywhere Fast and easy, setup Sleek design with high capacity, 3-year manufacturer''s limited warranty', 114, 'https://fakestoreapi.com/img/61mtL65D4cL._AC_SX679_.jpg', 4.8, 400, 100, 1),
    (13, '624b332eda7674e0d99d15ab', 1, 'Acer SB220Q bi 21.5 inches Full HD (1920 x 1080) IPS Ultra-Thin', '21. 5 inches Full HD (1920 x 1080) widescreen IPS display And Radeon free Sync technology. No compatibility for VESA Mount Refresh Rate: 75Hz - Using HDMI port Zero-frame design | ultra-thin | 4ms response time | IPS panel Aspect ratio - 16: 9. Color Supported - 16. 7 million colors. Brightness - 250 nit Tilt angle -5 degree to 15 degree. Horizontal viewing angle-178 degree. Vertical viewing angle-178 degree 75 hertz', 599, 'https://fakestoreapi.com/img/81QpkIctqPL._AC_SX679_.jpg', 2.9, 250, 100, 1),
    (14, '624b332eda7674e0d99d15ac', 1, 'Samsung 49-Inch CHG90 144Hz Curved Gaming Monitor (LC49HG90DMNXZA) – Super Ultrawide Screen QLED ', '49 INCH SUPER ULTRAWIDE 32:9 CURVED GAMING MONITOR with dual 27 inch screen side by side QUANTUM DOT (QLED) TECHNOLOGY, HDR support and factory calibration provides stunningly realistic and accurate color and contrast 144HZ HIGH REFRESH RATE and 1ms ultra fast response time work to eliminate motion blur, ghosting, and reduce input lag', 999.99, 'https://fakestoreapi.com/img/81Zt42ioCgL._AC_SX679_.jpg', 2.2, 140, 100, 1),
    (15, '624b332eda7674e0d99d15ad', 3, 'BIYLACLESEN Women''s 3-in-1 Snowboard Jacket Winter Coats', 'Note:The Jackets is US standard size, Please choose size as your usual wear Material: 100% Polyester; Detachable Liner Fabric: Warm Fleece. Detachable Functional Liner: Skin Friendly, Lightweigt and Warm.Stand Collar Liner jacket, keep you warm in cold weather. Zippered Pockets: 2 Zippered Hand Pockets, 2 Zippered Pockets on Chest (enough to keep cards or keys)and 1 Hidden Pocket Inside.Zippered Hand Pockets and Hidden Pocket keep your things secure. Humanized Design: Adjustable and Detachable Hood and Adjustable cuff to prevent the wind and water,for a comfortable fit. 3 in 1 Detachable Design provide more convenience, you can separate the coat and inner as needed, or wear it together. It is suitable for different season and help you adapt to different climates', 56.99, 'https://fakestoreapi.com/img/51Y5NI-I5jL._AC_UX679_.jpg', 2.6, 235, 100, 1),
    (16, '624b332eda7674e0d99d15ae', 3, 'Lock and Love Women''s Removable Hooded Faux Leather Moto Biker Jacket', '100% POLYURETHANE(shell) 100% POLYESTER(lining) 75% POLYESTER 25% COTTON (SWEATER), Faux leather material for style and comfort / 2 pockets of front, 2-For-One Hooded denim style faux leather jacket, Button detail on waist / Detail stitching at sides, HAND WASH ONLY / DO NOT BLEACH / LINE DRY / DO NOT IRON', 29.95, 'https://fakestoreapi.com/img/81XH0e8fefL._AC_UY879_.jpg', 2.9, 340, 100, 1),
    (17, '624b332eda7674e0d99d15af', 3, 'Rain Jacket Women Windbreaker Striped Climbing Raincoats', 'Lightweight perfet for trip or casual wear---Long sleeve with hooded, adjustable drawstring waist design. Button and zipper front closure raincoat, fully stripes Lined and The Raincoat has 2 side pockets are a good size to hold all kinds of things, it covers the hips, and the hood is generous but doesn''t overdo it.Attached Cotton Lined Hood with Adjustable Drawstrings give it a real styled look.', 39.99, 'https://fakestoreapi.com/img/71HblAHs5xL._AC_UY879_-2.jpg', 3.8, 679, 100, 1),
    (18, '624b332eda7674e0d99d15b0', 3, 'MBJ Women''s Solid Short Sleeve Boat Neck V ', '95% RAYON 5% SPANDEX, Made in USA or Imported, Do Not Bleach, Lightweight fabric with great stretch for comfort, Ribbed on sleeves and neckline / Double stitching on bottom hem', 9.85, 'https://fakestoreapi.com/img/71z3kpMAYsL._AC_UY879_.jpg', 4.7, 130, 100, 1),
    (19, '624b332eda7674e0d99d15b1', 3, 'Opna Women''s Short Sleeve Moisture', '100% Polyester, Machine wash, 100% cationic polyester interlock, Machine Wash & Pre Shrunk for a Great Fit, Lightweight, roomy and highly breathable with moisture wicking fabric which helps to keep moisture away, Soft Lightweight Fabric with comfortable V-neck collar and a slimmer fit, delivers a sleek, more feminine silhouette and Added Comfort', 7.95, 'https://fakestoreapi.com/img/51eg55uWmdL._AC_UX679_.jpg', 4.5, 146, 100, 1),
    (20, '624b332eda7674e0d99d15b2', 3, 'DANVOUY Womens T Shirt Casual Cotton Short', '95%Cotton,5%Spandex, Features: Casual, Short Sleeve, Letter Print,V-Neck,Fashion Tees, The fabric is soft and has some stretch., Occasion: Casual/Office/Beach/School/Home/Street. Season: Spring,Summer,Autumn,Winter.', 12.99, 'https://fakestoreapi.com/img/61pHAEJ4NML._AC_UX679_.jpg', 3.6, 145, 100, 1);


INSERT INTO carts (id, mongo_id, legacy_id, user_id, status, cart_date) VALUES
    (1, '624b32e4da7674e0d99d1598', 1, 1, 'active', '2020-03-02 00:00:02'),
    (2, '624b32e4da7674e0d99d1599', 2, 1, 'active', '2020-01-02 00:00:02'),
    (3, '624b32e4da7674e0d99d159a', 3, 2, 'active', '2020-03-01 00:00:02'),
    (4, '624b32e4da7674e0d99d159b', 4, 3, 'active', '2020-01-01 00:00:02'),
    (5, '624b32e4da7674e0d99d159c', 5, 3, 'active', '2020-03-01 00:00:02'),
    (6, '624b32e4da7674e0d99d159d', 6, 4, 'active', '2020-03-01 00:00:02'),
    (7, '624b32e4da7674e0d99d159e', 6, 8, 'active', '2020-03-01 00:00:02'),
    (8, NULL, 7, 5, 'active', '2020-04-10 11:00:00');


INSERT INTO cart_items (id, mongo_id, cart_id, user_id, product_id, title, price, quantity, added_at) VALUES
    (1, '6a3191bc7c3aa60fe91faceb', 7, 8, 18, 'MBJ Women''s Solid Short Sleeve Boat Neck V', 9.85, 1, '2020-03-01 00:00:02'),
    (2, '6a3191bc7c3aa60fe91facec', 4, 3, 1, 'Fjallraven - Foldsack No. 1 Backpack', 109.95, 4, '2020-01-01 00:00:02'),
    (3, '6a3191bc7c3aa60fe91faced', 7, 8, 3, 'Mens Cotton Jacket', 55.99, 2, '2020-03-01 00:05:00'),
    (4, '6a3191bc7c3aa60fe91facee', 4, 3, 13, 'Acer SB220Q bi 21.5 inches Full HD IPS Ultra-Thin', 599, 1, '2020-01-01 00:10:00'),
    (5, '6a3191bc7c3aa60fe91facef', 8, 5, 3, 'Mens Cotton Jacket', 55.99, 1, '2020-04-10 11:00:00'),
    (6, '6a3191bc7c3aa60fe91facf0', 8, 5, 13, 'Acer SB220Q bi 21.5 inches Full HD IPS Ultra-Thin', 599, 1, '2020-04-10 11:05:00'),
    (7, NULL, 1, 1, 1, 'Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops', 109.95, 4, '2020-03-02 00:00:02'),
    (8, NULL, 1, 1, 2, 'Mens Casual Premium Slim Fit T-Shirts ', 22.3, 1, '2020-03-02 00:00:02'),
    (9, NULL, 1, 1, 3, 'Mens Cotton Jacket', 55.99, 6, '2020-03-02 00:00:02'),
    (10, NULL, 2, 1, 2, 'Mens Casual Premium Slim Fit T-Shirts ', 22.3, 4, '2020-01-02 00:00:02'),
    (11, NULL, 2, 1, 1, 'Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops', 109.95, 10, '2020-01-02 00:00:02'),
    (12, NULL, 2, 1, 5, 'John Hardy Women''s Legends Naga Gold & Silver Dragon Station Chain Bracelet', 695, 2, '2020-01-02 00:00:02'),
    (13, NULL, 3, 2, 1, 'Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops', 109.95, 2, '2020-03-01 00:00:02'),
    (14, NULL, 3, 2, 9, 'WD 2TB Elements Portable External Hard Drive - USB 3.0 ', 64, 1, '2020-03-01 00:00:02'),
    (15, NULL, 5, 3, 7, 'White Gold Plated Princess', 9.99, 1, '2020-03-01 00:00:02'),
    (16, NULL, 5, 3, 8, 'Pierced Owl Rose Gold Plated Stainless Steel Double', 10.99, 1, '2020-03-01 00:00:02'),
    (17, NULL, 6, 4, 10, 'SanDisk SSD PLUS 1TB Internal SSD - SATA III 6 Gb/s', 109, 2, '2020-03-01 00:00:02'),
    (18, NULL, 6, 4, 12, 'WD 4TB Gaming Drive Works with Playstation 4 Portable External Hard Drive', 114, 3, '2020-03-01 00:00:02');


INSERT INTO wishlists (id, mongo_id, user_id) VALUES
    (1, '6a3191bc7c3aa60fe91fad03', 5),
    (2, '6a3191bc7c3aa60fe91fad04', 7),
    (3, '6a3191bc7c3aa60fe91fad05', 8),
    (4, '6a3191bc7c3aa60fe91fad06', 3);


INSERT INTO wishlist_items (wishlist_id, product_id, added_at) VALUES
    (1, 13, '2020-02-10 09:00:00'),
    (1, 3, '2020-02-12 14:00:00'),
    (2, 1, '2020-03-05 11:00:00'),
    (2, 18, '2020-03-06 15:30:00'),
    (2, 3, '2020-03-10 10:00:00'),
    (3, 13, '2020-01-20 08:00:00');


INSERT INTO coupons (id, mongo_id, code, discount_type, discount_value, min_order_amount, max_discount, usage_limit, used_count, is_active, valid_from, valid_until) VALUES
    (1, '6a3191bc7c3aa60fe91fad07', 'WELCOME10', 'percentage', 10, 100, 50, 1000, 320, 1, '2020-01-01 00:00:00', '2025-12-31 23:59:59'),
    (2, '6a3191bc7c3aa60fe91fad08', 'FLAT50', 'flat', 50, 500, 50, 500, 150, 1, '2020-01-01 00:00:00', '2024-06-30 23:59:59'),
    (3, '6a3191bc7c3aa60fe91fad09', 'SUMMER25', 'percentage', 25, 200, 100, 200, 200, 0, '2020-05-01 00:00:00', '2020-08-31 23:59:59'),
    (4, '6a3191bc7c3aa60fe91fad0a', 'NEWUSER30', 'percentage', 30, 300, 150, 100, 45, 1, '2023-01-01 00:00:00', '2026-12-31 23:59:59');


INSERT INTO orders (id, mongo_id, user_id, address_id, status, total_amount, discount, final_amount, currency, payment_method, ordered_at, delivered_at) VALUES
    (1, '6a3191bc7c3aa60fe91facf1', 8, 5, 'delivered', 121.83, 0, 121.83, 'USD', 'credit_card', '2020-03-02 10:00:00', '2020-03-07 14:30:00'),
    (2, '6a3191bc7c3aa60fe91facf2', 3, 4, 'delivered', 1038.8, 50, 988.8, 'USD', 'debit_card', '2020-01-02 09:00:00', '2020-01-08 16:00:00'),
    (3, '6a3191bc7c3aa60fe91facf3', 5, 1, 'shipped', 654.99, 0, 654.99, 'USD', 'upi', '2020-04-11 08:00:00', NULL),
    (4, '6a3191bc7c3aa60fe91facf4', 7, 3, 'cancelled', 55.99, 0, 55.99, 'USD', 'credit_card', '2020-05-01 12:00:00', NULL),
    (5, '6a3191bc7c3aa60fe91facf5', 3, 4, 'pending', 599, 30, 569, 'USD', 'net_banking', '2020-06-15 10:00:00', NULL);


INSERT INTO order_items (id, mongo_id, order_id, product_id, title, price, quantity, subtotal) VALUES
    (1, '6a3191bc7c3aa60fe91facf6', 1, 18, 'MBJ Women''s Solid Short Sleeve Boat Neck V', 9.85, 1, 9.85),
    (2, '6a3191bc7c3aa60fe91facf7', 1, 3, 'Mens Cotton Jacket', 55.99, 2, 111.98),
    (3, '6a3191bc7c3aa60fe91facf8', 2, 1, 'Fjallraven - Foldsack No. 1 Backpack', 109.95, 4, 439.8),
    (4, '6a3191bc7c3aa60fe91facf9', 2, 13, 'Acer SB220Q bi 21.5 inches Full HD IPS Ultra-Thin', 599, 1, 599),
    (5, '6a3191bc7c3aa60fe91facfa', 3, 3, 'Mens Cotton Jacket', 55.99, 1, 55.99),
    (6, '6a3191bc7c3aa60fe91facfb', 3, 13, 'Acer SB220Q bi 21.5 inches Full HD IPS Ultra-Thin', 599, 1, 599),
    (7, '6a3191bc7c3aa60fe91facfc', 4, 3, 'Mens Cotton Jacket', 55.99, 1, 55.99),
    (8, '6a3191bc7c3aa60fe91facfd', 5, 13, 'Acer SB220Q bi 21.5 inches Full HD IPS Ultra-Thin', 599, 1, 599);


INSERT INTO payments (id, mongo_id, legacy_id, order_id, user_id, method, card_last4, amount, currency, status, transaction_id, paid_at) VALUES
    (1, '6a3191bc7c3aa60fe91facfe', 1, 1, 8, 'credit_card', '4242', 121.83, 'USD', 'success', 'TXN100001', '2020-03-02 10:01:00'),
    (2, '6a3191bc7c3aa60fe91facff', 2, 2, 3, 'debit_card', '8765', 988.8, 'USD', 'success', 'TXN100002', '2020-01-02 09:02:00'),
    (3, '6a3191bc7c3aa60fe91fad00', 3, 3, 5, 'upi', NULL, 654.99, 'USD', 'success', 'TXN100003', '2020-04-11 08:05:00'),
    (4, '6a3191bc7c3aa60fe91fad01', 4, 4, 7, 'credit_card', '1111', 55.99, 'USD', 'refunded', 'TXN100004', '2020-05-01 12:02:00'),
    (5, '6a3191bc7c3aa60fe91fad02', 5, 5, 3, 'net_banking', NULL, 569, 'USD', 'pending', 'TXN100005', NULL);


INSERT INTO reviews (id, mongo_id, product_id, user_id, rating, title, comment, is_verified_purchase, created_at) VALUES
    (1, '6a3191bd7c3aa60fe91fad0b', 3, 8, 5, 'Excellent jacket!', 'Very warm and comfortable. Perfect for winter hiking.', 1, '2020-03-10 12:00:00'),
    (2, '6a3191bd7c3aa60fe91fad0c', 13, 3, 4, 'Great monitor for the price', 'Display quality is really good. Slight backlight bleed but acceptable.', 1, '2020-01-15 09:00:00'),
    (3, '6a3191bd7c3aa60fe91fad0d', 1, 3, 5, 'Love this backpack', 'Durable and spacious. Using it daily for work.', 1, '2020-01-20 14:00:00'),
    (4, '6a3191bd7c3aa60fe91fad0e', 3, 5, 4, 'Good quality', 'Nice jacket. Slightly tight on the arms but overall great.', 0, '2020-05-01 18:00:00'),
    (5, '6a3191bd7c3aa60fe91fad0f', 18, 7, 3, 'Average quality', 'Fabric could be better. Color faded after two washes.', 0, '2020-04-15 10:00:00'),
    (6, '6a3191bd7c3aa60fe91fad10', 13, 5, 5, 'Best budget monitor', 'Crisp display, thin bezels. Highly recommended.', 1, '2020-05-20 16:00:00');


COMMIT;

SET FOREIGN_KEY_CHECKS = 1;