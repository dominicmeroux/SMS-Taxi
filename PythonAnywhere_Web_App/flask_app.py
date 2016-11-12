# Install packages: https://help.pythonanywhere.com/pages/InstallingNewModules
# Web: https://www.pythonanywhere.com/user/dmeroux/webapps/#tab_id_dmeroux_pythonanywhere_com
# Web Site: http://dmeroux.pythonanywhere.com
# Twilio Console: https://www.twilio.com/console/sms/logs?toNumber=+19162490575
# Google Maps API: https://github.com/googlemaps/google-maps-services-python
# Google Maps API Manager: https://console.developers.google.com/apis/dashboard?project=firstproject-960&duration=PT1H

from flask import Flask, Response, request, render_template
from twilio import twiml
import googlemaps
from m2x.client import M2XClient
import sqlite3
import re

gDistance = googlemaps.Client(key='')
gPlaces = googlemaps.Client(key='')
gDirections = googlemaps.Client(key='')


app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def home():
    return render_template("HomePage.html")

@app.route("/Admin")
def Admin():
    return render_template("Admin.html")

@app.route("/twilio", methods=["POST"])
def inbound_sms():
    response = twiml.Response()
    # we get the SMS message from the request. we could also get the
    # "To" and the "From" phone number as well
    inbound_message = request.form.get("Body")

    ###########################################################
    # If SMS has invalid syntax
    ###########################################################
    # If message is too long to be an address, Twilio already has this limit (160 characters)
    # If message contains invalid characters
    if (re.search(r'\+|\?|\*|\^|\$|\(|\)|\[|\]|\{|\}\||\\', inbound_message)):
        response.message("Invalid characters in ride request")

    # If message does not include semicolons
    elif not re.search(r';', inbound_message):
        response.message("Please format your ride request with semicolons like this: 33.586773,-7.618161; 33.586777, -7.618111; 1")

    ###########################################################
    # If SMS is an M2X low fuel alert trigger
    ###########################################################
    elif (re.search(r'Low Fuel trigger fired by device', inbound_message)):
        # Google maps API to add fuel station to route
        # (916) 249-0575 Twilio phone number
        # (415)-877-4758 IFTT phone number
        # Request Bin URL for Logger1 trigger: http://requestb.in/12e6hv31
        # Home URL: http://requestb.in/12e6hv31?inspect
        # https://ifttt.com/myrecipes/personal
        ###### 1) set up with Google Maps API; 2) add multiple devices and triggers for each
        Message = re.sub(r'-.*', '', inbound_message)
        Device = re.sub(r'Low Fuel trigger fired by device ', '', Message)

        try:
            conn = sqlite3.connect('passenger.db')
            c = conn.cursor()
            c.execute("SELECT vehicleID FROM vehicle WHERE data_loggerID = " + Device)
            Vehicle = c.fetchall()
        except:
            response.message("issue with SQLite db connection.")
            return Response(str(response), mimetype="application/xml"), 200


        try:
            # Obtain taxi's last reported location from M2X
            KEY = ''
            client = M2XClient(KEY)
            client.devices()
            json = client.last_response.json
            DeviceInfo = [d for d in json['devices'] if d['name'] == Device]
            Location = str(DeviceInfo[0]['location']['latitude']) + "," + str(DeviceInfo[0]['location']['latitude'])


            # Obtain gas stations near the taxi's current location
            GasStations = gPlaces.places('gas_station', location=Location)

            # Add first fuel station listing to destination list
            c.execute("INSERT INTO TABLE passenger VALUES (9999, 1, '33.575868, -7.614046'," + GasStations['results'][0]['formatted_address'] + ", 0," + Vehicle + ", 0)")
            conn.commit()

        except:
            response.message("Trigger recieved - exception found: check M2X connection, Google Maps API status, and SQLite database passenger")


    ###########################################################
    # If SMS is a message from the driver on passenger status
    ###########################################################
    # The driver must update the vehicle state with either of the following two text messages
    # passenger 1; picked up
    # passenger 1; dropped off
    elif (re.search(r'passenger', inbound_message)):
        M = inbound_message.split(';')
        Passenger = re.sub(r'passenger ', '', M[0])
        Action = re.sub(r' ', '', M[1])

        conn = sqlite3.connect('passenger.db')
        c = conn.cursor()

        if (re.search(r'pick', M[1])):
            try:
                c.execute("UPDATE passenger SET picked_up_status = 1 WHERE passengerID = " + str(Passenger))
                conn.commit()

                response.message("Thank you. We have recorded that passenger " + str(Passenger) + " has been picked up.")

                # Future extension could link google maps directions for the driver, e.g.
                # https://www.google.com/maps/dir/760+W+Genesee+St+Syracuse+NY+13204/314+Avery+Ave+Syracuse+NY+13204/9090+Destiny+USA+Dr+Syracuse+NY+13204
                # TUTORIAL: http://gearside.com/easily-link-to-locations-and-directions-using-the-new-google-maps/
                # COULD DO THIS FOR GAS: https://www.google.com/maps/search/food/43.12345,-76.12345,14z
            except:
                response.message("Please re-type message - passenger is" + str(Passenger))

        elif (re.search(r'drop', M[1])):
            try:
                c.execute("DELETE FROM passenger WHERE passengerID = "+str(Passenger))
                conn.commit()
                response.message("Thank you. We have recorded that passenger " + str(Passenger) + " has been dropped off.")
            except:
                response.message("Please re-type message")
        else:
            response.message("Please re-type message")

    ###########################################################
    # If SMS is a ride request
    ###########################################################
    # Extract Location, Destination, and Seating Requested and perform action
    else:
        try:
            M = inbound_message.split(';')
            Location = M[0]
            Destination = M[1]
            Seating_Requested = int(M[2])
            if (re.search(r'F|f', M[3])):
                Gender = 0
            elif (re.search(r'M|m', M[3])):
                Gender = 1
            else:
                response.message("Please re-send gender value as M or F. Gender found was" + str(M[3]))

            ###########################################################
            ########################################################### Stage 1: Determine potential matches
            ###########################################################
            # Obtain taxi's last reported location from M2X
            conn = sqlite3.connect('passenger.db')
            c = conn.cursor()
            try:
                KEY = ''
                client = M2XClient(KEY)
                devices = client.devices()
                json = client.last_response.json
                Taxis = {}
                for i in json['devices']:
                    if (i['location']):
                        Taxis[i['name']] = str(i['location']['latitude']) + "," + str(i['location']['longitude'])
            except:
                response.message("Issue with M2X connection, we will fix this soon! Show this message to your driver on your next ride and get a free ride!")
                return Response(str(response), mimetype="application/xml"), 200

            # Generate distance matrix between existing vehicles and latest ride request
            Locations = [value for value in Taxis.values()]
            DevIDs = [key for key in Taxis.keys()]
            Distance = gDistance.distance_matrix(Locations, Location)

            # Declare vehicle assignment index "Occurances" at zero
            ColCounter = 0
            RowCounter = 0

            # initialize duration and distance arrays
            Pickup_Duration = [0 for i in range(0, len(Locations))]
            Pickup_Distance = [0 for j in range(0, len(Locations))]

            # initialize list of potential vehicles for new request
            J = []

            # For each vehicle
            for i in range(0, len(Taxis)-1):

                # Extract duration and distance from distance matrix
                if ('duration' in Distance['rows'][i]['elements'][0]):
                    Pickup_Duration[i] = Distance['rows'][i]['elements'][0]['duration']['value']
                    Pickup_Distance[i] = Distance['rows'][i]['elements'][0]['distance']['value']
                    RowCounter += 1
                ColCounter += 1
                RowCounter = 0
                # 38.544909, -121.742755, 38.547090, -121.751081
                try:
                    c.execute("SELECT SUM(p.seatingDemand) FROM passenger as p, vehicle as v WHERE p.vehicleID = v.vehicleID AND v.data_loggerID = '"+DevIDs[i]+"'")
                    SeatsOutput = c.fetchall()
                    Seating = 0
                    if (SeatsOutput[0][0] != None):
                        Seating = SeatsOutput[0][0]
                    c.execute("SELECT passengerCapacity FROM vehicle WHERE data_loggerID = '"+DevIDs[i]+"'")
                    PassCapacity = c.fetchall()
                except:
                    response.message("db vehicle seats query not working - please contact our support team")
                if (((float(Pickup_Duration[i]) / 60) < 15) and (Seating + Seating_Requested < PassCapacity[0][0])):
                    # Append the index for the vehicle in Current_Status
                    J.append(i)

            # If no vehicles met the requirement for proximity to pickup location
            if len(J) == 0:
                response.message("No available vehicles are in your area at the moment")
            else:
                ###########################################################
                ########################################################### Stage 2: Apply Insertion Heuristic to find optimal match
                ###########################################################
                def OpCost(Distance, fuel_economy, fuel_price):
                    # For now only includes fuel cost,
                    # Fuel Cost = (L / 100 km) * (0.01 * Distance km) * fuel_price per L
                    return fuel_economy * (0.01 * Distance) * fuel_price

                def TimeCost(Duration):
                    # refer to labor cost etc. ?????????
                    # for now, using arbitrary placeholder value of 0.12 per duration unit worth of cost
                    return Duration * 0.12

                def GenderCost(Gender, Seating_Requested, Current_Gender_Mix):
                    if Gender==0 and Current_Gender_Mix > 0:
                        return Seating_Requested * 10 ##### ??????? MODIFY THIS FACTOR LATER
                    else:
                        return 0

                # Initialize lists and variables to be used in insertion heuristic
                Current_Distance = [0 for i in range(0, len(J))]
                Current_Duration = [0 for i in range(0, len(J))]
                New_Distance = [0 for i in range(0, len(J))]
                New_Duration = [0 for i in range(0, len(J))]
                Incremental_Distance = 9999
                Incremental_Duration = 9999
                fuel_efficiency = 9999
                Trip_Price = 0
                Incremental_Vehicle = None
                Profit_Margin = 1.25 # 25% profit
                Gender_Cost = 0
                fuel_price = 3.65
                FinalDurationVal = 0
                Counter = 0

                # For all potential matches - taxis within a 15 minute pickup window with adequate seating capacity
                for i in J:
                    ############################
                    # Calculate Initial Cost
                    ############################
                    # If taxi has zero passengers, default current cost value of 0 is accepted
                    # Waypoints list
                    Stops = []

                    # If all current passengers are in the car, this stays true
                    CanOptimizeWaypoints = True

                    try:
                        c.execute("SELECT p.passengerID, p.picked_up_status, p.pickup_time, p.origin, p.destination, p.gender, p.vehicleID, p.seatingDemand FROM passenger as p, vehicle as v WHERE v.data_loggerID = "+str(DevIDs[Counter]))
                        PassengerInfo = c.fetchall()
                    except:
                        PassengerInfo = []

                    # For each passenger in each vehicle
                    for p in range(0, len(PassengerInfo)):

                        # If the passenger is picked up, only need to stop at destination
                        if (PassengerInfo[1]=='TRUE'):     # picked up status
                            Stops.append(PassengerInfo[4]) # append destination

                        # Else, need to stop at origin as well and cannot optimize waypoints
                        else:
                            Stops.append(PassengerInfo[3]) # origin
                            Stops.append(PassengerInfo[4]) # destination
                            CanOptimizeWaypoints = False

                    # If car has more than one passenger, current directions involve waypoints;
                    if (len(Stops) > 1):
                        Waypoint_Values = Stops[0:len(Stops)-1]

                    # else set waypoints to None
                    else:
                        Waypoint_Values = None

                    # If there are existing passengers
                    if (len(Stops) != 0):

                        # Get directions with initial configuration
                        directions_result = gDirections.directions(

                            # Origin is the current location of the taxi
                            Locations[i],

                            # Destination is the last entry (destination) for the last passenger in stops
                            Stops[len(Stops)-1],

                            # Waypoints are existing passenger destinations
                            waypoints=Waypoint_Values,
                            # Have to set optimize to false if not all passengers are in the car
                            # because waypoints include origins and destinations - Can't stop at destination before origin
                            optimize_waypoints=CanOptimizeWaypoints,
                            mode="driving",
                            departure_time="now")

                        Current_Distance[Counter] = directions_result[0]['legs'][0]['distance']['value']
                        Current_Duration[Counter] = directions_result[0]['legs'][0]['duration']['value']

                    ############################
                    # Calculate Cost with Added Request
                    ############################
                    # Get directions with added passenger
                    directions_result = gDirections.directions(
                        # Origin is the current location of the taxi
                        str(Locations[i]),
                        # Destination is the that of the new ride request
                        str(Location),
                        # Waypoints are existing passenger destinations as well as new passenger pickup location
                        waypoints=Destination,
                        # Have to set optimize to false if not all passengers are in the car
                        # because waypoints include origins and destinations - Can't stop at destination before origin
                        optimize_waypoints=CanOptimizeWaypoints,
                        mode="driving",
                        departure_time="now")

                    New_Distance[Counter] = directions_result[0]['legs'][0]['distance']['value']
                    New_Duration[Counter] = directions_result[0]['legs'][0]['duration']['value']

                    # Calculated Incremental Distance and Duration, and select the vehicle with the lowest
                    # incremental cost to assign the new passenger
                    try:
                        c.execute("SELECT fuel_economy, vehicleID, vehicleAlias FROM vehicle WHERE data_loggerID = '"+DevIDs[Counter]+"'")
                        VehicleInfo = c.fetchall()
                    except:
                        response.message("Database issue")

                    try:
                        c.execute("SELECT SUM(p.gender) FROM passenger as p, vehicle as v WHERE p.vehicleID = v.vehicleID AND v.data_loggerID = '"+DevIDs[Counter]+"'")
                        GenderOutput = c.fetchall()
                        Female = 0
                        if (GenderOutput[0][0] != None):
                            Female = GenderOutput[0][0]
                    except:
                        response.message("db gender query not working")

                    try:
                        if (OpCost(Incremental_Distance, fuel_efficiency, fuel_price) + TimeCost(Incremental_Duration) + Gender_Cost > \
                            OpCost(New_Distance[Counter] - Current_Distance[Counter], VehicleInfo[0][0], fuel_price) + TimeCost(Incremental_Duration) + GenderCost(Gender, Seating_Requested, Female)):
                            Incremental_Distance = New_Distance[Counter] - Current_Distance[Counter]
                            Incremental_Duration = New_Duration[Counter] - Current_Duration[Counter]
                            fuel_efficiency = VehicleInfo[0][0]
                            Gender_Cost = GenderCost(Gender, Seating_Requested, Female)
                            Incremental_Vehicle = VehicleInfo[0][2]
                            Trip_Price = OpCost(Incremental_Distance, VehicleInfo[0][0], fuel_price)*Profit_Margin
                            #TaxiJval = Counter
                            TaxiJval = i
                    except:
                        TaxiJval = 0
                    Counter += 1


                # Generate passenger ID
                c.execute("SELECT MAX(passengerID) FROM passenger")
                MaxID_list = c.fetchall()
                if (MaxID_list[0][0]==None):
                    Max_ID = 0
                else:
                    Max_ID = MaxID_list[0][0]
                Max_ID += 1

                FinalDurationMat = gDistance.distance_matrix(Taxis[DevIDs[TaxiJval]], Location)
                FinalDurationVal = round(float(FinalDurationMat['rows'][0]['elements'][0]['duration']['value'])/60, 1)

                # Match new ride request with taxi in database
                c.execute("INSERT INTO passenger VALUES (" + str(Max_ID) + ", 0, '" + str(Location) + "', '" + str(Destination) + "'," + str(Female) + ", '" + str(Incremental_Vehicle) + "'," + str(Seating_Requested) + ")")
                conn.commit()

                # Inform passenger which vehicle they will be taking and expected trip cost
                response.message("Your vehicle is " + str(Incremental_Vehicle) + " and it will be arriving in " + str(FinalDurationVal) + " minutes. Your trip cost will be " + str(round(Trip_Price, 2)) + " Dhs")
        except:
            response.message("Your request could not be completed. Please check the format of your message or contact support.")

    # Send Twilio an XML response
    return Response(str(response), mimetype="application/xml"), 200
