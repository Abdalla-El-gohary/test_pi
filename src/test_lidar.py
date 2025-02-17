#!/usr/bin/env python3 

from rp_lidar.rp_lidar import LidarInterface
import time

if __name__ == '__main__':
    lidar = LidarInterface(port='/dev/ttyUSB0')  # Change to your port (e.g., '/dev/ttyUSB0' on Linux)
    try:
        lidar.start()
        # lidar.visualize()

        while True and lidar.running:
            print('Distances:', lidar.get_distances())
            print('Rate & RPM:', lidar.get_device_speed())
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        print('Stopping... finally')
        lidar.stop()