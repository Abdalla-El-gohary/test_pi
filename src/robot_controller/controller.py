#!/usr/bin/env python3

import serial
import struct
import numpy as np

class RobotController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, kinematics=None):
        self.serial_connection = serial.Serial(port, baudrate, timeout=1000)
        self.kinematics = kinematics
        self.command = {'vx': 0.0, 'vy': 0.0, 'w': 0.0}
        self.linear_speed = 0.1
        self.angular_speed = 0.1

    def calculate_wheel_speeds(self):
        wheel_speeds = self.kinematics.mecanum_4_vel_forward(
            self.command['vx'], self.command['vy'], self.command['w']
        )
        int8_speeds = np.clip(wheel_speeds, -128, 127).astype(np.int8)
        return int8_speeds

    def send_speeds_to_serial(self):
        speeds = self.calculate_wheel_speeds()
        # print(f"Speeds: {speeds}")
        data = struct.pack('4b', *speeds)
        if self.serial_connection.is_open:
            try:
                self.serial_connection.write(data)
                received = self.serial_connection.read(4)
                if len(received) == 4:
                    signed_bytes = [int.from_bytes([byte], byteorder='little', signed=True) for byte in received]
                    # print(f"Received Bytes: {signed_bytes}")
                else:
                    print("No data received or insufficient bytes.")
                    
             

                print(f"Sent speeds: {speeds}")
                #print(f"received speeds :{received}")
            except Exception as e:
                print(f"Error sending data: {e}")
        else:
            print("Serial connection is not open.")


    def update_command(self, vx, vy, w):
        self.command['vx'] = vx
        self.command['vy'] = vy
        self.command['w'] = w

