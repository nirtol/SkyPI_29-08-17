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
        'pulse': 1500
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
pi.set_servo_pulsewidth(PINS['roll']['gpio'], PINS['roll']['pulse'])
pi.set_servo_pulsewidth(PINS['throttle']['gpio'], PINS['throttle']['pulse'])
pi.set_servo_pulsewidth(PINS['pitch']['gpio'], PINS['pitch']['pulse'])
pi.set_servo_pulsewidth(PINS['yaw']['gpio'], PINS['yaw']['pulse'])
print("global")

def set_value(msg, direction, value, parallel):
    if not parallel:
        raw_input("Press enter to: " + msg)
        
    current_direction = PINS[direction]
    current_value = current_direction["pulse"]
    step = STEP if (value > current_value) else -STEP
    for i in range(current_direction["pulse"], value, step): 
        pi.set_servo_pulsewidth(current_direction['gpio'], i)
        sleep(STEP_INTERVAL)
    
    current_direction["pulse"] = value
    
if __name__ == "__main__":
    print("main")
    # --> check movements
    set_value('Throttle up', 'throttle', 2000, False)
    set_value('Throttle center', 'throttle', 1500, False)
    
    set_value('Roll left', 'roll', 2000, False)
    set_value('Roll center', 'roll', 1500, False)
    
    set_value('Pitch forward', 'pitch', 1000, False)
    set_value('Pitch center', 'pitch', 1500, False)
    
    set_value('Yaw right', 'yaw', 2000, False)
    set_value('Yaw center', 'yaw', 1500, False)

    # --> set extends
    set_value('Throttle up', 'throttle', 2000, True)
    set_value('Roll left', 'roll', 2000, True)
    set_value('Pitch backward', 'pitch', 2000, True)
    set_value('Yaw right', 'yaw', 2000, True)
    sleep(0.5)
    set_value('Throttle Down', 'throttle', 1000, True)
    set_value('Roll right', 'roll', 1000, True)  
    set_value('Pitch forward', 'pitch', 1000, True)
    set_value('Yaw left', 'yaw', 1000, True)
    sleep(0.5)
    set_value('Throttle center', 'throttle', 1500, True)
    set_value('Roll center', 'roll', 1500, True)
    set_value('Pitch center', 'pitch', 1500, True)
    set_value('Yaw center', 'yaw', 1500, True)

    # --> gyro
    set_value('Nose up', 'pitch', 1000, False)
    set_value('Back to center', 'pitch', 1500, False)
    set_value('Nose up', 'pitch', 1000, False)
    set_value('Back to center', 'pitch', 1500, False)
    set_value('Nose up', 'pitch', 1000, False)
    set_value('Back to center', 'pitch', 1500, False)
    set_value('Nose up', 'pitch', 1000, False)
    set_value('Back to center', 'pitch', 1500, False)
    
