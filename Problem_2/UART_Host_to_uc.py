"""This is the main script of UART_Host_to_uc.py

Program is written to enable communication between Host and Raspberry Pi Pico using USB/UART:
i) This python script handles all the invalid inputs and processes only valid
+/- rotation angle inputs. 
ii) This script automatically detects the port to which the Raspberry Pi Pico is connected
no matter if the script is running in the Linux system or Windows system.
iii) Displays the format at which the input angle needs to be provided and ignores if
the invalid inputs are provided. 
iv) This script does not break and not breaks Raspberry Pi Pico even if any random invalid input provided.
v) Consists of good exception handling mechanism.

"""

import os
import sys
import time
import serial as pyserial
import re


"""Helper Method to check if special characters exist in the input

    Args: data : input string 
    Returns : True : Special characters does not exist, False : Special characters exist 
        
""" 
def check_special_characters(data):
    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

    if(regex.search(data) == None):
        return True
         
    else:
        return False


"""Helper Method to detect the serial port to which Raspberry Pi is connected and automatically detects
whether it is Linux system or Windows System.

    Args:  
    Returns : Port number or None 
        
"""
def detect_serial_port():
    system_platform = sys.platform
    serial_ports = []

     # Detect serial ports based on the operating system
    if 'linux' in system_platform:
        serial_ports = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2" , "/dev/ttyACM3", "/dev/ttyACM4", "/dev/ttyACM5", "/dev/ttyUSB0", "/dev/ttyUSB1"]
    elif 'win' in system_platform:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        serial_ports = [port.device for port in ports]

     # Check each serial port for connectivity
    for port in serial_ports:
        try:
            with pyserial.Serial(port, 9600, timeout=1):
                return port
        except (OSError, pyserial.SerialException):
            pass

    return None


"""main function to detect the serial port to which Raspberry Pi is connected and send the user input request to Raspberry Pi
Pico to drive the stepper motor accurately.
"""

def main():
    # Detect the serial port
    port = detect_serial_port()
    print("Detected port :", port)    


    if port:
        # Establish a serial connection
        with pyserial.Serial(port, 9600) as ser:
            try:
                while True:
                    # Get user input for the angle
                    angle = input('Enter the value in the format : angle deg. e.g: 45 deg = +45, -45 deg = -45 \n')
                    pos = angle.find(' deg')
                    float_pos = angle.find('.')
                    print(pos)
                    if pos == -1:
                        print ("Invalid input, Re-enter the value in the format : angle deg.")
                        continue
                    if float_pos >= 0:
                        print ("Invalid input. Float values cannot be provided. Re-enter the value in the format angle deg.")
                        continue
                    if check_special_characters(angle) == False:
                        print ("Invalid input, Re-enter the value in the format : angle deg.")
                        continue
                    print("Sending angle:", angle)
                     # Send the input value over UART
                    ser.write(angle.encode())  # send the input value over UART
                    print("Value is sent to the device")
                    time.sleep(0.5)

            except pyserial.SerialException as e:
                print('An Exception Occurred')
                print('Exception Details ->', e)
    else:
        print("No serial port detected.")

if __name__ == "__main__":
    main()
