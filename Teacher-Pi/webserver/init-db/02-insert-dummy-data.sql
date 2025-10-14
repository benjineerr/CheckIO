-- Insert test teachers
INSERT INTO teachers (username, firstname, lastname, email, password, role) VALUES
('teacher', 'Max', 'Mustermann', 'max.mustermann@school.de', SHA2('@itech', 256), 'admin'),
('anna.schmidt', 'Anna', 'Schmidt', 'anna.schmidt@school.de', SHA2('teacher123', 256), 'teacher'),
('peter.mueller', 'Peter', 'Müller', 'peter.mueller@school.de', SHA2('teacher123', 256), 'teacher');

-- Insert test students
INSERT INTO students (username, firstname, lastname, email, class_name, password) VALUES
('lukas', 'Lukas', 'Müller', 'lukas.mueller@school.de', 'IT-2A', SHA2('test1234', 256)),
('melvin', 'Melvin', 'Schmidt', 'melvin.schmidt@school.de', 'IT-2A', SHA2('test1234', 256)),
('jonas', 'Jonas', 'Weber', 'jonas.weber@school.de', 'IT-2B', SHA2('test1234', 256)),
('rayk', 'Rayk', 'Fischer', 'rayk.fischer@school.de', 'IT-2B', SHA2('test1234', 256)),
('benny', 'Benny', 'Wagner', 'benny.wagner@school.de', 'IT-3A', SHA2('test1234', 256)),
('suzie', 'Suzie', 'Klein', 'suzie.klein@school.de', 'IT-3A', SHA2('test1234', 256)),
('maria', 'Maria', 'Lopez', 'maria.lopez@school.de', 'IT-1A', SHA2('test1234', 256)),
('tom', 'Tom', 'Brown', 'tom.brown@school.de', 'IT-1B', SHA2('test1234', 256));

-- Insert RFID devices
INSERT INTO rfid_devices (rfid_tag, device_name, device_type, status) VALUES
('RFID001234', 'Card-001234', 'card', 'active'),
('RFID005678', 'Card-005678', 'card', 'active'),
('RFID009012', 'Card-009012', 'card', 'active'),
('RFID111111', 'Fob-111111', 'fob', 'active'),
('RFID222222', 'Card-222222', 'card', 'inactive'),
('RFID333333', 'Wristband-333333', 'wristband', 'active');

-- Link students to RFID devices
UPDATE students SET rfid_tag = 'RFID001234' WHERE username = 'lukas';
UPDATE students SET rfid_tag = 'RFID005678' WHERE username = 'melvin';
UPDATE students SET rfid_tag = 'RFID009012' WHERE username = 'jonas';

UPDATE rfid_devices SET assigned_to_student = (SELECT id FROM students WHERE username = 'lukas') WHERE rfid_tag = 'RFID001234';
UPDATE rfid_devices SET assigned_to_student = (SELECT id FROM students WHERE username = 'melvin') WHERE rfid_tag = 'RFID005678';
UPDATE rfid_devices SET assigned_to_student = (SELECT id FROM students WHERE username = 'jonas') WHERE rfid_tag = 'RFID009012';

-- Insert some dummy RFID scans
INSERT INTO rfid_scans (rfid_tag, timestamp, scan_count, location, status) VALUES
('RFID001234', '2025-10-13 08:15:00', 1, 'Haupteingang', 'success'),
('RFID005678', '2025-10-13 08:20:00', 1, 'Haupteingang', 'success'),
('RFID001234', '2025-10-13 12:30:00', 2, 'Cafeteria', 'success'),
('RFID009012', '2025-10-13 08:25:00', 1, 'Haupteingang', 'success'),
('RFID001234', '2025-10-13 16:45:00', 3, 'Haupteingang', 'success'),
('RFID999999', '2025-10-13 09:00:00', 1, 'Haupteingang', 'denied'),
('RFID005678', '2025-10-13 14:15:00', 2, 'Bibliothek', 'success');