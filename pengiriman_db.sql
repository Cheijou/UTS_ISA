CREATE DATABASE pengiriman_db;
USE pengiriman_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password TEXT,
    role ENUM('admin', 'kurir', 'pengirim')
);
