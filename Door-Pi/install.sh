#!/bin/bash
# Door-Pi/install.sh - Smart Installation & Update Script
# Usage: ./install.sh [install|update|build]

MODE="${1:-auto}"

# Auto-detect mode if not specified
if [ "$MODE" = "auto" ]; then
    if [ -f "docker-compose.yml" ]; then
        echo "� Detected existing installation - Running in UPDATE mode"
        MODE="update"
    else
        echo "🆕 No installation found - Running in INSTALL mode"
        MODE="install"
    fi
fi

# Function: Check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
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
    
    echo "✅ Dependencies OK"
}

# Function: Fresh installation
install_fresh() {
    echo "🚪 Installing Door-Pi Node (Fresh Installation)..."
    
    REPO_URL="https://github.com/benjineerr/CheckIO.git"
    
    check_dependencies
    
    # Clone repository
    echo "📥 Cloning repository..."
    rm -rf door-pi-setup
    git clone $REPO_URL door-pi-setup
    cd door-pi-setup/Door-Pi
    
    configure_device
    start_container
}

# Function: Update existing installation
update_project() {
    echo "🔄 Updating Door-Pi Node..."
    
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ Error: Not in a Door-Pi directory. Run with 'install' mode first."
        exit 1
    fi
    
    echo "📥 Pulling latest changes..."
    git pull origin main
    
    echo "🔨 Rebuilding container..."
    docker compose down
    docker compose up --build -d
    
    show_status
}

# Function: Just build/rebuild
build_project() {
    echo "🔨 Building Door-Pi Node..."
    
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ Error: Not in a Door-Pi directory."
        exit 1
    fi
    
    echo "🛑 Stopping existing container..."
    docker compose down
    
    echo "🔨 Building and starting..."
    docker compose up --build -d
    
    show_status
}

# Function: Configure device
configure_device() {
    # Check for serial device
    echo "🔌 Checking serial devices..."
    if [ -e "/dev/ttyACM0" ]; then
        echo "✅ /dev/ttyACM0 found"
    elif [ -e "/dev/ttyUSB0" ]; then
        echo "✅ /dev/ttyUSB0 found, updating config..."
        sed -i 's/ttyACM0/ttyUSB0/g' config/main.conf docker-compose.yml
    else
        echo "⚠️  No serial device found. Please connect your Arduino/RFID reader."
        echo "Available serial devices:"
        ls -la /dev/tty* | grep -E "(USB|ACM)" || ls -la /dev/tty* | head -5
        read -p "Continue anyway? (y/N): " CONTINUE
        if [ "$CONTINUE" != "y" ]; then
            exit 1
        fi
    fi
    
    # Get local IP for configuration
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo "🌐 Detected local IP: $LOCAL_IP"
    
    # Update MQTT broker IP
    read -p "Enter MQTT Broker IP (or press Enter for $LOCAL_IP): " MQTT_IP
    MQTT_IP=${MQTT_IP:-$LOCAL_IP}
    
    echo "📝 Updating configuration with MQTT broker: $MQTT_IP"
    sed -i "s/^broker = .*/broker = ${MQTT_IP}/" config/main.conf
    
    if grep -q "broker = ${MQTT_IP}" config/main.conf; then
        echo "✅ MQTT broker IP successfully updated to: $MQTT_IP"
    else
        echo "⚠️  Manual config update failed, using fallback..."
        cat > config/main.conf << EOF
[serial]
port = /dev/ttyACM0
baud = 115200

[mqtt]
broker = ${MQTT_IP}
port = 1883
topic = rfid/scans

[device]
id = door_node_001
location = door
EOF
        echo "✅ Config manually set with broker: $MQTT_IP"
    fi
}

# Function: Start container
start_container() {
    echo "🚀 Starting Door-Pi container..."
    docker compose up --build -d
    show_status
}

# Function: Show status
show_status() {
    echo ""
    echo "📊 Container status:"
    docker compose ps
    echo ""
    echo "📋 Recent logs:"
    docker compose logs --tail=15 door-node
    echo ""
    echo "🎉 Door-Pi ready!"
    echo ""
    echo "📋 Quick commands:"
    echo "   Logs:         docker compose logs -f door-node"
    echo "   Stop:         docker compose down"
    echo "   Restart:      docker compose restart"
    echo "   Update:       ./install.sh update"
    echo "   Rebuild:      ./install.sh build"
}

# Main execution
case "$MODE" in
    install)
        install_fresh
        ;;
    update)
        update_project
        ;;
    build)
        build_project
        ;;
    *)
        echo "Usage: $0 [install|update|build]"
        echo ""
        echo "Modes:"
        echo "  install  - Fresh installation (clones repo, sets up config)"
        echo "  update   - Pull latest changes and rebuild"
        echo "  build    - Just rebuild container (no git pull)"
        echo "  (auto)   - Automatically detects what to do"
        exit 1
        ;;
esac