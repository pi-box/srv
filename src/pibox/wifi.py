#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
WiFi Management Module for Pi-Box

This module provides functionality for managing WiFi networks on the Pi-Box system.
It allows scanning for available networks and connecting to a specified WiFi network.

Endpoints:
- GET `/wifi/`: Returns a list of available WiFi networks.
- GET `/wifi/?ssid=<SSID>&pwd=<PASSWORD>`: Connects to a specified WiFi network.

Dependencies:
- tornado.web: Handles web requests.
- subprocess: Executes system commands for managing WiFi connections.

Platform Support:
- Linux (tested on Raspberry Pi)
- Windows (limited support for scanning networks only)

"""

import tornado.web
import os
import json
import subprocess
import codecs

class WifiHandler(tornado.web.RequestHandler):
    """
    Tornado request handler for WiFi management.
    
    Provides methods to:
    - Scan for available WiFi networks.
    - Connect to a specified WiFi network.
    """
    
    def getSsids(self):
        """Scans and retrieves a list of available WiFi networks."""
        ssids = None
        
        if os.name == 'nt':  # Windows system
            results = subprocess.check_output(["netsh", "wlan", "show", "network"])
            results = results.decode("cp1252").replace("\r", "").split("\n")[4:-1]
            ssids = [result.split(":")[1].strip() for result in results if "SSID" in result]
        else:  # Linux system (Raspberry Pi)
            results = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"])
            results = results.decode().split("\n")
            ssids = [result.split(":")[1].strip("\"") for result in results if "ESSID" in result]
            ssids = [codecs.escape_decode(ssid)[0].decode('utf-8') for ssid in ssids if ssid]
            ssids = list(set(ssids))  # Remove duplicates
        
        return ssids
    
    async def get(self):
        """Handles HTTP GET requests for WiFi management.
        
        Supported operations:
        - Retrieve available WiFi networks.
        - Connect to a WiFi network using provided SSID and password.
        """
        self.set_header("Access-Control-Allow-Origin", "*")
        result = None
        
        if self.get_argument("ssid", ""):  # Attempt to connect to a network
            ssid = self.get_argument("ssid", "")
            pwd = self.get_argument("pwd", "")
            os.popen(f"sudo nmcli d wifi connect {ssid} password {pwd} ifname wlan0")
            try:
                result = {"status": "ok"}
            except OSError:
                result = {"status": "error", "msg": "wlan0 Reconfigure Error"}
        else:  # Return available networks
            result = {"status": "ok", "ssids": self.getSsids()}
        
        self.write(json.dumps(result))
        self.flush()
