# Warehouse Management System

A Python based, event-driven application modeling warehouse operations such as inventory tracking, order processing and alerts. Includes an AGV controller and RFID sensor simulation for item movement.

for more detailed information: https://shorturl.at/oaZd5

## Features
- **Inventory Tracker** manages item quantities, raises low-stock alerts.
- **Order Processor** handles new orders, approves them if stock is available.
- **AGV Controller** simulates an automated guided vehicle for item transfer.
- **RFID Sensor** detects arrivals/departures of stock items.
- **Alert System** logs and displays critical events (e.g., low stock or AGV errors).

**to run project**:  
   ```bash
   Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
python -m src.app


```
