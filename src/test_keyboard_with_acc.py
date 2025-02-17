#!/usr/bin/env python3 

import serial
from keyboard.keyboard_control import KeyboardControl
from kinematics.model import kinematicModel
from robot_controller.controller import RobotController
from time import sleep
import zmq

# Model specifications
wheel_radius = 0.04  
lx = 0.13  
ly = 0.15  

my_port = "/dev/ttyUSB0"
my_baudrate = 115200

kinematic = kinematicModel(wheel_radius, lx, ly)
robot = RobotController(port=my_port, baudrate=my_baudrate, kinematics=kinematic)
keyboard = KeyboardControl()

# ZeroMQ Context and Socket
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # Connect to ACC Server

if __name__ == "__main__":
    try:
        while True:
            # Request speed from ACC
            socket.send(b"GET_SPEED")
            acc_speed = int(socket.recv().decode())
            print(f"ACC Speed: {acc_speed}")

            # Get keyboard inputs
            speeds = keyboard.return_speeds()

            # Override the vx (forward speed) with ACC speed
            speeds['vx'] = min(speeds['vx'], acc_speed)
            print(f"Speeds: {speeds}")

            robot.update_command(speeds['vx'], speeds['vy'], speeds['w'])
            robot.send_speeds_to_serial()

            sleep(0.1)
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        if robot.serial_connection.is_open:
            robot.serial_connection.close()
