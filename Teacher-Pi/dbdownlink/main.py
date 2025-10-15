# arduino_bridge.py

import serial
import mysql.connector
import time

# --- Konfiguration ---
import os

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'user')
MYSQL_PASS = os.environ.get('MYSQL_PASSWORD', 'password')
MYSQL_DB = os.environ.get('MYSQL_DATABASE', 'testdb')
SERIAL_PORT = os.environ.get('SERIAL_PORT', 'compose_port')
SERIAL_BAUDRATE = int(os.environ.get('SERIAL_BAUDRATE', '115200'))

def get_data_from_db():
    """Holt die Namen aus der Datenbank und formatiert sie."""
    try:
        db = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB
        )
        cursor = db.cursor()
        
        # Annahme: Deine Tabelle heißt 'students' und die Spalte 'name'
        cursor.execute("SELECT username, active FROM students ORDER BY username ASC")
        
        # Alle Ergebnisse als Liste von Tupeln holen, z.B. [('Anna',), ('Ben',)]
        results = cursor.fetchall()
        
        # Die Namen aus den Tupeln extrahieren und mit '|' verbinden
        # -> "Anna|Ben|Charlie"
        names = [item[0] for item in results]
        formatted_data = "|".join(names)
        
        db.close()
        return formatted_data
        
    except mysql.connector.Error as err:
        print(f"Datenbankfehler: {err}")
        return None

def main():
    print("Starte Arduino-Bridge...")
    # Serielle Verbindung zum Arduino herstellen
    try:
        arduino = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        time.sleep(2) # Warte kurz, bis die Verbindung stabil ist
        print("Verbindung zum Arduino hergestellt.")
    except serial.SerialException as err:
        print(f"Fehler bei der seriellen Verbindung: {err}")
        return

    while True:
        # Prüfen, ob der Arduino eine Nachricht geschickt hat
        if arduino.in_waiting > 0:
            message_from_arduino = arduino.readline().decode('utf-8').strip()
            print(f"Nachricht vom Arduino empfangen: {message_from_arduino}")
            
            # Wenn der Arduino die Daten anfordert...
            if message_from_arduino == "GET_DATA":
                print("Daten werden aus der DB geholt...")
                datasets = get_data_from_db()
                
                if datasets:
                    # Sende die formatierten Daten, gefolgt von einem Newline-Zeichen
                    # Das Newline-Zeichen signalisiert dem Arduino das Ende der Übertragung
                    response = datasets + '\n'
                    arduino.write(response.encode('utf-8'))
                    print(f"Daten an Arduino gesendet: {datasets}")
        
        time.sleep(0.1)

if __name__ == '__main__':
    main()