
import logging
import argparse
import time
import json
import requests
import os

import random
import numpy as np
from scipy.constants import *
from helpers import D, B_z_s, zi

from dotenv import load_dotenv
import os

# Get the full path to the .env file
dotenv_path = os.path.abspath('.env')

try:
    load_dotenv(dotenv_path)
except Exception as e:
    print(f"Error loading .env file: {e}")

api_key = os.environ.get('API_KEY')


def get_iss_coordinates():
    
    hostname = "https://api.wheretheiss.at/v1/satellites/25544"

    try: 
        response = requests.get(hostname)
        # extract JSON payload of response as Python dictionary
        json_payload = response.json()
        # raise an Exception if we encoutnered any HTTP error codes like 404 
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e: 
    # handle any typo errors in url or endpoint, or just patchy internet connection
        print(e)
    except requests.exceptions.HTTPError as e:  
    # handle HTTP error codes in the response
        print(e, json_payload['error'])
    except requests.exceptions.RequestException as e:  
    # general error handling
        print(e, json_payload['error'])
    else:
        json_payload = response.json()
        position_iss = json.dumps(json_payload, indent=4, sort_keys=True)
    return position_iss

def get_magnetic_field(number_of_datapoints, altitude, longitude, latitude, year):
    headers = {"API-Key" : api_key}

    hostname = "https://geomag.amentum.io/wmm/magnetic_field"

    params = dict(
        altitude = altitude, # [km]
        longitude = longitude, # [deg]
        latitude = latitude, 
        year = year # decimal year, half-way through 2020
    )
    try: 
        response = requests.get(hostname, params=params, headers=headers)
        # extract JSON payload of response as Python dictionary
        json_payload = response.json()
        # raise an Exception if we encoutnered any HTTP error codes like 404 
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e: 
    # handle any typo errors in url or endpoint, or just patchy internet connection
        print(e)
    except requests.exceptions.HTTPError as e:  
    # handle HTTP error codes in the response
        print(e, json_payload['error'])
    except requests.exceptions.RequestException as e:  
    # general error handling
        print(e, json_payload['error'])
    else:
        json_payload = response.json()
        geomagnetic_field = json.dumps(json_payload, indent=4, sort_keys=True)
    return geomagnetic_field
