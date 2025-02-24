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

# features flags
acc_flag = True

# ZeroMQ Context and Sockets
context = zmq.Context()

host_eth_ip = "10.118.142.1"
host_ip= "192.168.66.77"

if acc_flag:
    acc_socket = context.socket(zmq.REQ)
    acc_socket.connect("tcp://localhost:5555")  
    poller = zmq.Poller()
    poller.register(acc_socket, zmq.POLLIN)

speed_socket = context.socket(zmq.SUB)
speed_socket.connect("tcp://"+host_ip+":5556")  
speed_socket.setsockopt_string(zmq.SUBSCRIBE, '')  

if __name__ == "__main__":
    try:
        while True:
            speeds_str = speed_socket.recv()
            speeds = json.loads(speeds_str.decode("utf-8"))
            
            if acc_flag:
                acc_socket.send(b"GET_SPEED")
                socks = dict(poller.poll(500))  
                if acc_socket in socks and socks[acc_socket] == zmq.POLLIN:
                    acc_speed = int(acc_socket.recv().decode())
                    speeds['vx'] = min(speeds['vx'], acc_speed)
            
            robot.update_command(speeds['vx'], speeds['vy'], speeds['w'])
            robot.send_speeds_to_serial()
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