CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    rfid_tag VARCHAR(255) UNIQUE NULL,
    device_registration_pending BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS rfid_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfid_tag VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    scan_count INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rfid_timestamp ON rfid_scans(rfid_tag, timestamp);
CREATE INDEX idx_student_class ON students(class_name);