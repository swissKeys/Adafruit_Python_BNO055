# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#TODO: Imports

import logging
import argparse
import time

import random
import time

#TODO: reiceive mockeed telemetry from sensor (pos x,y,z) and magneticfield values(x,y,z). the sensor is facked moved along the z axis.
#TODO: collect_array(axis) use ongoing telemertry from sensor for z-axis. Save the value for magnetfield (z) and pos (z) every 5cm the sensor moves into positove z-direction Until we have 10 values. return list.
#TODO: func(array) return current
#TODO: calc_volage(current) return voltage, power  

def collect_array(axis, max_number):
    mocked_telemetry = [
    {'index': 0, 'pos_x': 0.0, 'pos_y': 0.2224, 'pos_z': 0.0, 'mag_x': 0.1, 'mag_y': 0.2, 'mag_z': 0.5},
    {'index': 1, 'pos_x': 0.0, 'pos_y': 0.2221, 'pos_z': 0.3, 'mag_x': 0.2, 'mag_y': 0.3, 'mag_z': 0.6},
    {'index': 2, 'pos_x': 0.0, 'pos_y': 0.4, 'pos_z': 0.7, 'mag_x': 0.3, 'mag_y': 0.4, 'mag_z': 0.7},
    {'index': 3, 'pos_x': 0.0, 'pos_y': 0.6, 'pos_z': 1.2, 'mag_x': 0.4, 'mag_y': 0.5, 'mag_z': 0.8},
    {'index': 4, 'pos_x': 0.0, 'pos_y': 0.8, 'pos_z': 1.7, 'mag_x': 0.5, 'mag_y': 0.6, 'mag_z': 0.9},
    {'index': 5, 'pos_x': 0.0, 'pos_y': 1.0, 'pos_z': 2.2, 'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 1.0}
    ]

    # Initialize index for new data points
    current_index = len(mocked_telemetry)

    # Simulate ongoing data flow
    collecting_along_axis = True
    number_of_datapoints = 0
    increment_step_size = 0
    data_point_results = []



    while collecting_along_axis:
        # Magnetometer data (in micro-Teslas):
        #x,y,z = bno.read_magnetometer()
        random_pos_z = random.uniform(1, 2)
        random_variation = random.uniform(-0.02, 0.02)
        latest_data_point = mocked_telemetry[current_index-1]
        new_data_point = {
            'index': current_index,
            'pos_x': 0.0,
            'pos_y': 4.567,
            'pos_z': latest_data_point["pos_"+ axis] + random_pos_z,
            'mag_x': 0.6 + random_variation,
            'mag_y': 0.7 + random_variation,
            'mag_z': 1.0 + random_variation,
        }

        mocked_telemetry.sort(key=lambda data: data["pos_"+ axis])
        #print("Added new data point pos z:", new_data_point["pos_z"])
        #print("Added new data point mag z:", new_data_point["mag_z"])

        #print("latest data point:", latest_data_point)
        #print("last pos_z", latest_data_point["pos_z"])
        #print("new pos_z", new_data_point["pos_z"])
        increment_step_size = increment_step_size + (new_data_point["pos_"+ axis] - latest_data_point["pos_"+ axis])
        #print("increment step size", increment_step_size)
        if increment_step_size >= max_number: 
            #TODO: add to array and increase number_of_datapoints
            print("Sensor moved in 5 in pos z axis")

            number_of_datapoints += 1
            data_point_results.append({"pos_"+ axis: new_data_point["pos_"+ axis], "mag_"+ axis: new_data_point["mag_"+ axis]})
        #print("Added new data point:", new_data_point)
        if len(data_point_results) == 5:
            return data_point_results
        time.sleep(1)  # Delay for 1 seconds
        # Add the new data point to the telemetry list
        mocked_telemetry.append(new_data_point)
        
        # Increment the index
        current_index += 1

def main():
    parser = argparse.ArgumentParser(description='Calculate voltage, power, and current')
    parser.add_argument('--resistance', type=float, required=False, default=0.1, help='Resistance of the wire')
    parser.add_argument('--length_of_one_side', type=float, required=False, default=0.1, help='Length of one side of the coil')
    parser.add_argument('--distance_coils', type=float, required=False, default=0.2, help='Distance between coils')
    parser.add_argument('--number_turns', type=int, required=False, default=100, help='Number of turns in the coil')
    parser.add_argument('--measured_axis', type=str, required=False, default='z', help='Axis along which measurements are taken')
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=5, help='Number of data points to be collected')
    args = parser.parse_args()

    magneto_data_array = collect_array(args.measured_axis, args.number_of_datapoints)
    print(magneto_data_array)

    """ 
        telemetry_array, pos = collect_array(args.measured_axis)
        current = calc_current(telemetry_array, pos)
        voltage, power = calc_voltage_power(current, args.resistance)
        
        print(f"Voltage: {voltage:.2f} V")
        print(f"Power: {power:.2f} W")
        print(f"Current: {current:.2f} A") """

if __name__ == "__main__":
    main()
