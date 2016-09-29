############################################################################################
# 
# OpenXC Trace File Post Request Simulator
#
############################################################################################
import os
import requests
import time
import json
import re

############################################################################################
# PARSE DATA AND STREAM DIRECTLY TO AT&T M2X
# ALTERNATIVE TO USING FLOW FOR THIS PURPOSE; 
############################################################################################
### Function send_test_data() modified from the function with the same name developed by the
### OpenXC team in the web logging example (https://github.com/openxc/web-logging-example) 
def send_test_data(filename, deviceID, deviceAPIKey):

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
                        ####################
                        # fuel_level
                        ####################
                        # if measurement is 'fuel_level' and the value has changed (or is the first observation)
                        if record['name'] == 'fuel_level' and record['value'] < fuel_level and record['value'] != 0.0 and record['value'] != None:
                            # submit PUT request
                            StringS = 'curl --request PUT --header "Content-Type: application/json" --header "X-M2X-KEY: ' + deviceAPIKey + '" --data \'{"value": '+str(record['value'])+'}\' http://api-m2x.att.com/v2/devices/' + deviceID + '/streams/fuel_level/value?pretty=true'
                            os.system(StringS)
                            fuel_level = record['value']
                            #print "Sending %s" % str(fuel_level)

                        ####################
                        # location
                        ####################
                        # if measurement is 'latitude' and the value has changed (or is the first observation)
                        elif record['name'] == 'latitude' and record['value'] != latitude and record['value'] != 0.0 and record['value'] != None:
                            latitude = record['value']
                            Lat = True
                        # if measurement is 'longitude' and the value has changed (or is the first observation)
                        elif record['name'] == 'longitude' and record['value'] != longitude and record['value'] != 0.0 and record['value'] != None:
                            longitude = record['value']
                            Lon = True
                        # if we have our lat / lon coordinate pair, submit PUT request
                        if (Lat and Lon) or ((Lat or Lon) and (Lat > 0.0 and Lat != None) and (Lon > 0.0 and Lon != None)):
                            #print longitude
                            #print latitude
                            StringL = 'curl -i -X PUT http://api-m2x.att.com/v2/devices/' + deviceID + '/location -H "X-M2X-KEY: ' + deviceAPIKey + '" -H "Content-Type: application/json" -d  \'{ "latitude" : ' + str(latitude) + ', "longitude" : ' + str(longitude) + '}\''
                            #print StringL
                            os.system(StringL)
                            Lat = False
                            Lon = False
                    except:
                        continue # keeps it going, but keep an eye out for what shows up on the log
                        

                    if records_len == 25:
                        time.sleep(.5)
                        records_len = 0

        except IOError:
            print("No active trace file found at %s" % filename)

### Send a pre-recorded OpenXC trace to the "device" in M2X corresponding to the vehicle
Filepath = '~./Drive_Traces/1FADP5BU4EL513709/' # folder containing drive traces for a vehicle
deviceID = '' # AT&T M2X device ID
deviceAPIKey = '' # AT&T M2X device API Key
Files = os.listdir(Filepath)
JSONfiles = []
for i in range(0, len(Files)):
    if (re.search(r'.json', Files[i])):
        JSONfiles.append(Files[i])
        send_test_data(Filepath + Files[i], deviceID, deviceAPIKey)