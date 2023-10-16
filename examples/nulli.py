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

import logging
import argparse
import sys
import time

import random
import numpy as np

from Adafruit_BNO055 import BNO055
#from scipy.constants import *
from helpers import D, B_z_s, zi

# Initialize variables for storing current velocity and position
current_velocity = [0, 0, 0]  # Initialize with zero velocity
current_position = [0, 0, 0]  # Initialize at the origin

# Function to calculate displacement from acceleration data
def calculate_displacement_from_acceleration(acceleration, time_interval):
    # Using the equations of motion to calculate displacement
    displacement = [0, 0, 0]
    for i in range(3):
        displacement[i] = current_velocity[i] * time_interval + 0.5 * acceleration[i] * (time_interval ** 2)
    return displacement

# Function to update velocity based on acceleration
def update_velocity(acceleration, time_interval):
    for i in range(3):
        current_velocity[i] += acceleration[i] * time_interval

def collect_array(axis, number_of_datapoints, length_of_one_side):

    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

    mag_x,mag_y,mag_z = bno.read_magnetometer()
    acc_x,acc_y,acc_z = bno.read_accelerometer()

    # Calculate displacement from acceleration    
    print('acc_x={0} acc_y={1} acc_z={2}'.format(round(acc_x), round(acc_y), round(acc_z)))
    displacement_from_acceleration = calculate_displacement_from_acceleration([round(acc_x), round(acc_y), round(acc_z)], 0.1)

    # Update current position
    
    for i in range(3):
        current_position[i] += displacement_from_acceleration[i]

    # Print the current position
    print("Current Position (x, y, z):", current_position)
    telemetry = [
        {'index': 0, 'pos_x': current_position[0], 'pos_y': current_position[1], 'pos_z': current_position[2], 'mag_x': mag_x, 'mag_y': mag_y, 'mag_z': mag_z}
        ]
    print(telemetry)

    # Simulate ongoing data flow
    collecting_along_axis = True
    max_increment_step = length_of_one_side/number_of_datapoints
    increment_step_size = 0
    data_point_results = []

    current_index = len(telemetry) #more devine: start collecting in look but lets see

    while collecting_along_axis:
        # Magnetometer data (in micro-Teslas):
        #random_variation = random.uniform(-1, 1)

        latest_data_point = telemetry[0]
        
        acc_x,acc_y,acc_z = bno.read_accelerometer()
        mag_x,mag_y,mag_z = bno.read_magnetometer()  

        print('acc_x={0} acc_y={1} acc_z={2}'.format(round(acc_x), round(acc_y), round(acc_z)))
        displacement_from_acceleration = calculate_displacement_from_acceleration([round(acc_x), round(acc_y), round(acc_z)], 0.1)

        for i in range(3):
            current_position[i] += displacement_from_acceleration[i]

        print("Current Position (x, y, z):", current_position)

        new_data_point = {
            'index': current_index + 1,
            'pos_x': current_position[0],
            'pos_y': current_position[1],
            'pos_z': current_position[2],
            'mag_x': mag_x,
            'mag_y': mag_y,
            'mag_z': mag_z,
        }
        print(telemetry)
        telemetry.sort(key=lambda data: data["pos_"+ axis]) #TODO: check this function
        #print("Added new data point pos z:", new_data_point["pos_z"])
        #print("Added new data point mag z:", new_data_point["mag_z"])

        #print("latest data point:", latest_data_point)
        #print("last pos_z", latest_data_point["pos_z"])
        #print("new pos_z", new_data_point["pos_z"])
        increment_step_size = increment_step_size + (new_data_point["pos_"+ axis] - latest_data_point["pos_"+ axis])
        #print("increment step size", increment_step_size)

        if increment_step_size >= max_increment_step: 
            print("Sensor moved in max_increment_step in pos z axis")
            data_point_results.append({"pos_"+ axis: new_data_point["pos_"+ axis], "mag_"+ axis: new_data_point["mag_"+ axis]})
            increment_step_size = 0

        if len(data_point_results) == number_of_datapoints:
            index = int(len(data_point_results)/2)
            return data_point_results
        time.sleep(0.01)  # Delay for 1 seconds
        # Add the new data point to the telemetry list
        mocked_telemetry.append(new_data_point)
        
        # Increment the index
        current_index += 1

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
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=50, help='Number of data points to be collected')
    args = parser.parse_args()


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

    print('Reading BNO055 data, press Ctrl-C to quit...')

    magneto_data_array = collect_array(args.measured_axis, args.number_of_datapoints, args.length_of_one_side)
    current_av = calculate_current(args.measured_axis, magneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)  
    print(current_av, "A")
    voltage, power = calc_voltage_power(current_av, args.resistance)
    print(voltage)

if __name__ == "__main__":
    main()
