from rplidar import RPLidar
import threading
from os import path  # to check if LIDAR is connected

from datetime import datetime  # to get the current time and display it
import time

import numpy as np # for numerical operations
import matplotlib.pyplot as plt # for visualization
import matplotlib.animation as animation

class LidarInterface:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1 ,min_range=0, max_range=13000, enable_visualization=True):
        ''' Initializes the Lidar interface '''
        if not path.exists(port):  # Check if the Lidar is connected
            print('[Error] Could not found device: {0}'.format(port))
            raise Exception('Lidar not connected to port:', port)

        # initialize the Lidar
        self.port = port
        self.lidar = RPLidar(port=self.port, baudrate=baudrate, timeout=timeout)
        self.max_range = max_range  # Maximum range of the Lidar in meters
        self.min_range = min_range  # Maximum range of the Lidar in meters
        self.scan_data = [0] * 360
        self.rate = 0  # Lidar rate in Hz
        self.rpm = 0  # Lidar speed in RPM
        self.delta_time = [] # To store delta time between scans to calculate the rate and RPM

        # Thread Control (Used to always get the latest data of the Lidar)
        self.running = False        
        self.thread = threading.Thread(target=self.extract_data , daemon=True)

        # Visualization
        self.enable_visualization = enable_visualization
        if self.enable_visualization:
            self.scan_store = []

    def get_info(self):
        ''' Returns the Lidar information '''
        print('\n{:*^50s}'.format(" Lidar Status "))
        print('Found device : {0}'.format(self.port))

        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('Date & Time  : {0}'.format(date_time))

        info = self.lidar.get_info()
        for key, value in info.items():
            print('{0:<13}: {1}'.format(key.capitalize(), str(value)))

        health = self.lidar.get_health()
        print('Health Status: {0[0]} - {0[1]}'.format(health))
        print('*' * 50)

    def get_device_speed(self):
        ''' Returns the Lidar speed '''
        return self.rate, self.rpm

    def extract_data(self):
        ''' Extracts scan data from Lidar '''
        old_time = None
        try:
            for scan in self.lidar.iter_scans():
                if self.enable_visualization:
                    self.scan_store.append(scan)
                    if (len(self.scan_store) > 5):
                        self.scan_store.pop(0)

                for (_, angle, distance) in scan:
                    if (distance > self.min_range) and (distance < self.max_range) and (angle < 360) and (angle >= 0):
                        self.scan_data[min([359, int(angle)])] = distance

                if (len(self.delta_time) < 10):
                    now = time.time()
                    if not old_time:
                        old_time = now
                        continue
                    delta_time = now - old_time
                    self.delta_time.append(delta_time)
                    old_time = now

                if (len(self.delta_time) == 10):
                    delta_time_avg = sum(self.delta_time) / len(self.delta_time)
                    self.rate = 1 / delta_time_avg
                    self.rpm = 60 / delta_time_avg
                    
        except Exception as e:
            print('Error:', e)
            self.stop()

    def get_distance(self, angle):
        ''' Returns the distance at a specific angle '''
        return self.scan_data[angle]
    
    def get_distances(self):
        ''' Returns distances at 0, 90, 180, and 270 degrees '''
        return {
            '0°': self.get_distance(0),
            '90°': self.get_distance(90),
            '180°': self.get_distance(180),
            '270°': self.get_distance(270)
        }

    def update_visualization(self, num, line):
        ''' Updates the visualization for the animation '''
        if len(self.scan_store) > 0:
            scan = self.scan_store[-1]  # Get the latest scan data
            offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
            line.set_offsets(offsets)
            intents = np.array([meas[0] for meas in scan])
            line.set_array(intents)
        return line

    def visualize(self):
        ''' Visualizes the Lidar data in polar coordinates '''
        if self.enable_visualization:
            DMAX: int = 4000
            IMIN: int = 0
            IMAX: int = 50
            try:
                fig = plt.figure()
                title = 'RPLIDAR'
                fig.set_label(title)
                fig.canvas.manager.set_window_title(title)

                ax = plt.subplot(111, projection='polar')
                line = ax.scatter([0, 0], [0, 0], s=5, c=[IMIN, IMAX], cmap=plt.cm.Greys_r, lw=0)
                ax.set_title('360° scan result')
                ax.set_rmax(DMAX)
                ax.grid(True)

                ani = animation.FuncAnimation(fig, self.update_visualization, fargs=(line,), interval=50)

                plt.show()
            except Exception as e:
                print('Error:', e)
                self.stop()
        else:
            print('Visualization is disabled')

    def start(self):
        if not self.running:
            self.running = True
            self.thread.start()
        time.sleep(2)  # Wait for the Lidar to initialize and start scanning

    def stop(self):
        ''' Stops the Lidar safely '''
        self.running = False
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()

if __name__ == '__main__':
    lidar = LidarInterface(port='/dev/ttyUSB0')  # Change to your port (e.g., '/dev/ttyUSB0' on Linux)
    try:
        lidar.start()
        lidar.visualize()

        while True and lidar.running:
            print('Distances:', lidar.get_distances())
            print('Rate & RPM:', lidar.get_device_speed())
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        print('Stopping... finally')
        lidar.stop()
