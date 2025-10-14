import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Funktion zum E-Mail-Versand
def send_email(to_address, name, date, time):
    body = f"""Hallo {name},

am {date} um {time} bist du zu spät gekommen.
Bitte sei in Zukunft pünktlich.

Viele Grüße
Dein Anwesenheitssystem
"""
    msg = MIMEText(body)
    msg['Subject'] = "Verspätung - Anwesenheitssystem"
    msg['From'] = "schule.itech@gmx.de"   # Absenderadresse
    msg['To'] = to_address

    # Verbindung zum Mailserver (Beispiel: Gmail)
    with smtplib.SMTP("mail.gmx.net", 587) as server:
        server.starttls()
        server.login("schule.itech@gmx.de", "Schule123!4567")
        server.send_message(msg)

# Hauptprogramm
if __name__ == "__main__":
    # Eingaben vom Nutzer
    name = input("Name des Schülers: ")
    email = input("E-Mail-Adresse des Schülers: ")
    uhrzeit = input("Uhrzeit des Eintreffens (HH:MM): ")

    # Heutiges Datum automatisch einsetzen
    heute = datetime.now().strftime("%d.%m.%Y")

    # E-Mail verschicken
    send_email(email, name, heute, uhrzeit)
    print(f"✅ E-Mail an {name} ({email}) wurde verschickt.")
