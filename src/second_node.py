#!/usr/bin/env python3 

import serial
from kinematics.model import kinematicModel
from robot_controller.controller import RobotController
from time import sleep
import zmq
import json  

# Model specifications
wheel_radius = 0.04  
lx = 0.13  
ly = 0.15  

my_port = "/dev/ttyUSB1"
my_baudrate = 115200

kinematic = kinematicModel(wheel_radius, lx, ly)
robot = RobotController(port=my_port, baudrate=my_baudrate, kinematics=kinematic)

# ZeroMQ Context
context = zmq.Context()

host_ip = "192.168.242.77"

# Set up Speed Subscriber (Non-Blocking)
speed_socket = context.socket(zmq.SUB)
speed_socket.connect(f"tcp://{host_ip}:5556")  
speed_socket.setsockopt_string(zmq.SUBSCRIBE, '')  
speed_socket.setsockopt(zmq.RCVTIMEO, 500)  # Timeout for receiving speeds
speed_socket.setsockopt(zmq.LINGER, 0)  # Prevents blocking on exit

# Adaptive Cruise Control (ACC) Requester
acc_socket = context.socket(zmq.REQ)
acc_socket.connect("tcp://localhost:5555")  
acc_socket.setsockopt(zmq.RCVTIMEO, 500)  # 500ms timeout to prevent blocking
acc_socket.setsockopt(zmq.LINGER, 0)

# Use a poller to avoid blocking
poller = zmq.Poller()
poller.register(speed_socket, zmq.POLLIN)
poller.register(acc_socket, zmq.POLLIN)

if __name__ == "__main__":
    try:
        while True:
            speeds = {'vx': 0, 'vy': 0, 'w': 0}  # Default speed values

            # Check if speed data is available
            try:
                socks = dict(poller.poll(500))  # Wait for 500ms
                if speed_socket in socks:
                    speeds_str = speed_socket.recv()
                    speeds = json.loads(speeds_str.decode("utf-8"))
            except zmq.Again:
                print("No speed data received. Skipping this cycle.")
            except json.JSONDecodeError:
                print("Invalid JSON data. Skipping.")

            # Request ACC speed if needed
            try:
                acc_socket.send(b"GET_SPEED")
                if acc_socket in socks:
                    acc_speed = int(acc_socket.recv().decode())
                    speeds['vx'] = min(speeds['vx'], acc_speed)  # Limit speed
            except zmq.Again:
                print("ACC speed request timed out.")
            except ValueError:
                print("Invalid ACC speed received.")

            # Send speeds to the robot
            try:
                if robot.serial_connection.is_open:
                    robot.update_command(speeds['vx'], speeds['vy'], speeds['w'])
                    robot.send_speeds_to_serial()
                else:
                    print("Serial connection lost. Attempting to reconnect...")
                    robot.serial_connection.open()
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                sleep(1)

            sleep(0.3)
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        speed_socket.close()
        acc_socket.close()
        context.term()
