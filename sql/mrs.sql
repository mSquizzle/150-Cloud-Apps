# Database Setup 

CREATE DATABASE IF NOT EXISTS mrs;
USE mrs;

CREATE TABLE donor (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(128) NOT NULL,
    blood_type VARCHAR(5),
    zipcode INT NOT NULL,
    last_donation DATE,
    eligibility ENUM('Eligible', 'Ineligible', 'Unknown') DEFAULT 'Unknown',
    contact ENUM('Email', 'Text', 'Phone', 'None') DEFAULT 'Email',
    outreach ENUM('YES', 'NO') DEFAULT 'YES'
);

CREATE TABLE bank (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hashed VARCHAR(128) NOT NULL,
    name VARCHAR(128) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(128) NOT NULL,
    address_1 VARCHAR(128),
    address_2 VARCHAR(128), 
    city VARCHAR(128),
    state VARCHAR(128),
    zipcode INT NOT NULL,
    O_neg INT DEFAULT 0,
    O_pos INT DEFAULT 0,
    A_neg INT DEFAULT 0,
    A_pos INT DEFAULT 0,
    B_neg INT DEFAULT 0,
    B_pos INT DEFAULT 0,
    AB_neg INT DEFAULT 0, 
    AB_pos INT DEFAULT 0
);

CREATE TABLE hospital (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hashed VARCHAR(128) NOT NULL,
    name VARCHAR(128) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(128) NOT NULL,
    address_1 VARCHAR(128),
    address_2 VARCHAR(128), 
    city VARCHAR(128),
    state VARCHAR(128),
    zipcode INT NOT NULL,
    O_neg INT DEFAULT 0,
    O_pos INT DEFAULT 0,
    A_neg INT DEFAULT 0,
    A_pos INT DEFAULT 0,
    B_neg INT DEFAULT 0,
    B_pos INT DEFAULT 0,
    AB_neg INT DEFAULT 0, 
    AB_pos INT DEFAULT 0
);
