#!/usr/bin/env python3 

import serial
import pynput
import struct
from keyboard.keyboard_control import KeyboardControl
from kinematics.model import kinematicModel
from robot_controller.controller import RobotController
from time import sleep



# Model specifications
wheel_radius = 0.04  # Wheel diameter = 15.2 cm
lx = 0.13  # Horizontal distance from the robot center
ly = 0.15  # Vertical distance from the robot center

my_port = "/dev/ttyUSB0"
my_baudrate = 115200



kinematic = kinematicModel(wheel_radius, lx, ly)
robot = RobotController(port=my_port, baudrate=my_baudrate, kinematics=kinematic)
keyboard = KeyboardControl()

if __name__ == "__main__":
    try:
        while True:
            speeds = keyboard.return_speeds()
            robot.update_command(speeds['vx'], speeds['vy'], speeds['w'])
            robot.send_speeds_to_serial()
            sleep(2)
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        # Close the serial connection gracefully
        if robot.serial_connection.is_open:
            robot.serial_connection.close()





