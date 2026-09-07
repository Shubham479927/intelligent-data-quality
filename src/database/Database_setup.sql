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
