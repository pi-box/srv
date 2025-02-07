# Pi-Box Installation Guide

## Introduction

Pi-Box is a Raspberry Pi-based multimedia system designed to facilitate easy playback of media content. The system syncs videos and images from a dedicated Telegram group to a Raspberry Pi device and displays them on a connected TV in full high-definition (FHD) quality. This setup is ideal for digital signage, automated multimedia playback, or remote content management without requiring manual intervention.

The system ensures seamless synchronization by leveraging the Telegram API to fetch media files automatically. Once set up, Pi-Box can continuously loop media files on a connected screen, making it useful for businesses, presentations, or personal entertainment setups.

## Installation Steps

### 1. Install Raspberry Pi OS

The installation has been tested on Raspberry Pi Zero 2 W.

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Use the imager to flash Raspberry Pi OS (Lite recommended) onto an SD card.
3. Insert the SD card into the Raspberry Pi and power it on.

### 2. Optional: Configure WiFi Without a Computer (Temporary Hotspot)

📌 **How it Works?** When the Raspberry Pi is powered on, it will check for available WiFi networks. If no known network is found, it will start a hotspot, allowing you to connect via a phone or computer and configure the WiFi. The network setup can be done using a phone by connecting to the hotspot and accessing the management interface, as described in the section [Accessing the Pi-Box User Interface](#accessing-the-pi-box-user-interface).

#### Create a Connection Management Script (AutoHotspot)

First, create a script to check if the device is connected to WiFi and enable the hotspot mode if not.

```bash
sudo nano /usr/bin/autohotspot
```

Add the following script:

```bash
#!/bin/bash
SSID="PIBOX_AP"
PASS="12345678"

# Check if connected to a network; if not, enable AP mode
if ! iwgetid -r; then
    echo "Not connected - enabling AP..."
    nmcli dev wifi hotspot ifname wlan0 ssid $SSID password $PASS
else
    echo "Already connected to a WiFi network."
fi
```

Save and make the script executable:

```bash
sudo chmod +x /usr/bin/autohotspot
```

#### Create a System Service for AutoHotspot

To ensure the script runs at startup, create a systemd service:

```bash
sudo nano /etc/systemd/system/autohotspot.service
```

Add the following content:

```ini
[Unit]
Description=AutoHotspot Service
After=network.target

[Service]
ExecStart=/usr/bin/autohotspot
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Save and exit (`CTRL + X`, then `Y` and press `Enter`).

Enable and start the service:

```bash
sudo systemctl enable autohotspot
sudo systemctl start autohotspot
```

#### Reboot and Connect to the Hotspot

Now, when the RPi boots up without an available network, it will broadcast a WiFi network named `PIBOX_AP` with the password `12345678`. You can connect to this network using your phone and access the management interface, as detailed in the section [Accessing the Pi-Box User Interface](#accessing-the-pi-box-user-interface), to configure a permanent WiFi connection.

### 3. Install Required Packages

Run the following commands to install essential dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip git
```

### 4. Install Pi-Box Service

Clone and install the Pi-Box service:

```bash
sudo pip install git+https://github.com/pi-box/srv.git --break-system-packages
```

### 5. Setup Telegram API Credentials

To enable syncing from Telegram:

1. [Go to](https://my.telegram.org/) [my.telegram.org](https://my.telegram.org/).
2. Create a new application.
3. Save the `api_id` and `api_hash`. These will be required in step 7.

### 6. Create a Telegram Group

- Create a Telegram group, preferably private.
- Copy the group link in the format `t.me/+your_group_link_here`, as it will be required in step 7.

### 7. Run Initial Setup

Run the setup script and follow the prompts to enter the required information:

```bash
sudo setup_pibox
```

During the setup, you will be prompted to enter:

- Your Telegram API ID
- Your Telegram API Hash
- Your phone number or bot token
- Confirmation of the entered phone number
- The confirmation code sent to your Telegram app
- Your Telegram group link in the format `t.me/+your_group_link_here`

Ensure that you have saved these details as noted in steps 5, 6.

### 8. Configure Auto-Start Service

Create a system service to start Pi-Box on boot.

```bash
sudo systemctl enable pibox
sudo systemctl start pibox
```

### 9. Install VLC

VLC is required for media playback:

```bash
sudo apt install -y vlc
```

### 10. Modify Permissions for VLC

To allow VLC to run as a root service:

```bash
sudo sed -i 's/geteuid/getppid/' /usr/bin/vlc
```

### 11. Configure VLC as a System Service

Create a new service file:

```bash
sudo nano /etc/systemd/system/pibox-vlc.service
```

Add the following content:

```ini
[Unit]
Description=Pi-Box VLC Service
After=network.target

[Service]
ExecStart=/bin/bash -c 'PYTHON_CLI_DIR=$(python -c "import os, sys; print(os.path.join(os.path.dirname(sys.executable), 'Scripts' if os.name == 'nt' else 'bin'))"); FILES_PATH="$PYTHON_CLI_DIR/files/*"; cvlc --loop --no-osd $FILES_PATH'
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Enable and start the VLC service:

```bash
sudo systemctl enable pibox-vlc
sudo systemctl start pibox-vlc
```

## Accessing the Pi-Box User Interface

You can access the Pi-Box service through its user interface when connected to the same network or WiFi:

[http://pi-box.local](http://pi-box.local) (where pi-box.local is the hostname of your Raspberry Pi).

From this interface, you can manually trigger synchronization or configure a WiFi network.

## Conclusion

You have successfully set up Pi-Box, which will now automatically sync media from Telegram and play it on your connected display. If any issues arise, check the logs using:

```bash
sudo journalctl -u pibox -f
sudo journalctl -u pibox-vlc -f
```

