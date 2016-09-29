############################################################################################
# SEND TEST LINES FROM PRE-RECORDED OPENXC TRACES TO AT&T FLOW, 
# WHERE THEY WILL BE PARSED AND SENT TO M2X
############################################################################################
### Use OpenXC library function to upload trace file one line at a time
### Useful if you want to send a small amount of data as a test
###
### 1) 
### Run on CL "python M2X_post_vehicle_data.py" and press CTRL + C to submit a new line

import os
import requests
import time
import json
import re
import openxc
from openxc import sinks


def send_test_data_To_Flow(filename, url):

    def wait_for_next_record(starting_time, first_timestamp,timestamp):
        target_time = starting_time + (timestamp - first_timestamp)
        sleep_duration = target_time - time.time()
        if sleep_duration > 0:
            time.sleep(sleep_duration + 1)

    records_len = 0

    fuel_level = 100.0
    fuel_val = None

    latitude = 0.0
    longitude = 0.0
    Lat = False
    Lon = False
    

    while True:
        starting_time = time.time()
        first_timestamp = None
        try:
            with open(filename, 'r') as trace_file:
                for line in trace_file:
                    record = json.loads(line)
                    records_len += 1

                    if first_timestamp is None:
                        first_timestamp = record['timestamp']
                    wait_for_next_record(starting_time, first_timestamp,
                            record['timestamp'])

                    try:
                        openxc.sinks.uploader.UploaderSink.Uploader._upload(url, line)
                    except:
                        continue # keeps it going, but keep an eye out for what shows up on the log

        except IOError:
            print("No active trace file found at %s" % filename)

File = '~./2016-03-20-18-00-39.json' # enter the filepath to your JSON trace file
url2 = "" # YOUR FLOW ENDPOINT
send_test_data_To_Flow(File, url2)