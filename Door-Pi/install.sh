#!/bin/bash
# Door-Pi/install.sh
echo "🚪 Installing Door-Pi Node..."

# Korrekte Repository URL
REPO_URL="https://github.com/benjineerr/CheckIO.git"

# Check dependencies
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo apt update && sudo apt install -y git
fi

if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "⚠️  Please logout and login again, then run this script again"
    exit 1
fi

# Clone repository
echo "📥 Cloning repository..."
rm -rf door-pi-setup
git clone $REPO_URL door-pi-setup
cd door-pi-setup/Door-Pi

# Check for serial device
echo "🔌 Checking serial devices..."
if [ -e "/dev/ttyACM0" ]; then
    echo "✅ /dev/ttyACM0 found"
elif [ -e "/dev/ttyUSB0" ]; then
    echo "✅ /dev/ttyUSB0 found, updating config..."
    sed -i 's/ttyACM0/ttyUSB0/g' config/main.conf docker-compose.yml
else
    echo "❌ No serial device found. Please connect your Arduino/RFID reader."
    ls -la /dev/tty* | grep -E "(USB|ACM)" || echo "Available devices:"
    ls -la /dev/tty* | head -5
    exit 1
fi

# Get local IP for configuration
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🌐 Detected local IP: $LOCAL_IP"

# Update MQTT broker IP
read -p "Enter MQTT Broker IP (or press Enter for $LOCAL_IP): " MQTT_IP
MQTT_IP=${MQTT_IP:-$LOCAL_IP}

echo "📝 Updating configuration with MQTT broker: $MQTT_IP"
sed -i "s/broker = .*/broker = $MQTT_IP/" config/main.conf

# Start container
echo "🚀 Starting Door-Pi container..."
docker compose up --build -d

# Show status
echo "📊 Container status:"
docker compose ps
docker compose logs --tail=10 door-node

echo ""
echo "🎉 Door-Pi installation complete!"
echo "📋 Management commands:"
echo "   View logs:    docker compose logs -f door-node"
echo "   Stop:         docker compose down"
echo "   Restart:      docker compose restart"
echo "   Update:       docker compose pull && docker compose up -d"