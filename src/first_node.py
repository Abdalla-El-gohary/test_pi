#!/usr/bin/env python3 

import zmq
import json
import time
from keyboard.keyboard_control import KeyboardControl
keyboard = KeyboardControl()

# ZeroMQ Context and Publisher
context = zmq.Context()
publisher = context.socket(zmq.PUB)
pi_ip = "192.168.247.77"
publisher.bind("tcp://"+pi_ip+":5556")  # Bind to a port for broadcasting

if __name__ == "__main__":
    try:
        while True:
            speeds = keyboard.return_speeds()

            # Convert to list
            # speeds_list = list(speeds.values())
            # print(f"Speeds as List: {speeds_list}")

            # Convert list to string
            speeds_str = json.dumps(speeds)  
            print(f"Speeds as String: {speeds_str}")

            # Send as string
            publisher.send(speeds_str.encode("utf-8"))  
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("Exiting keyboard publisher.")
