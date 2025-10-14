#!/usr/bin/env python3
"""
Door-Pi - RFID Scanner Node
Liest RFID-Tags vom Arduino und sendet sie via MQTT
"""
import os
import json
import time
from datetime import datetime
import serial
import paho.mqtt.client as mqtt
import configparser
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Lädt die Konfiguration"""
    config = configparser.ConfigParser()
    config_file = '/app/config/main.conf'
    
    # Defaults
    config.read_dict({
        'serial': {'port': '/dev/ttyACM0', 'baud': '115200'},
        'mqtt': {'broker': '192.168.178.114', 'port': '1883', 'topic': 'rfid/scans'},
        'device': {'id': 'door_node_001'}
    })
    
    if os.path.exists(config_file):
        config.read(config_file)
        logger.info(f"✅ Config loaded: {config_file}")
    
    return config

config = load_config()

# Config auslesen
SERIAL_PORT = config.get('serial', 'port')
SERIAL_BAUD = config.getint('serial', 'baud')
MQTT_BROKER = config.get('mqtt', 'broker')
MQTT_PORT = config.getint('mqtt', 'port')
MQTT_TOPIC = config.get('mqtt', 'topic')
DEVICE_ID = config.get('device', 'id')

logger.info(f"🚪 Door Node: {DEVICE_ID}")
logger.info(f"📡 Serial: {SERIAL_PORT} @ {SERIAL_BAUD}")
logger.info(f"📨 MQTT: {MQTT_BROKER}:{MQTT_PORT} → {MQTT_TOPIC}")

# MQTT Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"✅ MQTT connected")
    else:
        logger.error(f"❌ MQTT failed: {rc}")

client.on_connect = on_connect

def main():
    # MQTT verbinden
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        logger.error(f"❌ MQTT error: {e}")
        return
    
    # Serial verbinden
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        logger.info(f"✅ Serial connected")
        time.sleep(2)
    except serial.SerialException as e:
        logger.error(f"❌ Serial error: {e}")
        return
    
    logger.info("🎯 Ready - listening for RFID scans...")
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    # Arduino sendet: "RFID001234AB"
                    rfid_tag = ser.readline().decode('utf-8').strip()
                    
                    if rfid_tag:
                        # Timestamp hier hinzufügen
                        timestamp = datetime.now().isoformat()
                        
                        # MQTT Message
                        message = {
                            "rfid_tag": rfid_tag,
                            "timestamp": timestamp
                        }
                            #"device_id": DEVICE_ID,
                            #"location": "door"
                        #}

                        client.publish(MQTT_TOPIC, json.dumps(message))
                        logger.info(f"✅ {rfid_tag} → MQTT")
                        
                except Exception as e:
                    logger.error(f"❌ Error: {e}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()