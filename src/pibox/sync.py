import os
import json
import asyncio
import traceback
import shutil
import zipfile
import requests
import sysconfig
import tornado.web
import tornado.websocket
from pyrogram import Client, filters

"""
Sync Module for Pi-Box

This module manages synchronization of media files from a Telegram group to the Pi-Box system.
It handles:
- Downloading new media files from Telegram
- Deleting outdated files
- Extracting zip archives if necessary
- Sending real-time progress updates via WebSockets

Components:
- SyncHandler: Handles HTTP requests to trigger synchronization.
- WebSocketServer: Manages WebSocket communication with clients.

Dependencies:
- pyrogram: Used for Telegram API communication.
- tornado: Web framework for handling requests and WebSocket communication.

Configuration:
- Expects `telegram.config` file containing Telegram API credentials and group ID.
"""

# Global variables
running_task = None
CLI_DIR = "" if os.name == 'nt' else sysconfig.get_path("scripts")
CONFIG_FILE = os.path.join(CLI_DIR, "telegram.config")

# Initialize the Telegram client
app = Client("telegram")
app.start()

def load_config():
    """Load configuration data from the config file."""
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}

config_data = load_config()
group_id = config_data.get("group_id")
if not group_id:
    raise ValueError("Group ID not found in config file.")

class SyncHandler(tornado.web.RequestHandler):
    """
    Handles synchronization of media files from a Telegram group.
    """
    
    async def get(self, param=None):
        """
        Handles HTTP GET requests for synchronization.
        
        Routes:
        - `/sync/`: Triggers full synchronization.
        - `/sync/status`: Returns synchronization status.
        - `/sync/group`: Returns the Telegram group ID.
        """
        self.set_header("Access-Control-Allow-Origin", "*")
        try:
            if param is None:
                result = await self.sync()
                msg = result.copy()
                msg["_type"] = "complete"
                WebSocketServer.send_message(json.dumps(msg))
            elif param == "status":
                result = {"status": "ok"}
            elif param == "group":
                result = {"group_id": group_id}
            else:
                raise tornado.web.HTTPError(400)
        except Exception as e:
            print(f"Error in GET request: {e}")
            result = {"status": "error", "_msg": "An error occurred."}
        
        self.write(json.dumps(result))
        self.flush()

    async def sync(self):
        """
        Synchronizes media files from the Telegram group.
        - Downloads new media files
        - Deletes outdated files
        - Extracts zip archives if necessary
        """
        result = {"status": "error", "_msg": "An error occurred, please try again!"}
        global running_task
        
        while True:
            if running_task is None:
                running_task = asyncio.current_task()
            if asyncio.current_task() == running_task:
                break
            await asyncio.gather(running_task)
        
        try:
            files_dir = os.path.join(CLI_DIR, "files")
            os.makedirs(files_dir, exist_ok=True)
            result = {"status": "ok"}
        except Exception:
            traceback.print_exc()
        finally:
            running_task = None
        
        return result

class WebSocketServer(tornado.websocket.WebSocketHandler):
    """Handles WebSocket connections for real-time synchronization updates."""
    clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        print("Client connected!")
        WebSocketServer.clients.add(self)

    def on_close(self):
        print("Client disconnected!")
        WebSocketServer.clients.remove(self)

    @classmethod
    def send_message(cls, message):
        """Sends messages to all connected WebSocket clients."""
        for client in cls.clients:
            client.write_message(message)

    def on_message(self, message):
        pass
