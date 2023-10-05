# Simple Adafruit BNO055 sensor reading example.  Will print the orientation
# and calibration data every second.
#
# Copyright (c) 2015 Adafruit Industries
# Author: Tony DiCola
#
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
import sys
import time

from Adafruit_BNO055 import BNO055




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

current_velocity = [0, 0, 0]  # Initialize with zero velocity
current_position = [0, 0, 0]  # Initialize at the origin

def calculate_displacement_from_acceleration(acceleration, time_interval):
    # Using the equations of motion to calculate displacement
    displacement = [0, 0, 0]
    for i in range(3):
        current_velocity[i] = acceleration[i] * time_interval
        displacement[i] = 0.5 * acceleration[i] * pow(time_interval, 2) + current_velocity[i] * time_interval
    return displacement

while True:
    # Read the Euler angles for heading, roll, pitch (all in degrees).
    #heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    #sys, gyro, accel, mag = bno.get_calibration_status()
    # Print everything out.
    #print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(heading, roll, pitch, sys, gyro, accel, mag))
    # Other values you can optionally read:
    # Orientation as a quaternion:
    #x,y,z,w = bno.read_quaterion()
    # Sensor temperature in degrees Celsius:
    #temp_c = bno.read_temp()
    # Magnetometer data (in micro-Teslas):
    #x,y,z = bno.read_magnetometer()
    #print('mag_x={0} mag_y={1} mag_z={2}'.format(x, y, z))
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
    #print('grav_x={0} grav_y={1} grav_z={2}'.format(x, y, z))
    # Sleep for a second until the next reading.
    mag_x,mag_y,mag_z = bno.read_magnetometer()
    acc_x,acc_y,acc_z = bno.read_linear_acceleration()
    print('acc_x={0} acc_y={1} acc_z={2}'.format(acc_x,acc_y,acc_z))
    displacement_from_acceleration = calculate_displacement_from_acceleration([int(acc_x), int(acc_y), int(acc_z)], 1.00)

    for i in range(3):
        current_position[i] += displacement_from_acceleration[i]

    # Print the current position
    print("Current Position (x, y, z):", current_position)

    telemetry = [
        {'index': 0, 'pos_x': current_position[0], 'pos_y': current_position[1], 'pos_z': current_position[2], 'mag_x': mag_x, 'mag_y': mag_y, 'mag_z': mag_z}
        ] 
    #print(telemetry)
    time.sleep(1)
