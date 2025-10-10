#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime
import serial
import paho.mqtt.client as mqtt
import configparser

# Load configuration
config = configparser.ConfigParser()
config_file = '/app/config/main.conf'

# Try to read config file
try:
    if os.path.exists(config_file):
        config.read(config_file)
        print(f"[CONFIG] Loaded config from {config_file}")
    else:
        print(f"[CONFIG] Config file {config_file} not found, using environment variables and defaults")
except Exception as e:
    print(f"[CONFIG] Error reading config file: {e}, using environment variables and defaults")

# Helper function to safely get config values
def get_config_value(section, key, fallback, env_var=None):
    # Priority: Environment Variable > Config File > Fallback
    if env_var and os.getenv(env_var):
        return os.getenv(env_var)
    try:
        if config.has_section(section) and config.has_option(section, key):
            return config.get(section, key)
    except:
        pass
    return fallback

# Configuration with priority: ENV > Config File > Defaults
SERIAL_PORT = get_config_value('serial', 'port', '/dev/ttyUSB0', 'SERIAL_PORT')
SERIAL_BAUD = int(get_config_value('serial', 'baud', '115200', 'SERIAL_BAUD'))

MQTT_BROKER = get_config_value('mqtt', 'broker', 'mqtt', 'MQTT_BROKER')
MQTT_PORT = int(get_config_value('mqtt', 'port', '1883', 'MQTT_PORT'))
MQTT_TOPIC = get_config_value('mqtt', 'topic', 'rfid/scans', 'MQTT_TOPIC')

DEVICE_ID = get_config_value('device', 'id', 'door_node_01', 'DEVICE_ID')

print(f"[INFO] Door Node {DEVICE_ID} starting...")
print(f"[INFO] Serial: {SERIAL_PORT}@{SERIAL_BAUD}")
print(f"[INFO] MQTT: {MQTT_BROKER}:{MQTT_PORT} -> {MQTT_TOPIC}")

# Debug: Show configuration source
print("[DEBUG] Configuration loaded from:")
if os.path.exists(config_file):
    print(f"[DEBUG] - Config file: {config_file}")
else:
    print("[DEBUG] - Config file: NOT FOUND")
print("[DEBUG] - Environment variables and defaults")

# MQTT callbacks
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MQTT] Connected to broker {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"[MQTT] Connection failed (code {reason_code})")

def on_disconnect(client, userdata, rc, properties=None):
    print("[MQTT] Disconnected - retrying...")

# Setup MQTT client
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=DEVICE_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Connect to MQTT broker with retry
def connect_mqtt():
    while True:
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.loop_start()
            break
        except Exception as e:
            print(f"[MQTT] Waiting for broker... ({e})")
            time.sleep(5)

# Connect to serial port with retry
def connect_serial():
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
            print(f"[SERIAL] Connected to {SERIAL_PORT}")
            return ser
        except Exception as e:
            print(f"[SERIAL] Waiting for port... ({e})")
            time.sleep(5)

# Main function
def main():
    connect_mqtt()
    ser = connect_serial()
    
    print("[INFO] Door node ready - listening for RFID scans...")
    
    while True:
        try:
            # Read line from serial
            line = ser.readline().decode('utf-8').strip()
            
            if not line:
                continue
                
            # Parse JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                print(f"[WARN] Invalid JSON: {line}")
                continue
            
            # Skip status messages
            if data.get('status') == 'ready':
                print(f"[INFO] Arduino ready: {data}")
                continue
            
            # Add timestamp and device info
            data['timestamp'] = datetime.now().isoformat()
            data['node_id'] = DEVICE_ID
            
            # Send to MQTT
            payload = json.dumps(data)
            mqtt_client.publish(MQTT_TOPIC, payload)
            
            print(f"[DATA] Sent: {payload}")
            
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(1)
    
    # Cleanup
    ser.close()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

if __name__ == "__main__":
    main()