import logging
import argparse
import datetime
import csv
import time
import json
import threading
import sys
import random
import numpy as np

from Adafruit_BNO055 import BNO055
from scipy.constants import *
#from scipy.constants import *
from helpers import D, B_z_s, zi

def collect_array(measured_axis, number_of_datapoints, length_of_one_side, checking_data):

    # Open the CSV file in write mode (use 'a' for append mode if the file already exists)

    def average_num_in_time(frequency):

        total_x, total_y, total_z = 0, 0, 0

        array_x = []
        array_y = []
        array_z = []

        for _ in range(frequency):
            
            mag_x, mag_y, mag_z = bno.read_magnetometer()
            total_x += mag_x
            array_x.append(mag_x)
            total_y += mag_y
            array_y.append(mag_y)
            total_z += mag_z
            array_z.append(mag_z)
            time.sleep(1.0 / frequency)

        avg_x = total_x / frequency
        avg_y = total_y / frequency
        avg_z = total_z / frequency

        
        return avg_x, avg_y, avg_z, array_x, array_y, array_z
    
    # Implement your data collection logic here
    print("Press Enter to start data collection:")
    # Wait for the user to press Enter to start the loop
    input()
    # Perform the data collection in a loop

    # Create and configure the BNO sensor connection.  Make sure only ONE of the
    # below 'bno = ...' lines is uncommented:
    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

    CALIBRATION_FILE = 'webgl_demo/calibration.json'


    bno_changed = threading.Condition()


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

    system, gyro, accel, mag = bno.get_calibration_status()

    print(system)
    print(gyro)
    print(accel)
    print(mag)


    with open(CALIBRATION_FILE, 'r') as cal_file:
        data = json.load(cal_file)
    # Grab the lock on BNO sensor access to serial access to the sensor.
    with bno_changed:
        bno.set_calibration(data)

    print('Loading calib')

    system, gyro, accel, mag = bno.get_calibration_status()

    print(system)
    print(gyro)
    print(accel)
    print(mag)

    magneto_data_array = []
    detailed_data = []
    centimeter = 65
    for i in range(number_of_datapoints):
        print(f"Press Enter to collect Point number { i+1 } on {centimeter} cm:")
        # Insert your data collection code here
        input()

        mag_x,mag_y,mag_z, array_x, array_y, array_z = average_num_in_time(30)
        #mag_x,mag_y,mag_z = bno.read_magnetometer()

        print('mag_x={0} mag_y={1} mag_z={2}'.format(round(mag_x, 4), round(mag_y, 4), round(mag_z, 4)))
        
        new_data_point = {
            'mag_x': round(mag_x, 4),
            'mag_y': round(mag_y, 4),
            'mag_z': round(mag_z, 4),
        }

        new_exyensive_data_point = {
            'mag_x': array_x,
            'mag_y': array_y,
            'mag_z': array_z,
        }

        magneto_data_array.append(new_data_point)
        detailed_data.append(new_exyensive_data_point)

        centimeter -= 1
        print(f"Collecting data point {i+1}")
    
    # Generate a unique filename based on the current date and time
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if checking_data == False:
        json_file = f"collection_start_65_end_{centimeter}_mitte_{measured_axis}_{current_datetime}.json"
    else:
        json_file = f"checking_start_65_end_{centimeter}_mitte_{measured_axis}_{current_datetime}.json"
        

    data_dict = {
    "magneto_data": magneto_data_array,
    "detailed_data": detailed_data
    }

    # Save the data dictionary as a JSON object
    with open(json_file, 'w') as f:
        json.dump(data_dict, f, indent=4) 

    print(magneto_data_array)

    print("Data collection complete.")
    return magneto_data_array


def calculate_current(axis, magneto_data_array, number_turns, length_of_one_side, distance_coils):
    print("axis measured:", axis)
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
        
    print("Array of current to nulli:", current_to_nulli_array)
    av = np.average(current_to_nulli_array)
    current_to_nulli_av =[]

    for value in current_to_nulli:
        current_to_nulli_av.append(av)

    current_to_nulli_av= np.asarray(current_to_nulli_av)

    B_null_av = B_z_s(z1, current_to_nulli_av, N, L) + B_z_s(z2, current_to_nulli_av, N, L)
    null_array_av = magnetic_field_array - B_null_av

    print("Nullified array values", null_array_av)
    print("Average current:", av)

    # Generate a unique filename based on the current date and time
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    averaged_values_cvs = f"calculate_values_for_nulli_{current_datetime}.csv"

    # Write the values to a CSV file
    with open(averaged_values_cvs, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["axis","Array of current to nulli", "Nullified array values", "Average current (Ampere)", "number_turns", "length_of_one_side", "distance_coils"])
        writer.writerow([axis, current_to_nulli_array, null_array_av.tolist(), av, number_turns, length_of_one_side, distance_coils])

    print(f"Values saved to {averaged_values_cvs}")

    return av

def calc_voltage_power(current, resistance): 
    voltage = current*resistance
    power = voltage*current

    return voltage, power


def main():
    parser = argparse.ArgumentParser(description='Calculate voltage, power, and current')
    parser.add_argument('--resistance', type=float, required=False, default=31.7, help='Resistance of the wire')
    parser.add_argument('--length_of_one_side', type=float, required=False, default=0.84, help='Length of one side of the coil in m')
    parser.add_argument('--distance_coils', type=float, required=False, default=0.456, help='Distance between coils in m')
    parser.add_argument('--number_turns', type=float, required=False, default=20.0, help='Number of turns in the coil')
    parser.add_argument('--measured_axis', type=str, required=False, default='z', help='Axis along which measurements are taken')
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=5, help='Number of data points to be collected')
    args = parser.parse_args()

    # Enable verbose debug logging if -v is passed as a parameter.

    magneto_data_array = collect_array(args.measured_axis, args.number_of_datapoints, args.length_of_one_side, False)
    print("collected array rounded to integer values:", magneto_data_array)
    current_av = calculate_current(args.measured_axis, magneto_data_array, args.number_turns, args.length_of_one_side, args.distance_coils)  
    print(current_av, "A")
    voltage, power = calc_voltage_power(current_av, args.resistance)
    print(voltage, 'volts')
    print("Press enter to check nullification:")
    input()
    measured_data_array = collect_array(args.measured_axis, args.number_of_datapoints, args.length_of_one_side, True)
    print("Measured Array after nulli:", measured_data_array)

if __name__ == "__main__":
    main()
