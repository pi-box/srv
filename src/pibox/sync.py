import os, json
import asyncio
import traceback 
import shutil
import zipfile
import requests
import tornado.web, tornado.gen
import tornado.websocket
from pyrogram import Client, filters

running_task = None
app = Client("telegram")
app.start()

class SyncHandler(tornado.web.RequestHandler):
  def initialize(self):
    self.cid = -1

  @app.on_message(filters.chat(-1002127759899))
  @app.on_deleted_messages(filters.chat(-1002127759899))
  @app.on_edited_message(filters.chat(-1002127759899))
  async def on_message(client, message):
    result = await asyncio.to_thread(requests.get, 'http://localhost/sync/')

  async def get(self, param=None):
    self.set_header("Access-Control-Allow-Origin", "*")
    if param == None:
      result = await self.sync()
      msg = result.copy()
      msg["_type"] = "complete"
      msg = json.dumps(msg)
      WebSocketServer.send_message(msg)
    elif param == "status":
      result = {'status': 'ok'}
    else:
      raise tornado.web.HTTPError(400)
      
    self.write(json.dumps(result))
    self.flush()

  async def sync(self):
    result = result = {'status': 'error', '_msg':'ארעה תקלה, אנא נסה שוב!'}

    global running_task
    while True:
      if running_task is None:
        running_task = asyncio.current_task()
      if asyncio.current_task() == running_task:
        break
      await asyncio.gather(running_task)

    try:
      files_dir = "files"
      if os.path.exists(files_dir):
        files_exist = {file.split('.')[0]: file for file in os.listdir(files_dir)}
        if "System Volume Information" in files_exist: del files_exist["System Volume Information"] 
      else:
        files_exist = {}

      files_to_sync = []
      if self.cid < 0:
        gid = "t.me/+z11PczkD0iU0YTQ8"
        chat = await app.get_chat(gid)
        if "ChatPreview" in str(type(chat)):
          chat = await app.join_chat(gid)
        self.cid = chat.id

      total_size = 0
      self.temp_size = 0
      async for msg in app.get_chat_history(self.cid):
        file_info = None
        if not msg.caption or "ignore" not in msg.caption:
          if msg.photo:
            file_info = msg.photo.file_unique_id, "jpg", msg.photo.file_id, msg.photo.file_size
          else:
            msg_part = None
            if msg.document: msg_part = msg.document
            elif msg.video: msg_part = msg.video
            elif msg.animation: msg_part = msg.animation
            if msg_part:
              file_info = msg_part.file_unique_id, msg_part.mime_type.split('/')[1], msg_part.file_id, msg_part.file_size
        if file_info:
          base, size = file_info[0], file_info[3]
          if base in files_exist.keys():
            del files_exist[base]
          else:
            total_size += size
            files_to_sync.append(file_info)

      for file in files_to_sync:
        base, ext, fid, size = file
        path = os.path.join(files_dir, f"{base}.{ext}")
        await app.download_media(fid, path, progress=self.progress, progress_args=[size, total_size])
        if ext == "zip":
          with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_dir = os.path.join(base_dir, files_dir, base)
            zip_ref.extractall(zip_dir)
          os.remove(path)
       
      for key, val in files_exist.items():
        path = os.path.join(files_dir, val)
        if key == val:
          shutil.rmtree(path)
        else:
          os.remove(path)

      if len(files_to_sync) > 0 or len(files_exist) > 0:
        os.popen("systemctl stop pibox-vlc.service && systemctl start pibox-vlc.service &")

      result = {"status":"ok"}
    except Exception:
      traceback.print_exc()
    finally:
      running_task = None

    return result

  async def progress(self, current, total, size, total_size):
    if current >= size:
      self.temp_size += size
      current = 0
    msg = {'status': 'ok', '_type': 'progress', '_data': {'current': round((self.temp_size+current)/(1024*1024), 2), 'total': round(total_size/(1024*1024), 2)}}
    msg = json.dumps(msg)
    WebSocketServer.send_message(msg)

class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set()
    def check_origin(self, origin):
      return True
      
    def open(self):
      print("Client was connected!")
      WebSocketServer.clients.add(self)

    def on_close(self):
      print("Client was disconnected!")
      WebSocketServer.clients.remove(self)

    @classmethod
    def send_message(cls, message):
      for client in cls.clients:
        client.write_message(message)

    def on_message(self, message):
      pass
