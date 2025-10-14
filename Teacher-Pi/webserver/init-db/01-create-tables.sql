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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('teacher', 'admin') DEFAULT 'teacher',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS rfid_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfid_tag VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(100),
    device_type ENUM('card', 'fob', 'wristband', 'other') DEFAULT 'card',
    status ENUM('active', 'inactive', 'lost', 'broken') DEFAULT 'active',
    assigned_to_student INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to_student) REFERENCES students(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS rfid_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfid_tag VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    scan_count INT DEFAULT 1,
    location VARCHAR(100) DEFAULT 'Haupteingang',
    status ENUM('success', 'denied', 'error') DEFAULT 'success',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rfid_timestamp ON rfid_scans(rfid_tag, timestamp);
CREATE INDEX idx_student_class ON students(class_name);
CREATE INDEX idx_teacher_username ON teachers(username);
CREATE INDEX idx_device_status ON rfid_devices(status);