#!/usr/bin/env python3 

import zmq
import json
import time
from keyboard.keyboard_control import KeyboardControl

keyboard = KeyboardControl()

# ZeroMQ Context and Publisher
context = zmq.Context()
publisher = context.socket(zmq.PUB)
host_ip = "192.168.242.77"
publisher.bind(f"tcp://{host_ip}:5556")  # Bind to a port for broadcasting

if __name__ == "__main__":
    last_speeds = {'vx': 0.0, 'vy': 0.0, 'w': 0.0}

    # Give time for subscribers to connect before sending first message
    time.sleep(0.1)
    publisher.send(json.dumps(last_speeds).encode("utf-8"))  

    try:
        while True:
            speeds = keyboard.return_speeds()
            
            # Compare values explicitly
            if speeds.get('vx', 0) != last_speeds.get('vx', 0) or \
               speeds.get('vy', 0) != last_speeds.get('vy', 0) or \
               speeds.get('w', 0) != last_speeds.get('w', 0):
                
                speeds_str = json.dumps(speeds)
                publisher.send(speeds_str.encode("utf-8"))  
                print(f"Speeds sent: {speeds}")

                # Properly copy dictionary
                last_speeds = speeds.copy()

            time.sleep(0.5)  # Control loop frequency
            
    except KeyboardInterrupt:
        print("Exiting keyboard publisher.")
    finally:
        publisher.close()
        context.term()
