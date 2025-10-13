-- Insert test students
INSERT INTO students (username, firstname, lastname, email, class_name, password) VALUES
('lukas', 'Lukas', 'Müller', 'lukas.mueller@school.de', 'IT-2A', SHA2('test1234', 256)),
('melvin', 'Melvin', 'Schmidt', 'melvin.schmidt@school.de', 'IT-2A', SHA2('test1234', 256)),
('jonas', 'Jonas', 'Weber', 'jonas.weber@school.de', 'IT-2B', SHA2('test1234', 256)),
('rayk', 'Rayk', 'Fischer', 'rayk.fischer@school.de', 'IT-2B', SHA2('test1234', 256)),
('benny', 'Benny', 'Wagner', 'benny.wagner@school.de', 'IT-3A', SHA2('test1234', 256)),
('suzie', 'Suzie', 'Klein', 'suzie.klein@school.de', 'IT-3A', SHA2('test1234', 256));

-- Insert some dummy RFID scans
INSERT INTO rfid_scans (rfid_tag, timestamp, scan_count) VALUES
('RFID001234', '2025-10-13 08:15:00', 1),
('RFID005678', '2025-10-13 08:20:00', 1),
('RFID001234', '2025-10-13 12:30:00', 2),
('RFID009012', '2025-10-13 08:25:00', 1),
('RFID001234', '2025-10-13 16:45:00', 3);

-- Link some students to RFID tags
UPDATE students SET rfid_tag = 'RFID001234' WHERE username = 'lukas';
UPDATE students SET rfid_tag = 'RFID005678' WHERE username = 'melvin';
UPDATE students SET rfid_tag = 'RFID009012' WHERE username = 'jonas';