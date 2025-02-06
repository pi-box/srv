#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import tornado.web
import os, json
import subprocess
import codecs

class WifiHandler(tornado.web.RequestHandler):
  def getSsids(self):
    ssids = None
    if os.name == 'nt':
      results = subprocess.check_output(["netsh", "wlan", "show", "network"])
      results = results.decode("cp1252").replace("\r","").split("\n")[4:-1]
      ssids = [result.split(":")[1].strip() for result in results if "SSID" in result]
    else:
      results = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"])
      results = results.decode().split("\n")
      ssids = [result.split(":")[1].strip("\"") for result in results if "ESSID" in result]
      ssids = [codecs.escape_decode(ssid)[0].decode('utf-8') for ssid in ssids if ssid]
      ssids = list(set(ssids))
     
    return ssids

  async def get(self):
    self.set_header("Access-Control-Allow-Origin", "*")
    result = None
    if self.get_argument("ssid", ""):
      ssid = self.get_argument("ssid", "")
      pwd = self.get_argument("pwd", "")
      os.popen("sudo nmcli d wifi connect %s password %s ifname wlan0" % (ssid, pwd))
      try:
        #os.popen("sudo reboot")
        result = {"status":"ok"}
      except OSError as ose:
        result = {"status":"error", "msg": "wlan0 Reconfigure Error"}
      
    else:
      result = {"status":"ok", "ssids":self.getSsids()}
    
    self.write(json.dumps(result))
    self.flush()
