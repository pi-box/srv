#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import tornado.web
from tornado.ioloop import IOLoop

from pibox.wifi import WifiHandler
from pibox.sync import SyncHandler, WebSocketServer
from pibox.conn import ConnHandler

import subprocess

#base_dir = getattr(sys, '_MEIPASS', os.getcwd())
base_dir = os.path.dirname(os.path.abspath(__file__))

def main():
  print(f"Starting pibox srv")
  web = tornado.web.Application([(r"/wifi/", WifiHandler),
                                 (r"/sync/", SyncHandler),
                                 (r"/sync/([^/]+)", SyncHandler),
                                 (r"/websocket/", WebSocketServer),
                                 (r"/conn/", ConnHandler),
                                 (r"/(.*)",tornado.web.StaticFileHandler, {"path": os.path.join(base_dir, "public"), "default_filename": "index.html"})],
                                websocket_ping_interval=10, websocket_ping_timeout=30,)
  web.listen(80)
  io_loop = IOLoop.current()
  io_loop.start()
