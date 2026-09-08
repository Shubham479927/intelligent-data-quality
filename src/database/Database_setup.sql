create database intelligent_data_quality;

use intelligent_data_quality;

select database();

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    product_category VARCHAR(100),
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(12,2),
    payment_method VARCHAR(50),
    customer_age INT,
    customer_email VARCHAR(255)
);

show tables;

SELECT COUNT(*) FROM orders;

SELECT * FROM orders
LIMIT 10;

SELECT COUNT(*) AS total_orders
FROM orders;

SELECT
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date,
    MIN(quantity) AS minimum_quantity,
    MIN(unit_price) AS minimum_price
FROM orders;

CREATE INDEX idx_customer_id
ON orders(customer_id);

CREATE INDEX idx_order_date
ON orders(order_date);

SHOW INDEX FROM orders;

SELECT COUNT(*) AS total_orders
FROM orders;

CREATE TABLE anomaly_results (
    order_id INT PRIMARY KEY,
    anomaly_prediction INT,
    anomaly_score DECIMAL(10,6),
    anomaly_status VARCHAR(20),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);


