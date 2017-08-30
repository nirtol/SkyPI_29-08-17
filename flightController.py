# USAGE
# python object_movement.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import time
import pigpio
from time import sleep
import os

# ==========================================
#   Constants
# ==========================================
PIGPIO_CONNECTION_ERROR = "Error!! could not connect to pigpio. exiting..."
# ================================
#           PINS
# ================================
PINS = {
    # arduino: D8,  channel 1
    'roll': {
        'gpio': 26,
        'pulse': 1500
    },

    # arduino: D10,  channel 3
    'throttle': {
        'gpio': 13,
        'pulse': 1500
    },

    # arduino: D9,  channel 2
    'pitch': {
        'gpio': 19,
        'pulse': 1500
    },

    # arduino: D11,  channel 4
    'yaw': {
        'gpio': 21,
        'pulse': 1500
    }
}

STEP = 10
STEP_INTERVAL = 0.01


# =================================
#   Classes
# =================================
class FlightController:
    def __init__(self):
        #       os.system('sudo pigpiod')
        self.pins = PINS
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print (PIGPIO_CONNECTION_ERROR, "\n")
            exit()

        self.pi.set_servo_pulsewidth(self.pins['roll']['gpio'], self.pins['roll']['pulse'])
        self.pi.set_servo_pulsewidth(self.pins['throttle']['gpio'], self.pins['throttle']['pulse'])
        self.pi.set_servo_pulsewidth(self.pins['pitch']['gpio'], self.pins['pitch']['pulse'])
        self.pi.set_servo_pulsewidth(self.pins['yaw']['gpio'], self.pins['yaw']['pulse'])

    def self_debug(self):
        print (self)

    def write_to_pin(self, direction, value):
        if value < 1000:
            value = 1000
        if value > 2000:
            value = 2000
        current_direction = PINS[direction]
        current_value = current_direction["pulse"]
        step = STEP if (value > current_value) else -STEP
        for i in range(current_direction["pulse"], value, step):
            self.pi.set_servo_pulsewidth(current_direction['gpio'], i)
            sleep(STEP_INTERVAL)

        current_direction["pulse"] = value

    def write_to_arduino(self, new_status):
        self.write_to_pin('throttle', new_status['throttle'])
        self.write_to_pin('yaw', new_status['yaw'])
        self.write_to_pin('pitch', new_status['pitch'])
        self.write_to_pin('roll', new_status['roll'])



