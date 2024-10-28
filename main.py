# main.py

import json
import time
import threading
import random  # Import random module
from actuators.servos import Servos
from comms.xbee_comm import XBeeComm  # Import the XBeeComm class
from initialization.config import load_config  # Import load_config

# Load configuration
config = load_config()
boat_name = config['boat_name']

# Global variables
command_mode = 'manual'
target_gps_latitude = None
target_gps_longitude = None

def main():
    global command_mode, target_gps_latitude, target_gps_longitude

    # Initialize actuators
    servos = Servos()

    # Initialize XBee communication
    xbee_comm = XBeeComm()

    # Send registration message
    registration_message = json.dumps({
        "type": "registration",
        "boat_name": boat_name
    })
    xbee_comm.send_data(registration_message)

    # Start heartbeat thread
    def heartbeat_loop():
        while True:
            heartbeat_message = json.dumps({
                "type": "heartbeat",
                "boat_name": boat_name
            })
            xbee_comm.send_data(heartbeat_message)
            time.sleep(10)  # Send heartbeat every 10 seconds

    threading.Thread(target=heartbeat_loop, daemon=True).start()

    # Start simulated GPS data thread
    def gps_simulation_loop():
        while True:
            try:
                # Generate random latitude and longitude within a reasonable range
                simulated_latitude = random.uniform(37.8600, 37.8700)  # Example range near Berkeley, CA
                simulated_longitude = random.uniform(-122.3200, -122.3100)
                gps_message = json.dumps({
                    "type": "location_update",
                    "boat_name": boat_name,
                    "location": {
                        "latitude": simulated_latitude,
                        "longitude": simulated_longitude
                    }
                })
                xbee_comm.send_data(gps_message)
                print(f"Sent simulated GPS data: {gps_message}")
            except Exception as e:
                print(f"Error in gps_simulation_loop: {e}")
            time.sleep(5)  # Send GPS data every 5 seconds


    threading.Thread(target=gps_simulation_loop, daemon=True).start()

    def data_receive_callback(xbee_message):
        global command_mode, target_gps_latitude, target_gps_longitude

        print("Received data: %s" % xbee_message.data.decode())
        try:
            # Decode the JSON message
            data = json.loads(xbee_message.data.decode())

            # Check if the message is intended for this boat
            target_boat_name = data.get('boat_name')
            if target_boat_name not in [boat_name, 'all']:
                # Message is not for this boat
                return

            # Extract command mode with a fallback to 'manual'
            command_mode = data.get('command_mode', 'manual')
            print(f"Command Mode: {command_mode}")

            if command_mode == 'manual':
                # Process manual mode data
                process_manual_mode(data, servos)
            elif command_mode == 'autonomous':
                # Process autonomous mode data
                process_autonomous_mode(data)
            else:
                print(f"Unknown command mode: {command_mode}")

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error decoding data: {e}")
            print("Invalid data received. Please send valid JSON.")

    # Set up the XBee to receive data
    xbee_comm.add_data_received_callback(data_receive_callback)

    print("Waiting for data...\n")

    try:
        while True:
            if command_mode == 'manual':
                # Manual mode logic (if any)
                pass
            elif command_mode == 'autonomous':
                # Autonomous mode logic (if any)
                pass
            else:
                print(f"Unknown command mode: {command_mode}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        xbee_comm.close()
        servos.cleanup()

def process_manual_mode(data, servos):
    try:
        # Extract angles for rudder, sail, and throttle with defaults
        rudder_angle = float(data.get('rudder_angle', 0))
        sail_angle = float(data.get('sail_angle', 0))
        throttle = float(data.get('throttle', 0))

        # Print the received angles
        print(f"Rudder Angle: {rudder_angle}, Sail Angle: {sail_angle}, Throttle: {throttle}")

        # Move the servos
        servos.set_rudder_angle(rudder_angle)
        servos.set_sail_angle(sail_angle)
        # Process throttle if needed

    except (ValueError, TypeError) as e:
        print(f"Error processing manual mode data: {e}")

def process_autonomous_mode(data):
    global target_gps_latitude, target_gps_longitude
    try:
        # Extract target GPS coordinates with defaults
        target_gps_latitude = float(data.get('target_gps_latitude', 0))
        target_gps_longitude = float(data.get('target_gps_longitude', 0))

        # Print the received target coordinates
        print(f"Target GPS Latitude: {target_gps_latitude}, Target GPS Longitude: {target_gps_longitude}")

        # Implement autonomous navigation logic here

    except (ValueError, TypeError) as e:
        print(f"Error processing autonomous mode data: {e}")

if __name__ == '__main__':
    main()
