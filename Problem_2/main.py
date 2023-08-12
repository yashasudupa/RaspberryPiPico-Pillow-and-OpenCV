"""This is the main script of Problem

This scripts configures the stepper motor and controls the stepper motor,
based on the input that it recevies from the system.
This script interfaced with the "UART_uc_to_Host"
python code for serial input output capability.
"""

"""Pins of Raspberry Pico are configured to drive stepper motor"""


from machine import Pin, Timer
import utime
from UART_uc_to_Host import serial_io
dir_pin = Pin(27, Pin.OUT)
step_pin = Pin(26, Pin.OUT)
steps_per_revolution = 6400
pin_m2 = Pin(20, mode=Pin.OUT)
pin_m1 = Pin(19, mode=Pin.OUT)
pin_m0 = Pin(18, mode=Pin.OUT)
pin_fault = Pin(14, mode=Pin.IN)

"""
Set pins such a way that it sets to 36 microsteps/step mode
26 -> M2
25 -> M1
24 -> M0
"""
pin_m2.on()
pin_m1.on()
pin_m0.on()

pin_A_plus = Pin(4, mode=Pin.IN)
pin_Z_plus = Pin(5, mode=Pin.IN)
pin_Z_minus = Pin(10, mode=Pin.IN)
pin_B_plus = Pin(11, mode=Pin.IN)
pin_A_minus = Pin(12, mode=Pin.IN)
pin_B_minus = Pin(13, mode=Pin.IN)

one_whole_revolution = 360
# Initialize timer
tim = Timer()


"""Callback function that is executed whenever the timer is elapsed. Step() : Step pin is controlled".

    Args: t 
    Returns : None
        
""" 

def step(t):
    global step_pin
    step_pin.value(not step_pin.value())


"""Helper Method : Stepper motor is rotated based as per the given angle

    Args: delay  
    Returns : None 
        
""" 

def rotate_motor(delay):
    try:
        # Set up timer for stepping
        tim.init(freq=1000000//delay, mode=Timer.PERIODIC, callback=step)
    except:
        print("rotate_motor : delay could be large")
        pass        

"""Helper Method : Conversion of angle into its respective steps_per_revolution is implemented

    Args: angle  
    Returns : Respective steps per revolution
        
"""


def angle_to_step_per_revolution_conversion(angle):
    try:
        #If negative angle is received as input, direction pin is set to 1
        if (angle < 0):
           angle = angle * (-1)
           dir_pin.value(1)
           print('dir_pin value is 1')
        else:
            #If positive angle is received as input, direction pin is set to 0
           dir_pin.value(0)
           print('dir_pin value is 0')
        
        global one_whole_revolution, steps_per_revolution
        
        #Angle to step per revolution conversion is implemented
        steps_per_revolution_result = ((steps_per_revolution * angle)/one_whole_revolution)
        print('angle_to_step_per_revolution_conversion - steps_per_revolution_result : ', steps_per_revolution_result)
        #if steps_per_revolution_result >= 1000000
        return steps_per_revolution_result
    except:
        print("angle_to_step_per_revolution_conversion -Invalid input")
        pass        


"""Helper Method : Enters into infinite loop and drives the stepper motor and provide encoder values as per the input from host system

    Args: serial communication instance  
    Returns : None
        
"""

def loop(serial_com):
    while True:
        print("loop : Entered inside while loop")
        try:
            angle = int(serial_com.wait_for_input())
            print("loop : angle", angle)
        except:
            print("loop : Exception, pass")
            pass
        
        if angle == "Invalid Input":
            print("loop : Invalid Input")
            continue
        
        steps_per_revolution_result = angle_to_step_per_revolution_conversion(angle)
        # Spin motor slowly
        
        try:
            rotate_motor(500)
            utime.sleep_ms(int(steps_per_revolution_result))
        except:
            pass
        
        #Read Encoder and pin fault Values
        print(f'pin_fault value is {pin_fault.value()}')
        print(f'pin_A_plus value is {pin_A_plus.value()}')
        print(f'pin_Z_plus value is {pin_Z_plus.value()}')
        print(f'pin_Z_minus value is {pin_Z_minus.value()}')
        print(f'pin_B_plus value is {pin_B_plus.value()}')
        print(f'pin_A_minus value is {pin_A_minus.value()}')
        print(f'pin_B_minus value is {pin_B_minus.value()}')
        
        utime.sleep(0.25)
            
        # stop the timer
        tim.deinit()  
        utime.sleep(1)

"""main() : Main function """
def main():
    try:
        serial_com = serial_io()
        
        home_steps_per_revolution = angle_to_step_per_revolution_conversion(100)
        rotate_motor(500)
        print('main : home angle', 100)
        utime.sleep_ms(int(home_steps_per_revolution))
        
        #Read Home Encoder Values
         
        print(f'pin_A_plus value is {pin_A_plus.value()}')
        print(f'pin_Z_plus value is {pin_Z_plus.value()}')
        print(f'pin_Z_minus value is {pin_Z_minus.value()}')
        print(f'pin_B_plus value is {pin_B_plus.value()}')
        print(f'pin_A_minus value is {pin_A_minus.value()}')
        print(f'pin_B_minus value is {pin_B_minus.value()}')
        
        utime.sleep(0.25)
        tim.deinit()  # stop the timer
        utime.sleep(1)
        loop(serial_com)
    except:
        pass
         
if __name__ == '__main__':
    main()

