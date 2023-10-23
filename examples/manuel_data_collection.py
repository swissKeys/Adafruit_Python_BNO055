import logging
import argparse
import sys
import time

import random
import numpy as np

from Adafruit_BNO055 import BNO055
from scipy.constants import *
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
    magneto_data_array = []
    for i in range(number_of_datapoints):
        print(f"Press Enter to collect Point number { i }:")
        # Insert your data collection code here
        input()
        mag_x,mag_y,mag_z = bno.read_magnetometer()
        print('mag_x={0} mag_y={1} mag_z={2}'.format(round(mag_x), round(mag_y), round(mag_z)))
        
        new_data_point = {
            'mag_x': mag_x,
            'mag_y': mag_y,
            'mag_z': mag_z,
        }

        magneto_data_array.append(new_data_point)
        print(f"Collecting data point {i + 1}")

    print("Data collection complete.")
    return magneto_data_array


def calculate_current(axis, magneto_data_array, number_turns, length_of_one_side, distance_coils):

    N = number_turns  #number of turns of wire
    z = np.linspace(-0.05, 0.05, len(magneto_data_array)) #in meters 1U CubeSat
    #z = np.linspace(-0.05*3, 0.05*3, len(magneto_data_array)) #in meters 3U CubeSat
    L = length_of_one_side
    p = 0 
    z1 = z + distance_coils/2
    z2 = z - distance_coils/2
    current_to_nulli = []
    magnetic_field = []
    #print(z1)
    #print(z2)
    for index, datapoint in enumerate(magneto_data_array): #is i for one axis bevause in teh code it is 1 
         magnetic_field.append(datapoint["mag_"+ axis])
         current = datapoint["mag_"+ axis]*(4 * ((mu_0*N*L*L)/(np.pi)) * (1/(L*L + 4*z1[index]*z1[index])) * (1/(2*L*L + 4*z1[index]*z1[index])**0.5) *1e6  + 4 * ((mu_0*N*L*L)/(np.pi)) * (1/(L*L + 4*z2[index]*z2[index])) * (1/(2*L*L + 4*z2[index]*z2[index])**0.5) *1e6 )**-1
         current_to_nulli.append(current)

    #nullifying
    current_to_nulli_array = np.asarray(current_to_nulli)
    magnetic_field_array = np.asarray(magnetic_field)
    B_null = B_z_s(z1, current_to_nulli_array, N, L) + B_z_s(z2, current_to_nulli_array, N, L)
    #print(B_null)
    #print(magnetic_field_array)
    null_array = magnetic_field_array - B_null
    for value in null_array:
        if int(value) != 0: 
            print("failure")
            return
        
    av = np.average(current_to_nulli_array)
    current_to_nulli_av =[]
    for value in current_to_nulli:
        current_to_nulli_av.append(av)
    current_to_nulli_av= np.asarray(current_to_nulli_av)
    B_null_av = B_z_s(z1, current_to_nulli_av, N, L) + B_z_s(z2, current_to_nulli_av, N, L)
    null_array_av = magnetic_field_array - B_null_av
    print(null_array_av)
    return av

def calc_voltage_power(current, resistance): 
    voltage = current*resistance
    power = voltage*current

    return voltage, power


def main():
    parser = argparse.ArgumentParser(description='Calculate voltage, power, and current')
    parser.add_argument('--resistance', type=float, required=False, default=0.1, help='Resistance of the wire')
    parser.add_argument('--length_of_one_side', type=float, required=False, default=1, help='Length of one side of the coil')
    parser.add_argument('--distance_coils', type=float, required=False, default=0.54, help='Distance between coils')
    parser.add_argument('--number_turns', type=float, required=False, default=20.0, help='Number of turns in the coil')
    parser.add_argument('--measured_axis', type=str, required=False, default='z', help='Axis along which measurements are taken')
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=5, help='Number of data points to be collected')
    args = parser.parse_args()

    # Enable verbose debug logging if -v is passed as a parameter.

    magneto_data_array = collect_array(args.measured_axis, args.number_of_datapoints, args.length_of_one_side)
    current_av = calculate_current(args.measured_axis, magneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)  
    print(current_av, "A")
    voltage, power = calc_voltage_power(current_av, args.resistance)
    print(voltage)

if __name__ == "__main__":
    main()
