import pigpio
from time import sleep

#================================
#           PINS
#================================
PINS = {
    # arduino: D8,  channel 1
    'roll': {
        'gpio':26,
        'pulse': 1500
    },

    # arduino: D10,  channel 3
    'throttle': {
        'gpio':13,
        'pulse': 2000
    },

    # arduino: D9,  channel 2
    'pitch': {
        'gpio':19,
        'pulse': 1500
    },

    # arduino: D11,  channel 4
    'yaw': {
        'gpio':21,
        'pulse': 1500
    }
}

STEP = 10
STEP_INTERVAL = 0.01
#==================================
pi = pigpio.pi()
if not pi.connected:
    exit()
pi.set_servo_pulsewidth(PINS['roll']['gpio'], PINS['roll']['pulse'])
pi.set_servo_pulsewidth(PINS['throttle']['gpio'], PINS['throttle']['pulse'])
pi.set_servo_pulsewidth(PINS['pitch']['gpio'], PINS['pitch']['pulse'])
pi.set_servo_pulsewidth(PINS['yaw']['gpio'], PINS['yaw']['pulse'])

if __name__ == "__main__":
    while True:
        direction = input("direction:")
        value = int(input("value:"))
    
        current_direction = PINS[direction]
        current_value = current_direction["pulse"]
        step = STEP if (value > current_value) else -STEP
        for i in range(current_direction["pulse"], value, step): 
           pi.set_servo_pulsewidth(current_direction['gpio'], i)
           sleep(STEP_INTERVAL)
           
        current_direction["pulse"] = value
        print("value: ", pi.get_servo_pulsewidth(current_direction['gpio']))
