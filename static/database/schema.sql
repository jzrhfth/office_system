CREATE DATABASE IF NOT EXISTS office_supplies_db;
USE office_supplies_db;

-- Inventory Table
-- Based on inventory.html columns and modals
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    stock_quantity INT DEFAULT 0,
    unit VARCHAR(50), -- Displayed in table header
    reorder_level INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Requests Table (MRS)
-- Based on requests.html table and index.html form fields
CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mrs_no VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(100),
    request_date DATE,
    status VARCHAR(50) DEFAULT 'Pending', -- Pending, Approved, Rejected
    
    -- Requester Details (from index.html signatures)
    requester_name VARCHAR(255),
    requester_position VARCHAR(100),
    requester_date DATE,
    requester_signature TEXT,
    
    -- Approver Details (from index.html signatures)
    approver_name VARCHAR(255),
    approver_position VARCHAR(100),
    approver_date DATE,
    approver_signature TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Request Items Table
-- Based on index.html item details table
CREATE TABLE IF NOT EXISTS request_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    item_description VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(50),
    purpose TEXT,
    FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE
);

-- Admin Users Table
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user
INSERT IGNORE INTO admin (username, password) VALUES ('admin', 'admin123');