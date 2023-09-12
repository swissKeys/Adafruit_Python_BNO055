# Geomagneticfield extracting, simulating and verifying.
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
import time
import json

import numpy as np
from scipy.constants import *
from helpers import D, B_z_s, zi, seph_to_cat
from api import get_iss_coordinates, get_magnetic_field

def collect_data_geomagnetic_array(number_of_datapoints, year): #coordinates
    geomagnetic_data_array = []
    for datapoint in range(0, number_of_datapoints):

        iss_position = get_iss_coordinates()
        
        data = json.loads(iss_position)

        altitude = data['altitude']
        longitude = data['longitude']
        latitude = data['latitude']
        
        magnetic_field = get_magnetic_field(number_of_datapoints, altitude, longitude, latitude, year)

        magnetic_field_data = json.loads(magnetic_field)

        magnetic_field_in_cart = seph_to_cat(magnetic_field_data['total_intensity']['value'], magnetic_field_data['declination']['value'], magnetic_field_data['inclination']['value'])

        geomagnetic_data_array.append(magnetic_field_in_cart)

        print("step:", datapoint)

        time.sleep(5)

    return geomagnetic_data_array

def calculate_current(axis, geomagneto_data_array, number_turns, length_of_one_side, distance_coils):

    N = number_turns  #number of turns of wire
    z = np.linspace(-0.05, 0.05, len(geomagneto_data_array)) #in meters 1U CubeSat
    #z = np.linspace(-0.05*3, 0.05*3, len(magneto_data_array)) #in meters 3U CubeSat
    L = length_of_one_side
    p = 0 
    z1 = z + distance_coils/2
    z2 = z - distance_coils/2
    current_to_simul = []
    geomagnetic_field = []
    #print(z1)
    #print(z2)
    geomagnetic_field_array = []

    for index, datapoint in enumerate(geomagneto_data_array): #is i for one axis bevause in teh code it is 1 
         geomagnetic_field.append(datapoint["mag_"+ axis])
         current = datapoint["mag_"+ axis]*(4 * ((mu_0*N*L*L)/(np.pi)) * (1/(L*L + 4*z1[index]*z1[index])) * (1/(2*L*L + 4*z1[index]*z1[index])**0.5) *1e6  + 4 * ((mu_0*N*L*L)/(np.pi)) * (1/(L*L + 4*z2[index]*z2[index])) * (1/(2*L*L + 4*z2[index]*z2[index])**0.5) *1e6 )**-1
         current_to_simul.append(current)


    #simulating
    current_to_simul_array = np.asarray(current_to_simul)
    geomagnetic_field_array = np.asarray(geomagnetic_field)
    B_simul = B_z_s(z1, current_to_simul_array, N, L) + B_z_s(z2, current_to_simul_array, N, L)
    print(B_simul)
    print(geomagnetic_field_array)
    print(current_to_simul_array, "A")
        
    I_simul_av = np.average(current_to_simul_array)
    current_to_simul_av =[]
    for value in current_to_simul:
        current_to_simul_av.append(I_simul_av)
    current_to_simul_av= np.asarray(current_to_simul_av)
    B_simul_av = B_z_s(z1, current_to_simul_av, N, L) + B_z_s(z2, current_to_simul_av, N, L)
    simul_array_av = geomagnetic_field_array - B_simul_av
    print(simul_array_av)

    return I_simul_av, np.average(B_simul_av)

def calc_voltage_power(current, resistance): 
    #TODO: unit check
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
    parser.add_argument('--altitude', type=int, required=False, default=10, help='altitude')
    parser.add_argument('--longitude', type=int, required=False, default=10, help='longitude')
    parser.add_argument('--latitude', type=int, required=False, default=10, help='latitude')
    parser.add_argument('--year', type=float, required=False, default=2020.5, help='`year`')

    args = parser.parse_args()

    geomagneto_data_array = collect_data_geomagnetic_array(args.number_of_datapoints, args.year) #coordinates
    print("array", geomagneto_data_array)
    B_simul_av = calculate_current(args.measured_axis, geomagneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)[1] 
    current_av = calculate_current(args.measured_axis, geomagneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)[0] 
    print(current_av, "A")
    voltage, power = calc_voltage_power(current_av, args.resistance)
    print(voltage, power)


if __name__ == "__main__":
    main()