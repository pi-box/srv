# Pi-Box

## Overview

Pi-Box is a Raspberry Pi-based multimedia system that synchronizes media files from a Telegram group and plays them on a connected display. It provides REST API endpoints for managing WiFi, media synchronization, and device connectivity.

The `public/` directory contains the web-based management interface for Pi-Box. The frontend source code is available at [Pi-Box UI Repository](http://github.com/pi-box/ui).

## Project Structure

This project contains the following Python modules:

### 1. `srv.py` - **Server Initialization**

- Starts the Pi-Box web server using Tornado.
- Routes requests to handlers for WiFi, media synchronization, WebSockets, and connection status.

### 2. `conn.py` - **Internet Connection Handler**

- Provides an API to check whether the device is connected to the internet.
- **Endpoint:** `GET /conn/` - Returns connection status.

### 3. `wifi.py` - **WiFi Management**

- Scans available WiFi networks and allows connecting to a specified network.
- **Endpoints:**
  - `GET /wifi/` - Returns a list of available networks.
  - `GET /wifi/?ssid=<SSID>&pwd=<PASSWORD>` - Connects to a specified network.

### 4. `sync.py` - **Media Synchronization**

- Synchronizes media files from a Telegram group.
- Sends WebSocket updates for progress tracking.
- **Endpoints:**
  - `GET /sync/` - Triggers full synchronization.
  - `GET /sync/status` - Checks sync status.

## API Documentation

```yaml
openapi: 3.0.0
info:
  title: Pi-Box API
  version: 1.0.0
servers:
  - url: http://localhost
paths:
  /conn/:
    get:
      summary: Check internet connection
      responses:
        '200':
          description: Connection status
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  connected:
                    type: boolean
  /wifi/:
    get:
      summary: List available WiFi networks
      parameters:
        - name: ssid
          in: query
          schema:
            type: string
        - name: pwd
          in: query
          schema:
            type: string
      responses:
        '200':
          description: WiFi networks or connection status
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  ssids:
                    type: array
                    items:
                      type: string
  /sync/:
    get:
      summary: Trigger media synchronization
      responses:
        '200':
          description: Sync status
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
  /sync/status:
    get:
      summary: Check sync status
      responses:
        '200':
          description: Current synchronization status
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
```

## Installation and Usage

To set up Pi-Box, follow the installation guide in `README.md`. The API endpoints can be tested using tools like Postman or cURL.

## License

This project is licensed under the MIT License.

