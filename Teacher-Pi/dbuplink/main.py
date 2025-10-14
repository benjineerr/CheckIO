import os
import time
import json
import mysql.connector
import paho.mqtt.client as mqtt

# === Configuration from environment variables ===
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "db"),
    "user": os.getenv("MYSQL_USER", "user"),
    "password": os.getenv("MYSQL_PASSWORD", "password"),
    "database": os.getenv("MYSQL_DATABASE", "testdb"),
}

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "rfid/scans")

# === Connect to MySQL database ===
def connect_db():
    while True:
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            print("Connected to MySQL successfully!")
            return conn
        except Exception as e:
            print(f"Waiting for MySQL... ({e})")
            time.sleep(5)

db = connect_db()
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS rfid_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic VARCHAR(255),
    payload JSON
)
""")
db.commit()

# === MQTT callbacks ===
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"MQTT connection failed (code {reason_code})")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode()
        print(f"Message received on '{msg.topic}': {payload_str}")
        try:
            data = json.loads(payload_str)
        except json.JSONDecodeError:
            data = {"raw": payload_str}

        cursor.execute(
            "INSERT INTO rfid_scans (topic, payload) VALUES (%s, %s)",
            (msg.topic, json.dumps(data)),
        )
        db.commit()
        print("Record successfully saved to MySQL.")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected from MQTT broker – retrying connection...")
    while True:
        try:
            client.reconnect()
            break
        except Exception as e:
            print(f"Waiting for MQTT broker... ({e})")
            time.sleep(5)

# === MQTT client setup ===
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Start connection
print(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
client.connect(MQTT_BROKER, MQTT_PORT)

print(f"App is running – waiting for MQTT messages on '{MQTT_TOPIC}'...")
client.loop_forever()
