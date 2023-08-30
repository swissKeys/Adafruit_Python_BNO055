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
import time

import random
import numpy as np

from Adafruit_BNO055 import BNO055
from scipy.constants import *
from helpers import D, B_z_s, zi

#TODO: calc_volage(current) return voltage, power  

def collect_array(axis, number_of_datapoints, length_of_one_side):
    mocked_telemetry = [
    {'index': 0, 'pos_x': 0.0, 'pos_y': 0.2224, 'pos_z': 0.0, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00},
    {'index': 1, 'pos_x': 0.0, 'pos_y': 0.2221, 'pos_z': 0.3, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00},
    {'index': 2, 'pos_x': 0.0, 'pos_y': 0.4, 'pos_z': 0.7, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00},
    {'index': 3, 'pos_x': 0.0, 'pos_y': 0.6, 'pos_z': 1.2, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00},
    {'index': 4, 'pos_x': 0.0, 'pos_y': 0.8, 'pos_z': 1.7, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00},
    {'index': 5, 'pos_x': 0.0, 'pos_y': 1.0, 'pos_z': 2.2, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00}
    ]

    # Initialize index for new data points
    current_index = len(mocked_telemetry)

    # Simulate ongoing data flow
    collecting_along_axis = True
    max_increment_step = length_of_one_side/number_of_datapoints
    increment_step_size = 0
    data_point_results = []

    while collecting_along_axis:
        # Magnetometer data (in micro-Teslas):
        #x,y,z = bno.read_magnetometer()
        random_pos_z = random.uniform(0.01, 0.03)
        random_variation = random.uniform(-1, 1)
        latest_data_point = mocked_telemetry[current_index-1]
        new_data_point = {
            'index': current_index,
            'pos_x': 0.0,
            'pos_y': 4.567,
            'pos_z': latest_data_point["pos_"+ axis] + random_pos_z,
            'mag_x': 0.6,
            'mag_y': 0.7,
            'mag_z': 45.00 + random_variation,
        }

        mocked_telemetry.sort(key=lambda data: data["pos_"+ axis])
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
        time.sleep(1)  # Delay for 1 seconds
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
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=50, help='Number of data points to be collected')
    args = parser.parse_args()

    magneto_data_array = collect_array(args.measured_axis, args.number_of_datapoints, args.length_of_one_side)
    current_av = calculate_current(args.measured_axis, magneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)  
    print(current_av, "A")
    voltage, power = calc_voltage_power(current_av, args.resistance)
    print(voltage)

if __name__ == "__main__":
    main()
