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

# Global variables
running_task = None
CLI_DIR = sysconfig.get_path("scripts")
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
    """Handles synchronization of files from a Telegram group."""

    @app.on_message(filters.chat(group_id))
    @app.on_deleted_messages(filters.chat(group_id))
    @app.on_edited_message(filters.chat(group_id))
    async def on_message(client, message):
        """Handles new messages, edits, or deletions in the group."""
        try:
            await asyncio.to_thread(requests.get, 'http://localhost/sync/')
        except Exception as e:
            print(f"Error in sync request: {e}")

    async def get(self, param=None):
        """Handles GET requests for synchronization and status checks."""
        self.set_header("Access-Control-Allow-Origin", "*")
        try:
            if param is None:
                result = await self.sync()
                msg = result.copy()
                msg["_type"] = "complete"
                msg = json.dumps(msg)
                WebSocketServer.send_message(msg)
            elif param == "status":
                result = {"status": "ok"}
            else:
                raise tornado.web.HTTPError(400)
        except Exception as e:
            print(f"Error in GET request: {e}")
            result = {"status": "error", "_msg": "An error occurred."}
        
        self.write(json.dumps(result))
        self.flush()

    async def sync(self):
        """Synchronizes media files from the Telegram group."""
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
            files_exist = {file.split('.')[0]: file for file in os.listdir(files_dir) if file != "System Volume Information"}
            files_to_sync = []

            await app.get_chat(config_data.get("group_link"))

            total_size = 0
            self.temp_size = 0
            async for msg in app.get_chat_history(group_id):
                file_info = None
                if not msg.caption or "ignore" not in msg.caption:
                    msg_part = msg.document or msg.video or msg.animation or msg.photo
                    if msg_part:
                        file_info = msg_part.file_unique_id, msg_part.mime_type.split('/')[-1], msg_part.file_id, msg_part.file_size
                if file_info:
                    base, size = file_info[0], file_info[3]
                    if base in files_exist:
                        del files_exist[base]
                    else:
                        total_size += size
                        files_to_sync.append(file_info)

            for base, ext, fid, size in files_to_sync:
                path = os.path.join(files_dir, f"{base}.{ext}")
                await app.download_media(fid, path, progress=self.progress, progress_args=[size, total_size])
                if ext == "zip":
                    with zipfile.ZipFile(path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(files_dir, base))
                    os.remove(path)
            
            for key, val in files_exist.items():
                path = os.path.join(files_dir, val)
                try:
                    os.remove(path) if key != val else shutil.rmtree(path)
                except Exception as e:
                    print(f"Error removing file {path}: {e}")
            
            if files_to_sync or files_exist:
                os.popen("systemctl restart pibox-vlc.service &")
            
            result = {"status": "ok"}
        except Exception:
            traceback.print_exc()
        finally:
            running_task = None
        
        return result

    async def progress(self, current, total, size, total_size):
        """Tracks and sends progress updates for file downloads."""
        if current >= size:
            self.temp_size += size
            current = 0
        msg = {"status": "ok", "_type": "progress", "_data": {"current": round((self.temp_size+current)/(1024*1024), 2), "total": round(total_size/(1024*1024), 2)}}
        WebSocketServer.send_message(json.dumps(msg))

class WebSocketServer(tornado.websocket.WebSocketHandler):
    """Handles WebSocket connections for real-time updates."""
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
