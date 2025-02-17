#!/usr/bin/env python3 

from rp_lidar.rp_lidar import LidarInterface
from features.adaptive_cruise_control import AdaptiveCruiseControl
import time
import zmq

if __name__ == '__main__':
    lidar = LidarInterface(port='/dev/ttyUSB1')
    acc = AdaptiveCruiseControl(lidar)
    
    # ZeroMQ Context and Socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")  # Listen on port 5555

    try:
        lidar.start()
        while lidar.running:
            acc.update_speed()

            # Wait for a request from the Movement Controller
            message = socket.recv()
            if message == b"GET_SPEED":
                # Send the current speed to the Movement Controller
                socket.send(str(acc.current_speed).encode())
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        lidar.stop()
