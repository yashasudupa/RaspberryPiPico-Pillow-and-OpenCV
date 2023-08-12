"""This is the UART_uc_to_Host script

This scripts ensures the initialisation of serial port
i) Provides member function to wait for serial input
   and parse the received user input and extract the
   angle value from the string
ii) Exception handling is done to ensure the script does
    not break and still coninues to keep system stable
    and wait for user input

"""

from machine import Pin,UART
import time
import select
import sys

class serial_io:
    
    
    """Helper Method : UART initialisations of serial_io

    Args: None  
    Returns : None
        
    """
    def __init__(self):
        self.uart = UART(1, baudrate=9600)

    
    """Helper Method : Parser is written to parse the input angle and unit_marker

    Args: None  
    Returns : angle or Invalid Input
        
    """
    def wait_for_input(self):
        print('UART_uc_to_Host::waiting_for_input')
        input_str = ""
        
        #Reading the serial data byte by byte and concatenating to form a string
        while True:
            ch = sys.stdin.read(1)
            input_str += ch
            
            if ch == 'g':
                break
            
        #Concatenated serial input data is split into angle_str and unit (degree)
        try:        
            angle_str, unit_marker = input_str.split(' ')
            print('UART_uc_to_Host::wait_for_input - angle_str, unit_marker', angle_str, unit_marker)
            if unit_marker == 'deg':
                angle = int(angle_str)
                return angle
            else:
                print("UART_uc_to_Host::wait_for_input - Invalid unit marker:", unit_marker)
                return "Invalid Input"
        except ValueError:
            print('UART_uc_to_Host::wait_for_input - Invalid data format:', received_data)
            return "Invalid Input"
        
        time.sleep(1)
        return input_str
        
        
    """Helper Method : Sends data to Host system

    Args: data  
    Returns : None
        
    """ 
    def send_to_host(self, data):
        try:            
            print('UART_uc_to_Host::send_to_host : UART info :', self.uart)
            sys.stdout.write(data)
        except:
            pass
