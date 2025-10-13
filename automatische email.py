import mysql.connector
from datetime import datetime
from email.mime.text import MIMEText
import smtplib

def send_email(to_address, name, date, time):
    body = f"""Hallo {name},

am {date} um {time} bist du zu spät gekommen.
Bitte sei in Zukunft pünktlich.

Viele Grüße
Dein Anwesenheitssystem
"""
    msg = MIMEText(body)
    msg['Subject'] = "Verspätung - Anwesenheitssystem"
    msg['From'] = "schule@gmx.de"
    msg['To'] = to_address

    with smtplib.SMTP("mail.gmx.net", 587) as server:
        server.starttls()
        server.login("schule@gmx.de", "DEIN_PASSWORT")
        server.send_message(msg)

def process_rfid(rfid_code):
    conn = mysql.connector.connect(
        host="localhost",
        user="dein_user",
        password="dein_passwort",
        database="attendance_db"
    )
    cursor = conn.cursor(dictionary=True)

    # Schülerdaten abrufen
    cursor.execute("SELECT * FROM students WHERE rfid_tag = %s", (rfid_code,))
    student = cursor.fetchone()

    if not student:
        print("❌ RFID nicht erkannt.")
        return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    status = "on_time" if now.hour < 8 or (now.hour == 8 and now.minute <= 0) else "late"

    # Eintrag speichern
    cursor.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (%s, %s, %s, %s)",
                   (student['id'], date_str, time_str, status))
    conn.commit()

    # E-Mail bei Verspätung
    if status == "late":
        send_email(student['email'], student['name'], date_str, time_str)
        print(f"📧 E-Mail an {student['name']} verschickt.")

    cursor.close()
    conn.close()

# Beispiel: RFID-Code wird eingelesen
rfid_input = input("RFID-Code eingeben: ")
process_rfid(rfid_input)
