#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime
import serial
import paho.mqtt.client as mqtt
import configparser
import logging

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Robustere Config-Behandlung
def load_config():
    config = configparser.ConfigParser()
    config_file = '/app/config/main.conf'  # Variable hier definieren
    
    # Fallback-Konfiguration
    config.read_dict({
        'serial': {
            'port': '/dev/ttyACM0',
            'baud': '115200'
        },
        'mqtt': {
            'broker': '192.168.1.114',
            'port': '1883',
            'topic': 'rfid/scans'
        },
        'device': {
            'id': 'door_node_001'
        }
    })
    
    # Config-Datei laden falls vorhanden
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            logger.info(f"Config loaded from {config_file}")
        except Exception as e:
            logger.warning(f"Error reading config file: {e}, using defaults")
    else:
        logger.info("Config file not found, using defaults")
    
    return config

# Config laden
config = load_config()

# Konfiguration auslesen
SERIAL_PORT = config.get('serial', 'port')
SERIAL_BAUD = config.getint('serial', 'baud')
MQTT_BROKER = config.get('mqtt', 'broker')
MQTT_PORT = config.getint('mqtt', 'port')
MQTT_TOPIC = config.get('mqtt', 'topic')
DEVICE_ID = config.get('device', 'id')

print(f"[INFO] Door Node {DEVICE_ID} starting...")
print(f"[INFO] Serial: {SERIAL_PORT}@{SERIAL_BAUD}")
print(f"[INFO] MQTT: {MQTT_BROKER}:{MQTT_PORT} -> {MQTT_TOPIC}")

# MQTT Client Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[INFO] Connected to MQTT broker {MQTT_BROKER}")
    else:
        print(f"[ERROR] Failed to connect to MQTT broker, return code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"[WARNING] Disconnected from MQTT broker, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"[DEBUG] Message {mid} published")

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# Serial Connection Setup
def setup_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        print(f"[INFO] Serial connection established on {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Failed to connect to serial port {SERIAL_PORT}: {e}")
        return None

# Main Loop
def main():
    # MQTT verbinden
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"[ERROR] MQTT connection failed: {e}")
        return
    
    # Serial verbinden
    ser = setup_serial()
    if not ser:
        print("[ERROR] Serial connection failed, exiting")
        return
    
    print(f"[INFO] {DEVICE_ID} ready - listening for RFID scans...")
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    # JSON Data vom Arduino lesen
                    line = ser.readline().decode('utf-8').strip()
                    
                    if line and line.startswith('{') and line.endswith('}'):
                        # Parse JSON vom Arduino
                        arduino_data = json.loads(line)
                        
                        if 'rfid_tag' in arduino_data:
                            # MQTT Message für Backend erstellen
                            message = {
                                "rfid_tag": arduino_data['rfid_tag'],
                                "timestamp": datetime.now().isoformat(),
                                "device_id": DEVICE_ID,
                                "location": "door"
                            }
                            
                            # Als JSON an MQTT senden
                            json_message = json.dumps(message)
                            result = client.publish(MQTT_TOPIC, json_message)
                            
                            print(f"[INFO] RFID scan: {arduino_data['rfid_tag']} -> MQTT")
                        
                except json.JSONDecodeError as e:
                    # Falls es kein gültiges JSON ist, ignorieren (könnte Debug-Output sein)
                    pass
                except UnicodeDecodeError as e:
                    logger.error(f"Failed to decode serial data: {e}")
                except Exception as e:
                    logger.error(f"Error processing RFID data: {e}")
            
            time.sleep(0.1)  # Kurze Pause
            
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    finally:
        if ser:
            ser.close()
        client.loop_stop()
        client.disconnect()
        print("[INFO] Cleanup completed")

if __name__ == "__main__":
    main()