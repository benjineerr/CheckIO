# RFID School Check-in and Check-out System

A simple RFID-based attendance system for schools with real-time tracking, web dashboards, and multi-node support.

## Quick Overview

- **Teacher Node**: Raspberry Pi + Arduino + 16x2 LCD + 7-segment display
- **Door Nodes**: Raspberry Pi + Arduino + RFID reader + 16x2 LCD  
- **Web Interface**: Student and teacher dashboards
- **Real-time**: MQTT communication between nodes

## Complete Setup

### Hardware Used

**Teacher Node:**
- Raspberry Pi 4b (4GB)
- Arduino Uno R3
- 16x2 LCD Display (16-pin standard)
- 4-digit 7-segment display
- 2 Push buttons
- Breadboard and jumper wires

**Door Node:**
- Raspberry Pi 4b
- Arduino Uno R3 
- RC522 RFID Reader Module
- 16x2 LCD Display (16-pin standard)
- RFID cards/tags
- Breadboard and jumper wires

### Raspberry Pi Setup

1. **Install Raspberry Pi OS (light)**
    Flash Raspberry Pi OS to SD card (with enabled SSH)
    Boot, connect via SSH (it is recommended to use SSH keys) and update system
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2. **SSID Setup – WiFi Access Point**
    This guide will help you to set up your Raspberry Pi as a WiFi Access Point. It uses `hostapd`, `dnsmasq`, and `dhcpcd5` to broadcast a wireless network and assign IP addresses. This network will then be used for communication between the nodes.

    <details>
    <summary><strong>Step-by-step Setup</strong></summary>

    #### 1. Enable WiFi Interface

    Unblock the WiFi interface:
    ```bash
    sudo rfkill unblock wifi
    ```

    #### 2. Install Required Packages

    Install the necessary services:
    ```bash
    sudo apt install hostapd dnsmasq dhcpcd5
    ```
    **Package overview:**
    * `hostapd`: Broadcasts the wireless network (SSID).
    * `dnsmasq`: Provides DHCP and DNS services.
    * `dhcpcd5`: Used to assign a static IP address.
    **Enable the services:**
    ```bash
    sudo systemctl unmask hostapd
    sudo systemctl enable hostapd
    sudo systemctl enable dnsmasq
    sudo systemctl enable dhcpcd5
    ```

    #### 3. Configure `hostapd` (WiFi Access Point)

    Create the main configuration file:
    ```bash
    sudo vi /etc/hostapd/hostapd.conf
    ```
    Paste the following content (adjust `ssid` and `wpa_passphrase`):
    ```ini
    interface=wlan0
    driver=nl80211
    ssid=SSID
    hw_mode=g
    channel=6
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase=PASSWORD
    wpa_key_mgmt=WPA-PSK
    rsn_pairwise=CCMP
    ```
    Tell the system where to find this configuration:
    ```bash
    sudo vi /etc/default/hostapd
    ```
    ```ini
    DAEMON_CONF="/etc/hostapd/hostapd.conf"
    ```

    #### 4. Configure `dnsmasq` (DHCP Server)

    Backup the original config and create a new one:
    ```bash
    sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
    sudo vi /etc/dnsmasq.conf
    ```
    Add the following:
    ```ini
    interface=wlan0
    dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
    ```

    #### 5. Set Static IP for wlan0

    Edit the `dhcpcd` config:
    ```bash
    sudo vi /etc/dhcpcd.conf
    ```
    Add this to the end of the file:
    ```ini
    interface wlan0
        static ip_address=192.168.4.1/24
        nohook wpa_supplicant
    ```
    
    #### 6. Start Services

    Now restart/start the services:
    ```bash
    sudo systemctl restart dhcpcd
    sudo systemctl start hostapd
    sudo systemctl start dnsmasq
    ```

    #### Summary

    * Your device will now broadcast a WiFi network named `SSID`.
    * Connect using the password `PASSWORD`.
    * The Access Point’s IP address is `192.168.4.1`.

    * You may need to adjust firewall or network settings depending on your system.
    * Make sure `wlan0` is the correct interface. Check with `ip link` or `iwconfig`.
    </details>

3. **Install Docker:**
    ```bash
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    sudo reboot
    ```



## Features

- **Attendance tracking**
- **Real-time RFID scanning**
- **Multi-node support**
- **Docker deployment**
- **SQLite database**
- **MQTT communication**
- **Web-based dashboards**
- **Visual feedback**
