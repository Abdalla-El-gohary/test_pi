import pynput

class KeyboardControl:
    def __init__(self):

        self.speeds = {'vx': 0.0, 'vy': 0.0, 'w': 0.0} 
        self.linear_speed = 0.5
        self.angular_speed = 0.5
        self.listener = pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try:
            if key.char == 'w':
                self.speeds['vx'] = self.linear_speed
            elif key.char == 's':
                self.speeds['vx'] = -self.linear_speed
            elif key.char == 'a':
                self.speeds['vy'] = -self.linear_speed
            elif key.char == 'd':
                self.speeds['vy'] = self.linear_speed
            elif key.char == 'q':
                self.speeds['w'] = self.angular_speed
            elif key.char == 'e':
                self.speeds['w'] = -self.angular_speed
            elif key.char == 'm':
                self.linear_speed = min(self.linear_speed + 0.05, 5.0)  # Limit speed
                self.angular_speed = min(self.angular_speed + 0.05, 5.0)
            elif key.char == 'n':
                self.linear_speed = max(self.linear_speed - 0.05, 0.05)  # Minimum speed
                self.angular_speed = max(self.angular_speed - 0.05, 0.05)
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key.char in ['w', 's']:
                self.speeds['vx'] = 0
            elif key.char in ['a', 'd']:
                self.speeds['vy'] = 0
            elif key.char in ['q', 'e']:
                self.speeds['w'] = 0
        except AttributeError:
            pass


    def return_speeds(self):
        return self.speeds
