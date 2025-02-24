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

# Features flags
acc_flag = True

# ZeroMQ Context and Sockets
context = zmq.Context()

host_eth_ip = "10.118.142.1"
host_ip= "192.168.66.77"

def setup_acc_socket():
    """Creates and connects the acc_socket."""
    global acc_socket
    acc_socket = context.socket(zmq.REQ)
    acc_socket.connect("tcp://localhost:5555")
    acc_socket.setsockopt(zmq.RCVTIMEO, 500)  # Timeout for receiving ACC speed

if acc_flag:
    setup_acc_socket()

speed_socket = context.socket(zmq.SUB)
speed_socket.connect("tcp://"+host_ip+":5556")  
speed_socket.setsockopt_string(zmq.SUBSCRIBE, '')  
speed_socket.setsockopt(zmq.RCVTIMEO, 500)  # Timeout for receiving speeds

def reconnect_acc_socket():
    """Reconnects to the ACC socket if disconnected."""
    global acc_socket
    print("Reconnecting to ACC socket...")
    acc_socket.close()
    setup_acc_socket()
    sleep(1)  # Allow time for reconnection

if __name__ == "__main__":
    try:
        while True:
            try:
                speeds_str = speed_socket.recv()
                speeds = json.loads(speeds_str.decode("utf-8"))
            except zmq.Again:
                print("Warning: No speed data received. Skipping this cycle.")
                continue  
            except json.JSONDecodeError:
                print("Warning: Invalid JSON data. Skipping this cycle.")
                continue

            if acc_flag:
                try:
                    acc_socket.send(b"GET_SPEED")
                    acc_speed = int(acc_socket.recv().decode())
                    speeds['vx'] = min(speeds['vx'], acc_speed)
                except zmq.Again:
                    print("Warning: No ACC speed received. Using last known speed.")
                except zmq.ZMQError:
                    print("Error: ACC socket in invalid state. Reconnecting...")
                    reconnect_acc_socket()
                except ValueError:
                    print("Warning: Invalid ACC speed received. Skipping update.")

            try:
                if robot.serial_connection.is_open:
                    robot.update_command(speeds.get('vx', 0), speeds.get('vy', 0), speeds.get('w', 0))
                    robot.send_speeds_to_serial()
                else:
                    print("Serial connection lost. Attempting to reconnect...")
                    robot.serial_connection.open()
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                sleep(1)

            sleep(0.3)
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        if robot.serial_connection.is_open:
            robot.serial_connection.close()
        speed_socket.close()
        if acc_flag:
            acc_socket.close()
        context.term()
