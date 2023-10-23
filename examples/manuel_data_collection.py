import logging
import argparse
import sys
import time

import random
import numpy as np

from Adafruit_BNO055 import BNO055
#from scipy.constants import *
from helpers import D, B_z_s, zi

def collect_array(measured_axis, number_of_datapoints, length_of_one_side):
    # Implement your data collection logic here
    print("Press Enter to start data collection:")
    # Wait for the user to press Enter to start the loop
    input()
    # Perform the data collection in a loop

    # Create and configure the BNO sensor connection.  Make sure only ONE of the
    # below 'bno = ...' lines is uncommented:
    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)
    # BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
    # and RST connected to pin P9_12:
    #bno = BNO055.BNO055(rst='P9_12')


    # Enable verbose debug logging if -v is passed as a parameter.
    if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
        logging.basicConfig(level=logging.DEBUG)

    # Initialize the BNO055 and stop if something went wrong.
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

    # Print system status and self test result.
    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
    # Print out an error if system status is in error mode.
    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')

    # Print BNO055 software revision and other diagnostic data.
    sw, bl, accel, mag, gyro = bno.get_revision()
    print('Software version:   {0}'.format(sw))
    print('Bootloader version: {0}'.format(bl))
    print('Accelerometer ID:   0x{0:02X}'.format(accel))
    print('Magnetometer ID:    0x{0:02X}'.format(mag))
    print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

    print('Reading BNO055 data, press Ctrl-C to quit...')
    
    for i in range(number_of_datapoints):
        # Insert your data collection code here
        print(f"Collecting data point {i + 1}")

    print("Data collection complete.")

def main():
    parser = argparse.ArgumentParser(description='Calculate voltage, power, and current')
    parser.add_argument('--resistance', type=float, required=False, default=0.1, help='Resistance of the wire')
    parser.add_argument('--length_of_one_side', type=float, required=False, default=1, help='Length of one side of the coil')
    parser.add_argument('--distance_coils', type=float, required=False, default=0.54, help='Distance between coils')
    parser.add_argument('--number_turns', type=float, required=False, default=20.0, help='Number of turns in the coil')
    parser.add_argument('--measured_axis', type=str, required=False, default='z', help='Axis along which measurements are taken')
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=50, help='Number of data points to be collected')
    args = parser.parse_args()

    # Enable verbose debug logging if -v is passed as a parameter.

    magneto_data_array = collect_array(args.measured_axis, args.number_of_datapoints, args.length_of_one_side)

if __name__ == "__main__":
    main()
