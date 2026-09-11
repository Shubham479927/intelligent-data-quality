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

SELECT COUNT(*) AS total_results
FROM anomaly_results;

SHOW VARIABLES LIKE 'port';

USE intelligent_data_quality;

SELECT COUNT(*) FROM orders;

SELECT COUNT(*) FROM anomaly_results;

USE intelligent_data_quality;

SELECT COUNT(*) FROM anomaly_results;

select version();

SELECT user, host, plugin
FROM mysql.user
WHERE user = 'root';

CREATE USER 'powerbi_user'@'localhost'
IDENTIFIED WITH mysql_native_password
BY '9927';

GRANT SELECT ON intelligent_data_quality.* 
TO 'powerbi_user'@'localhost';

FLUSH PRIVILEGES;

SELECT user, host, plugin
FROM mysql.user
WHERE user = 'powerbi_user';

CREATE USER 'powerbi_user'@'127.0.0.1'
IDENTIFIED WITH mysql_native_password
BY '9927';

ALTER USER 'powerbi_user'@'127.0.0.1'
IDENTIFIED WITH mysql_native_password
BY '9927';

GRANT SELECT ON intelligent_data_quality.*
TO 'powerbi_user'@'127.0.0.1';

CREATE USER 'metabase_user'@'localhost' IDENTIFIED BY '9927';

GRANT SELECT ON intelligent_data_quality.* 
TO 'metabase_user'@'localhost';

ALTER USER 'metabase_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY 'YOUR_SAME_PASSWORD';

ALTER USER 'metabase_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY '9927';

FLUSH PRIVILEGES;

USE intelligent_data_quality;

CREATE TABLE pipeline_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_rows INT,
    quarantined_rows INT,
    duplicates_removed INT,
    cleaned_rows INT,
    retention_rate DECIMAL(5,2),
    quality_score DECIMAL(5,2),
    pipeline_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE pipeline_metrics;

INSERT INTO pipeline_metrics (
    original_rows,
    quarantined_rows,
    duplicates_removed,
    cleaned_rows,
    retention_rate,
    quality_score,
    pipeline_status
)
VALUES (
    1020,
    38,
    19,
    963,
    94.41,
    66.67,
    'FAIL'
);

SELECT * FROM pipeline_metrics;

USE intelligent_data_quality;

SELECT *
FROM pipeline_metrics
ORDER BY created_at DESC;

SELECT COUNT(*) AS total_pipeline_runs
FROM pipeline_metrics;

SELECT COUNT(*) AS total_orders
FROM orders;

SELECT COUNT(*) AS total_anomaly_results
FROM anomaly_results;

SELECT anomaly_status, COUNT(*) AS count
FROM anomaly_results
GROUP BY anomaly_status;


