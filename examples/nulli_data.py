# Magneticfield reading and nullification.
#
# Copyright (c) 2023 Bennedetta Kalemi and Rebecca Barth

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import numpy as np
from scipy.constants import *
from helpers import D, B_z_s, zi

#TODO: calc_volage(current) return voltage, power 



def collect_array_real_data(number_of_datapoints):
    import logging
    import sys
    import time

    from Adafruit_BNO055 import BNO055

    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

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
    
    index = 0
    B_x = np.zeros(number_of_datapoints)
    B_y = np.zeros(number_of_datapoints)
    B_z = np.zeros(number_of_datapoints)


    while index<number_of_datapoints:                                                                                    #CAMBIARE
        # Read the Euler angles for heading, roll, pitch (all in degrees).
        #heading, roll, pitch = bno.read_euler()
        # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
        sys, gyro, accel, mag = bno.get_calibration_status()
        # Print everything out.
        #print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
        #   heading, roll, pitch, sys, gyro, accel, mag))
        # Other values you can optionally read:
        # Orientation as a quaternion:
        #x,y,z,w = bno.read_quaterion()
        # Sensor temperature in degrees Celsius:
        #temp_c = bno.read_temp()
        # Magnetometer data (in micro-Teslas):
        x,y,z = bno.read_magnetometer()
        B_x[index] = x
        B_y[index] = y
        B_z[index] = z
        print(B_z[index])
        # Gyroscope data (in degrees per second):
        #x,y,z = bno.read_gyroscope()
        # Accelerometer data (in meters per second squared):
        #x,y,z = bno.read_accelerometer()
        # Linear acceleration data (i.e. acceleration from movement, not gravity--
        # returned in meters per second squared):
        #x,y,z = bno.read_linear_acceleration()
        # Gravity acceleration data (i.e. acceleration just from gravity--returned
        # in meters per second squared):
        #x,y,z = bno.read_gravity()
        index +=1
        # Sleep for a second until the next reading.
        time.sleep(1)

    
    return B_z




def calculate_current(magneto_data_array, number_turns, length_of_one_side, distance_coils):

    N = number_turns  #number of turns of wire
    z = np.linspace(-0.05, 0.05, len(magneto_data_array)) #in meters 1U CubeSat
    #z = np.linspace(-0.05*3, 0.05*3, len(magneto_data_array)) #in meters 3U CubeSat
    L = length_of_one_side
    
    z1 = z + distance_coils/2
    z2 = z - distance_coils/2
    current_to_nulli = []
    magnetic_field = []
    
    index = 0
    while index <len(magneto_data_array): 
         magnetic_field.append(magneto_data_array[index])
         current = magneto_data_array[index]*(4 * ((mu_0*N*L*L)/(np.pi)) * (1/(L*L + 4*z1[index]*z1[index])) * (1/(2*L*L + 4*z1[index]*z1[index])**0.5) *1e6  + 4 * ((mu_0*N*L*L)/(np.pi)) * (1/(L*L + 4*z2[index]*z2[index])) * (1/(2*L*L + 4*z2[index]*z2[index])**0.5) *1e6 )**-1
         current_to_nulli.append(current)
         index+=1

    #nullifying
    current_to_nulli_array = np.asarray(current_to_nulli)
    magnetic_field_array = np.asarray(magnetic_field)
    B_null = B_z_s(z1, current_to_nulli_array, N, L) + B_z_s(z2, current_to_nulli_array, N, L)
    
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
    voltage = 0.0
    power = 0.0
    return voltage, power



def main():
    parser = argparse.ArgumentParser(description='Calculate voltage, power, and current')
    parser.add_argument('--resistance', type=float, required=False, default=0.1, help='Resistance of the wire')
    parser.add_argument('--length_of_one_side', type=float, required=False, default=1, help='Length of one side of the coil')
    parser.add_argument('--distance_coils', type=float, required=False, default=0.54, help='Distance between coils')
    parser.add_argument('--number_turns', type=float, required=False, default=20.0, help='Number of turns in the coil')
    parser.add_argument('--measured_axis', type=str, required=False, default='z', help='Axis along which measurements are taken')
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=20, help='Number of data points to be collected')
    args = parser.parse_args()

    magneto_data_array = collect_array_real_data(args.number_of_datapoints)
    current_av = calculate_current(magneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)  
    print(current_av, "A")
    voltage, power = calc_voltage_power(current_av, args.resistance)
    print(voltage)

if __name__ == "__main__":
    main()