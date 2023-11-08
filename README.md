# Adafruit Python BNO055

This is a Python library for accessing the Bosch BNO055 absolute orientation sensor on a Raspberry Pi or Beaglebone Black.

#### Establishing a Connection to the raspberry

1. Connect your Raspberry Pi to your local machine via an Ethernet (LAN) cable.

2. Open your terminal on your local machine and SSH into your Raspberry Pi:

    ```shell
    ssh pi@raspberrypi.local
    ```

3. Enter the password when prompted 

4. You are now connected to your Raspberry Pi via SSH but might not have internet access yet.

5. To configure network settings, run the following command in your Raspberry Pi terminal:

    ```shell
    sudo raspi-config
    ```

6. Navigate to "Localization Options" (likely under "Localization Settings").

7. Configure your Wi-Fi country settings by entering the appropriate location (e.g., "DE" for Germany) to comply with Wi-Fi channel regulations.

8. Enter your Wi-Fi network name (SSID) and password.

9. Confirm the changes and exit the configuration menu.

10. Check if you have internet access by running a ping command:

    ```shell
    ping www.google.com
    ```

11. Type "Exit" to return to your local machine's terminal.

12. Disconnect the LAN cable and connect your local machine to your Wi-Fi hotspot.

13. SSH into your Raspberry Pi again:

    ```shell
    ssh pi@raspberrypi.local
    ```

14. Enter the password when prompted

15. You should now be able to establish an SSH connection without the LAN cable.

Please note that these instructions provide a basic setup and connection guide. You may need to adapt them to your specific use case and hardware requirements.



## Installation and Usage

## Local Machine (Development)

1. Clone the repository to your local machine:

    ```shell
    git clone https://github.com/swissKeys/Adafruit_Python_BNO055
    cd Adafruit_Python_BNO055
    ```

**Install Dependencies:**

    ```shell
    python3 install setup.py
    ```

## Raspberry Pi (Remote)

To enter your Raspberry Pi and run the code remotely, follow these steps:

1. Establish an SSH connection:

    ```shell
    ssh pi@raspberrypi.local
    ```

2. Enter the password when prompted

3. Navigate to the examples folder within the project directory or clone it if new setup:

    ```shell
    cd git/Adafruit_Python_BNO055/examples
    ```
    **Install Dependencies:**

        ```shell
        python3 install setup.py
        ```

Make sure your Raspberry Pi is set up and configured properly before running the script.


### Nullification with Helmholtz cage

4. Run the Python script for manual data collection:

    ```shell
    python3 manuel_data_collection.py
    ```

    It will output the necessary voltage for nullification and trigger a remeasuring process. 






### Simulation of LEO with Helmholtz cage

4. Run the Python script for  simulation:

    ```shell
    python3 simu.py
    ```
