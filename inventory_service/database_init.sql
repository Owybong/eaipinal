-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS inventory_db;

-- Use the database
USE inventory_db;

-- Drop tables if they exist
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS warehouses;

-- Create warehouses table
CREATE TABLE warehouses (
  id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  location TEXT,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

-- Create inventory table
CREATE TABLE inventory (
  product_id VARCHAR(255) NOT NULL,
  warehouse_id VARCHAR(255) NOT NULL,
  stock INT NOT NULL DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id, warehouse_id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

-- Insert sample data
INSERT INTO warehouses (id, name, location) VALUES 
('WH001', 'Main Warehouse', 'Jakarta'),
('WH002', 'East Warehouse', 'Surabaya'),
('WH003', 'West Warehouse', 'Bandung');

INSERT INTO inventory (product_id, warehouse_id, stock) VALUES 
('P001', 'WH001', 100),
('P002', 'WH001', 50),
('P001', 'WH002', 75),
('P003', 'WH003', 200); 