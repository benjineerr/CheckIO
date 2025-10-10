# Door Node Configuration Guide

## Setup und Start

### 1. Container bauen und starten
```bash
# Im Door-Pi Verzeichnis
docker-compose build
docker-compose up -d
```

### 2. Logs überprüfen
```bash
docker-compose logs -f door-node
```

## Konfiguration

### Priorität der Konfiguration:
1. **Environment Variables** (höchste Priorität)
2. **Config File** (`config/main.conf`)
3. **Defaults** (niedrigste Priorität)

### Environment Variables überschreiben (optional):
```yaml
# In docker-compose.yml - nur wenn Config-Datei überschrieben werden soll
environment:
  MQTT_BROKER: "192.168.1.200"  # Überschreibt config/main.conf
  SERIAL_PORT: "/dev/ttyACM0"   # Überschreibt config/main.conf
```

### Config File bearbeiten (primäre Konfiguration):
```ini
# config/main.conf - Hauptkonfiguration
[serial]
port = /dev/ttyUSB0
baud = 115200

[mqtt]
broker = 192.168.1.100  # IP des DB-Pi MQTT Brokers
port = 1883
topic = rfid/scans

[device]
id = door_node_01
```

## Troubleshooting

### Config wird nicht geladen?
```bash
# Debug Output anzeigen
docker-compose logs door-node | grep CONFIG
docker-compose logs door-node | grep DEBUG
```

### Serial Port Probleme?
```bash
# Verfügbare Ports anzeigen
ls -la /dev/tty*

# In docker-compose.yml anpassen:
devices:
  - "/dev/ttyACM0:/dev/ttyACM0"  # oder ttyUSB0
```

### MQTT Verbindung fehlgeschlagen?
```bash
# MQTT Broker IP überprüfen
ping 192.168.1.100

# Port erreichbar?
telnet 192.168.1.100 1883
```