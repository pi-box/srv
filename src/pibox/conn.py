import tornado.web
import os
import json
from urllib import request

class ConnHandler(tornado.web.RequestHandler):
    """
    Connection Handler for checking internet connectivity.
    
    This class provides an API endpoint to verify whether the device is connected to the internet.
    It attempts to reach 'http://google.com' and returns the connection status.
    
    Endpoint:
    - GET `/conn/`: Returns a JSON response with `status` and `connected` fields.
    
    Example Response:
    ```json
    {
        "status": "ok",
        "connected": true
    }
    ```
    """
    
    async def get(self):
        """
        Handles HTTP GET requests to check internet connectivity.
        
        Returns:
        - JSON object with `status` ("ok") and `connected` (True/False)
        """
        self.set_header("Access-Control-Allow-Origin", "*")
        
        try:
            request.urlopen('http://google.com', timeout=1)
            result = True  # Connection is available
        except request.URLError:
            result = False  # No connection
        except Exception as err:
            result = False
            print(f"Error checking internet connection: {err}")
        
        response = {"status": "ok", "connected": result}
        self.write(json.dumps(response))
        self.flush()
