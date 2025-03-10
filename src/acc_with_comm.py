#!/usr/bin/env python3 

from rp_lidar.rp_lidar import LidarInterface
from features.adaptive_cruise_control import AdaptiveCruiseControl
import time
import zmq

if __name__ == '__main__':
    lidar = LidarInterface(port='/dev/ttyUSB0')
    acc = AdaptiveCruiseControl(lidar)
    
    # ZeroMQ Context
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")  # Listen on port 5555

    try:
        lidar.start()
        while lidar.running:
            acc.update_speed()

            # Check if there's a request to avoid blocking
            if socket.poll(100):  # 100ms timeout
                message = socket.recv()
                if message == b"GET_SPEED":
                    socket.send(str(acc.current_speed).encode())

            time.sleep(0.2)
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        lidar.stop()
        socket.close()
        context.term()
