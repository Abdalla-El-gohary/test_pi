#!/usr/bin/env python3 

import serial
from kinematics.model import kinematicModel
from robot_controller.controller import RobotController
from time import sleep
import zmq
import json  # Required for JSON parsing

# Model specifications
wheel_radius = 0.04  
lx = 0.13  
ly = 0.15  

my_port = "/dev/ttyUSB0"
my_baudrate = 115200

kinematic = kinematicModel(wheel_radius, lx, ly)
robot = RobotController(port=my_port, baudrate=my_baudrate, kinematics=kinematic)

# ZeroMQ Context and Sockets
context = zmq.Context()

pi_ip = "192.168.247.77"

# Socket for ACC speed
acc_socket = context.socket(zmq.REQ)
acc_socket.connect("tcp://"+pi_ip+":5555")  # Connect to ACC Server

# Socket for speed commands
speed_socket = context.socket(zmq.SUB)
speed_socket.connect("tcp://"+pi_ip+":5556")  # Connect to speed publisher
speed_socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages

if __name__ == "__main__":
    try:
        while True:
            # Receive speed commands from the publisher as a string
            speeds_str = speed_socket.recv()
            print(f"Received Speeds (String): {speeds_str}")
            
            # Convert the JSON string to a dictionary
            speeds = json.loads(speeds_str.decode("utf-8"))
            print(f"Received Speeds (Dict): {speeds}")

            # Request speed from ACC
            acc_socket.send(b"GET_SPEED")
            acc_speed = int(acc_socket.recv().decode())
            print(f"ACC Speed: {acc_speed}")

            # Override the vx (forward speed) with ACC speed
            speeds['vx'] = min(speeds['vx'], acc_speed)
            print(f"Final Speeds: {speeds}")

            # Update the robot's movement commands
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
