CREATE DATABASE flask_db;
USE flask_db;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile_no VARCHAR(15) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

SHOW TABLES;
INSERT INTO users (name, mobile_no, address, gender, email, password)
VALUES ('John Doe', '9876543210', '123 Street, City', 'Male', 'john@example.com', SHA2('password123', 256));

SELECT * FROM users;


