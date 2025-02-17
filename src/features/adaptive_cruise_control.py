
import time

class AdaptiveCruiseControl:
    def __init__(self, lidar, safe_distance=2000, max_speed=2.5, min_speed=0):
        ''' Initializes the Adaptive Cruise Control '''
        self.lidar = lidar
        self.safe_distance = safe_distance  # Safe following distance in mm
        self.max_speed = max_speed          # Maximum speed
        self.min_speed = min_speed          # Minimum speed (0 for stop)
        self.current_speed = 0              # Current speed of the vehicle

    def calculate_speed(self, distance):
        ''' Calculates the speed based on the distance to the object in front '''
        if distance < self.safe_distance:
            # Object is too close, slow down
            speed = max(self.min_speed, self.max_speed * (distance / self.safe_distance))
        else:
            # Safe to accelerate
            speed = self.max_speed
        return int(speed)
    
    def update_speed(self):
        ''' Updates the speed of the vehicle '''
        distance = self.lidar.get_distance(0)  # Get the distance at 0° (front)
        if distance == 0:
            print('[Warning] No object detected. Assuming clear path.')
            distance = self.safe_distance
        
        self.current_speed = self.calculate_speed(distance)
        print(f'Distance to Object: {distance} mm | Speed: {self.current_speed} cm/s')

    def run(self):
        ''' Runs the Adaptive Cruise Control '''
        while self.lidar.running:
            self.update_speed()
            time.sleep(0.1)  # Adjust the update rate as needed
