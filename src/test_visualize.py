#!/usr/bin/env python3 

from rp_lidar.rp_lidar import LidarInterface
import time

if __name__ == '__main__':
    lidar = LidarInterface(port='/dev/ttyUSB0')  # Change to your port (e.g., '/dev/ttyUSB0' on Linux)
    try:
        lidar.start()
        lidar.visualize()

        
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        print('Stopping... finally')
        lidar.stop()