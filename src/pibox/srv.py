#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Pi-Box Server Initialization Script

This script initializes and starts the Pi-Box web server using Tornado.
It sets up routes for handling WiFi connections, synchronization, WebSocket communication,
and static file serving.

Modules Used:
- tornado.web: Handles web requests
- tornado.ioloop: Manages asynchronous event loops
- pibox.wifi: Handles WiFi-related requests
- pibox.sync: Manages synchronization of media files
- pibox.conn: Handles internet connection status checks

Usage:
Run this script to start the Pi-Box web server, which listens on port 80.
"""

import os
import sys
import tornado.web
from tornado.ioloop import IOLoop

from pibox.wifi import WifiHandler
from pibox.sync import SyncHandler, WebSocketServer
from pibox.conn import ConnHandler

import subprocess

# Get the base directory of the script
base_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    """
    Main function to initialize and start the Pi-Box web server.
    
    The server provides endpoints for:
    - WiFi management (`/wifi/`)
    - Synchronization (`/sync/` and `/sync/{param}`)
    - WebSocket communication (`/websocket/`)
    - Internet connection status (`/conn/`)
    - Static file serving (`/(.*)`, serving files from `public/` directory)
    """
    print("Starting Pi-Box server")
    
    # Define Tornado web application with route handlers
    web = tornado.web.Application([
        (r"/wifi/", WifiHandler),
        (r"/sync/", SyncHandler),
        (r"/sync/([^/]+)", SyncHandler),
        (r"/websocket/", WebSocketServer),
        (r"/conn/", ConnHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(base_dir, "public"),
            "default_filename": "index.html"
        })
    ],
    websocket_ping_interval=10,  # Send a ping every 10 seconds
    websocket_ping_timeout=30     # Close connection if no response within 30 seconds
    )
    
    # Start the web server on port 80
    web.listen(80)
    
    # Get and start the event loop
    io_loop = IOLoop.current()
    io_loop.start()

if __name__ == "__main__":
    main()
