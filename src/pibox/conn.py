import tornado.web
import os, json
from urllib import request

class ConnHandler(tornado.web.RequestHandler):

  async def get(self):
    self.set_header("Access-Control-Allow-Origin", "*")
    try:
      request.urlopen('http://google.com', timeout=1)
      result = True
    except request.URLError as err: 
      result = False
    except Exception as err:
      result = False
      print(err)

    result = {"status":"ok", "connected":result}
    self.write(json.dumps(result))
    self.flush()
    
    





