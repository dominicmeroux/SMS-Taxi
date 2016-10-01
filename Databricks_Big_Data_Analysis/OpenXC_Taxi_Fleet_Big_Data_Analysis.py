# Databricks notebook source exported at Sat, 1 Oct 2016 03:13:55 UTC
########################################################################################################################
# VEHICLE DATA INSIGHTS - BIG DATA ANALYSIS OF OPENXC (http://openxcplatform.com) DRIVE TRACE FILES
########################################################################################################################

# Read in historical vehicle data to get insights into fuel economy (inform operating cost function in optimization) and other metrics; 
# Can be used to minimize operating cost by informing purchasing decisions and incentivizing better driver behavior 
# -- drivers get more likelihood of being the minimum cost vehicle and get assigned passengers if fuel economy is better
# -- incidents like excessive speeding and / or otherwise agressive driving can be detected
# -- in the event of an accident, driver liability (or innocence) can be proven with datapoints leading up to the accident

# Trace files used in this analysis were recorded from (rented) Zipcars as well as a personal vehicle
# Recording was done using the OpenXC Ford Reference VI (https://shop.openxcplatform.com)  
# and recorded via the Android OpenXC Enabler app on a 2013 Moto X and an Insignia 8" Model NS-P08A7100
# For this analysis files were cleaned (last line removed if partial JSON value, which can occur if the OpenXC Bluetooth signal 
# is broken, e.g. if the Reference VI is pulled out of the OBD port, or if the recording device is removed from Bluetooth connection range; 
# alternatively could have removed corrupt values column in Databricks) then uploaded to dbfs on Databricks

# This sample analyzed ~ 1.587 GB of drive trace data

# To establish a JDBC connection with an outside database (e.g. MySQL): 
# Follow one of these options 
# https://forums.databricks.com/questions/943/can-i-access-data-on-a-sql-database-from-databrick.html
# This would be useful to update vehicle information accessed to calculate operating cost (e.g. average fuel economy, etc.)

# Using Spark 2.0.0, Scala 2.1.0 Cluster on Databricks
# Code syntax may need to be modified slightly for use with different versions of Spark 

# TABLE OF CONTENTS
########################################################################################################################
# Annual Vehicle km Driven
# Fuel Economy Analysis
# Years to Positive ROI with More Efficient Vehicle
# Vehicle Speed Analysis (including count of incidences of speed > 115 km / hr)
# Frequency of Using Brakes
# Frequency of High Acceleration Events
# Headlamp Use
# High Beam Use
# Winshield Wiper Use
# Transmission Gear Position and Torque at Transmission
# Spatial Analysis - latitude, longitude
# RAW CAN DATA - a starting point for reading in and working with files of RAW CAN data
########################################################################################################################

# COMMAND ----------

# Import libraries
from pyspark.sql.functions import lit
from pyspark.sql import DataFrame
import pandas
import numpy
import datetime
from datetime import datetime

# COMMAND ----------

# The following filepaths are to folders (each corresponding to a vehicle) in the dbfs holding multiple JSON drive traces
# First must upload all drive traces for one vehicle to the dbfs, then copy the path to the folder containing these files. 
# Repeat for all vehicles. 
FilePath_3FADP4BJ5DM119777 = '/FileStore/tables/ctihs8f51474399879780' # Ford Fiesta
FilePath_3FADP4BJ5GM150984 = '/FileStore/tables/z7e1nahj1474399538799' # Ford Fiesta
FilePath_1FADP3K29FL326275 = '/FileStore/tables/9arkcf9y1474401915879' # Ford Focus
FilePath_1FADP3F21GL285393 = '/FileStore/tables/5y35vu7e1474434888619' # Ford Focus
FilePath_1FADP3F21FL245135 = '/FileStore/tables/jtn46ytl1471579054680' # Ford Focus
FilePath_1FADP3F21GL285457 = '/FileStore/tables/r3velry61471646875660' # Ford Focus
FilePath_1FADP5BU4EL513709 = '/FileStore/tables/hs8conyg1471647175714' # Ford C-Max
FilePath_1FMCU9J94GUC14197 = '/FileStore/tables/2r2nlyif1471647021373' # Ford Escape
FilePath_1FMCU9G94GUC63004 = '/FileStore/tables/cf53sxqe1474399686799' # Ford Escape
Cars = ['3FADP4BJ5DM119777', '3FADP4BJ5GM150984', '1FADP3K29FL326275', '1FADP3F21GL285393', '1FADP3F21FL245135', '1FADP3F21GL285457', '1FADP5BU4EL513709', '1FMCU9J94GUC14197', '1FMCU9G94GUC63004']

##### Using Spark 2.0, Scala 2.1.0 cluster on Databricks
df_3FADP4BJ5DM119777 = (spark.read.json(FilePath_3FADP4BJ5DM119777)).withColumn('VIN', lit(Cars[0]))
df_3FADP4BJ5GM150984 = (spark.read.json(FilePath_3FADP4BJ5GM150984)).withColumn('VIN', lit(Cars[1]))
df_1FADP3K29FL326275 = (spark.read.json(FilePath_1FADP3K29FL326275)).withColumn('VIN', lit(Cars[2]))
df_1FADP3F21GL285393 = (spark.read.json(FilePath_1FADP3F21GL285393)).withColumn('VIN', lit(Cars[3]))
df_1FADP3F21FL245135 = (spark.read.json(FilePath_1FADP3F21FL245135)).withColumn('VIN', lit(Cars[4]))
df_1FADP3F21GL285457 = (spark.read.json(FilePath_1FADP3F21GL285457)).withColumn('VIN', lit(Cars[5]))
df_1FADP5BU4EL513709 = (spark.read.json(FilePath_1FADP5BU4EL513709)).withColumn('VIN', lit(Cars[6]))
df_1FMCU9J94GUC14197 = (spark.read.json(FilePath_1FMCU9J94GUC14197)).withColumn('VIN', lit(Cars[7]))
df_1FMCU9G94GUC63004 = (spark.read.json(FilePath_1FMCU9G94GUC63004)).withColumn('VIN', lit(Cars[8]))

##### For Spark Version 1.6.1 instead use the following syntax for each vehicle:
#df_1FADP3F21FL245135 = (sqlContext.jsonFile(FilePath_1FADP3F21FL245135)).withColumn('VIN', lit(Cars[1]))

# append dataframes into one single dataframe
first = df_3FADP4BJ5DM119777 
rest = [df_3FADP4BJ5GM150984, df_1FADP3K29FL326275, df_1FADP3F21GL285393, df_1FADP3F21FL245135, df_1FADP3F21GL285457, df_1FADP5BU4EL513709, df_1FMCU9J94GUC14197, df_1FMCU9G94GUC63004]
DF = reduce(DataFrame.union, rest, first)

# save dataframe to Hive
DF.write.mode("overwrite").saveAsTable("Traces")

# COMMAND ----------

# In this section a rough estimate of annual km driven is calculated. This estimate is less accurate for newer vehicles, because the age subtraction is smaller; however, for most vehicles it can provide a good ballpark estimate with which to base TCO calculations on. The higher the km traveled in a year -> sooner positive ROI with a more fuel efficient (and / or cheaper alternative fuel) vehicle purchase

# Manual entry of vehicle model years (could alternatively be extracted from VIN numbers)
MY = [2013, 2016, 2015, 2016, 2015, 2016, 2014, 2016, 2016] ######## COULD EXTRACT FROM VIN

# Select only distinct maximum values per vehicle, to reduce this dataset to one value per vehicle - the current odometer reading
km = sqlContext.sql("SELECT DISTINCT VIN, MAX(DOUBLE(value)) AS odometer FROM traces WHERE name = 'odometer' GROUP BY VIN")

# Now that we have a very small dataset, no need for Spark past this point - convert to Pandas dataframe to iterate
kmPanda = km.toPandas()

# Iterate and append annual mileage estimate list by: odometer / vehicle age approximation
Annual_km_Est = []
for i in range(0, len(kmPanda['odometer'])):
  Annual_km_Est.append(kmPanda['odometer'][i] / ((2016 + (float(datetime.now().month)/12))-MY[i])) ####### swap out 2016 + 8.0/12 with current year + current month/12
  print Cars[i] + ": " + str(round(Annual_km_Est[i],0))+" km per year"

# COMMAND ----------

FE_data = sqlContext.sql("select distinct a.VIN as VIN, double(a.value) as fuel_consumed_since_restart, double(b.value) as odometer from (select a.timestamp, a.VIN, a.value from Traces as a where a.name = 'fuel_consumed_since_restart') inner join (select b.timestamp, b.VIN, b.value from Traces as b where b.name = 'odometer') on a.timestamp = b.timestamp and a.VIN = b.VIN")

# COMMAND ----------

# Output shows how performance is improved in the fuel economy calculation by using Spark
print "Total rows in our dataset: "
Total = DF.count()
print Total
print "\n"
print "Count of distinct rows for use in fuel economy analysis: "
FE_Count = FE_data.count()
print FE_Count
print "\n"
print "Using PySpark, we reduced the number of rows by " + str(round((1 - (float(FE_Count)/Total))*100,2)) + " percent, which allows us to use Pandas to iterate over the dataframe while minimizing computation time, or, depending on the dataset size and local machine's computational power, this may be allowing the computation to be made at all"

# COMMAND ----------

# Here there's no big data anaysis (just using plain Pandas), but at least the dataset has been limited to distinct values of odometer and fuel_consumed_since_restart (OpenXC measurements are taken frequently enough that a lot of values are repeated, so this reduction achieved in the previous block of code substantially reduces the amount of data that needs to be computed). Also note there may be future potential to use parallel computation with Pandas - http://sparklingpandas.com/#sparklingpandas
FE_data_PD = FE_data.toPandas()

# Declare Pandas dataframe to read mean fuel economy values into
FE = pandas.DataFrame(columns=('VIN','km_per_L'))

# For each observation
for i in range(1, len(FE_data_PD['odometer'])):
  
  # If the VIN is the same, and fuel consumption is positive - meaning we're not on a new trace file, since fuel_consumed_since_restart resets to 0 for each drive trace
  if ((FE_data_PD['VIN'][i] == FE_data_PD['VIN'][i-1] and FE_data_PD['fuel_consumed_since_restart'][i] > 0)):
       
       # Calculate fuel economy (Change in km) / (Change in fuel consumption)
    FE.loc[i] = [FE_data_PD['VIN'][i], float((FE_data_PD['odometer'][i] - FE_data_PD['odometer'][i-1])/(FE_data_PD['fuel_consumed_since_restart'][i] - FE_data_PD['fuel_consumed_since_restart'][i-1]))]

# COMMAND ----------

# Now that calculation has been performed, bring back into PySpark dataframe
FEDF = sqlContext.createDataFrame(FE)

# Register dataframe as a temporary table
sqlContext.registerDataFrameAsTable(FEDF, "F")

# Calculate average fuel efficiency in liters per 100 km, grouped by VIN, removing outliers of km_per_L values less than 10 or greater than 100
FinalFE = sqlContext.sql("select VIN, round(avg(100/((km_per_L))),3) as liters_aux_100_km from F where km_per_L > 10 and km_per_L < 100 group by VIN")

display(FinalFE)
# For reference, the French 2016 Ford Ka+ (small car) has a rating of 5.0 L per 100 km; the 2016 Ford Kuga 1.5 EcoBoost 150 ch S&S has a rating of 6.2 L per 100 km 
# for mixed (city and highway) driving. 
# 
# Additionally, carlabelling.ademe.fr lists several models of the Ford Focus with the following fuel efficiency ranges: 
# Urb: 5,5 - 10,0 (city)
# Ex-urb: 3,6 - 6,3 (highway)
# Mixte: 4,3 - 7,7 (combined rating)

##### ***** Note the single outlier had a much smaller sample of drive traces *****

# COMMAND ----------

# Pivot table showing numerical values
display(FinalFE)

##### ***** Note the single outlier had a much smaller sample of drive traces *****

# COMMAND ----------

# Assign fuel price per liter
Fuel_Price = 3.65

# Assign previously calculated fuel economy numbers to Pandas dataframe
fuel = FinalFE.toPandas()

# Calculate annual fuel cost
Annual_Fuel_Cost = []
for i in range(0, len(Cars)):
  Annual_Fuel_Cost.append((Annual_km_Est[i] / 100) * fuel['liters_aux_100_km'][i] * Fuel_Price)

# 20% reduction in fuel consumption (or fuel costs, if considering an alternative fuel)
Fuel_Efficiency_Benefit = 0.2

# Higher cost of more fuel efficient vehicle (Dhs)
Incremental_Cost = 12000

# Calculate years to positive ROI on more fuel efficient vehicle purchase
yearsToROI = []
print "Car" + "\t\t\t" + "Years to Positive ROI"
for i in range(0, len(Cars)):
  yearsToROI.append(float(Incremental_Cost) / (Annual_Fuel_Cost[i] * Fuel_Efficiency_Benefit))
  print str(Cars[i]) + "\t" + str(yearsToROI[i])

# COMMAND ----------

# Display first 1000 observations of speed for a specific vehicle (in this case 1FADP5BU4EL513709) and within a certain timeframe
Speed = sqlContext.sql("SELECT VIN, timestamp, DOUBLE(value) as vehicle_speed FROM traces WHERE name = 'vehicle_speed' and VIN = '1FADP5BU4EL513709' and DOUBLE(timestamp) > 1470274735")
display(Speed)

# COMMAND ----------

# Incidents of speed above 115 km / hr

# NOTE: OpenXC vehicle speed values are read at a frequency of 10Hz
Speed_All_Vehicles = sqlContext.sql("SELECT VIN, timestamp, DOUBLE(value) as vehicle_speed FROM traces WHERE name = 'vehicle_speed'")

# Filter speed values for those above 115 km / hr
highwaySpeeding = Speed_All_Vehicles.filter(Speed_All_Vehicles.vehicle_speed > 115).groupBy(Speed_All_Vehicles.VIN).count()
display(highwaySpeeding)

# COMMAND ----------

brake_pedal_status = sqlContext.sql("SELECT VIN, timestamp, value AS brake_pedal_status FROM traces WHERE name = 'brake_pedal_status' group by VIN, timestamp, value")

# Ratio of braking to not braking, indicator of driving in traffic and/or aggressive driving
# Important result is that if drive traces are a representative sample of driving pattern (e.g. rather than just one trip), 
# this can indicate which vehicles may need brakes replaced sooner, and may be indicative of other costs (higher fuel consumption, etc.)
True = brake_pedal_status.filter(brake_pedal_status.brake_pedal_status=='true').groupBy(brake_pedal_status.VIN).count()
False = brake_pedal_status.filter(brake_pedal_status.brake_pedal_status=='false').groupBy(brake_pedal_status.VIN).count()

# Now convert to Pandas, because 1) this allows for iterating and 2) we now have a very small dataframe to work with, so no need to parallelize computation here
T = True.toPandas()
F = False.toPandas()

# Print out ratio of breaks on to off (higher ratio is indicative of more breaking)
# Lists x and y store these ratios in case further analysis is desired
x = []
y = []
print "VIN" + "\t\t\t" + "Ratio true to false"
for i in range(0, len(T)):
  print T['VIN'][i] + "\t" + str(round((float(T['count'][i]) / F['count'][i]), 2))
  x.append(str(T['VIN'][i]))
  y.append(round((float(T['count'][i]) / F['count'][i]), 2))

# COMMAND ----------

# Distribution of acceleration events by how far the accelerator was pushed. The right tail of this distribution is indicative of the extent of agressive driving.
accelerator_pedal_position = sqlContext.sql("SELECT VIN, timestamp, DOUBLE(value) AS accelerator_pedal_position FROM traces WHERE name = 'accelerator_pedal_position'")

# COMMAND ----------

# Count of total accelerator pedal position values, by VIN
TotalCount = accelerator_pedal_position.groupBy(accelerator_pedal_position.VIN).count()

# Count of "aggressive" accelerator pedal position values, by VIN
Aggressive = accelerator_pedal_position.filter(accelerator_pedal_position.accelerator_pedal_position > 30).groupBy(accelerator_pedal_position.VIN).count()

# COMMAND ----------

display(Aggressive)

# COMMAND ----------

# Now that we have a small dataframe of one value per vehicle, convert to a Pandas dataframe and print out results
TotalPanda = TotalCount.toPandas()
AggressivePanda = Aggressive.toPandas()

print "VIN" + "\t\t\t" + "Ratio Greater than 30%"
for i in range(0, len(TotalPanda)):
  print TotalPanda['VIN'][i] + "\t" + str(round((float(AggressivePanda['count'][i]) / TotalPanda['count'][i]), 2))

# COMMAND ----------

# Can be useful in some cases including examining how the steering wheel was turned right before an accident, as well as simply another measure of aggressive driving
SteeringAngle = sqlContext.sql("select VIN, timestamp, value as steering_wheel_angle from traces where name = 'steering_wheel_angle'")
display(SteeringAngle)

# COMMAND ----------

Headlamp = sqlContext.sql("select VIN, timestamp, value as headlamp_status from traces where name = 'headlamp_status'")
Headlamp_Total = Headlamp.groupBy(Headlamp.VIN).count()
Headlamp_On = Headlamp.filter(Headlamp.headlamp_status == "true").groupBy(Headlamp.VIN).count()

# COMMAND ----------

# Number of seconds headlamps were on in total (indicator of future need for replacement)
# NOTE: no visualization / data shows up if headlamps were never used during data recording
display(Headlamp_On)

# COMMAND ----------

Highbeam = sqlContext.sql("select VIN, timestamp, value as high_beam_status from traces where name = 'high_beam_status'")
Highbeam_On = Highbeam.filter(Highbeam.high_beam_status == "true").groupBy(Highbeam.VIN).count()

# COMMAND ----------

# Number of seconds headlamps were on in total (indicator of future need for replacement)
# NOTE: no visualization / data shows up if high beams were never used during data recording
display(Highbeam_On)

# COMMAND ----------

Windshield_Wiper = sqlContext.sql("select VIN, timestamp, value as windshield_wiper_status from traces where name = 'windshield_wiper_status'")
Windshield_Wiper_On = Windshield_Wiper.filter(Windshield_Wiper.windshield_wiper_status == "true").groupBy(Windshield_Wiper.VIN).count()

# COMMAND ----------

# Number of seconds windshield wipers were on in total
# NOTE: not all vehicles displayed if some never used windshield wipers during data recording
display(Windshield_Wiper_On)

# COMMAND ----------

# This section is more for car company engineers / mechanics to examine whether the vehicle transmissions are shifting as expected 
Shifting = sqlContext.sql("select distinct a.VIN as VIN, a.value as transmission_gear_position, double(b.value) as torque_at_transmission from ((select a.timestamp, a.VIN, a.value from traces as a where a.name = 'transmission_gear_position') inner join (select b.timestamp, b.VIN, b.value from traces as b where b.name = 'torque_at_transmission') on a.timestamp = b.timestamp and a.VIN = b.VIN)")

# COMMAND ----------

# Arbitrary visualization
display(Shifting)

# COMMAND ----------

TripLocations = sqlContext.sql("select distinct a.VIN as VIN, a.timestamp, double(a.value) as latitude, double(b.value) as longitude from (select a.timestamp, a.VIN, a.value from traces as a where a.name = 'latitude') inner join (select b.timestamp, b.VIN, b.value from traces as b where b.name = 'longitude') on a.timestamp = b.timestamp and a.VIN = b.VIN")

# COMMAND ----------

TripLocations.printSchema()

# COMMAND ----------

# save dataframe to Hive, and access the data via visualization software (e.g. Tableau) or spatial analytics software (e.g. ArcGIS)
#
# Note: an upgraded subscription (from Community Edition) of Databricks must be used for information needed to connect Hive tables to Tableau and other software
#       https://docs.cloud.databricks.com/docs/latest/databricks_guide/01%20Databricks%20Overview/10%20REST%20API.html
#
# Tableau: https://forums.databricks.com/questions/267/how-do-i-integrate-tableau.html
# ArcGIS: https://github.com/Esri/spatial-framework-for-hadoop
#
# Analysis could include looking at whether drivers were following the speed limit, using the Google Maps Roads API https://developers.google.com/maps/documentation/roads/intro

TripLocations.write.mode("overwrite").saveAsTable("TripLocations")

# COMMAND ----------

# Alternatively, you can filter out the dataset for a specific trip or vehicle, and run an anlysis in Pandas with that dataset
SpecificVehicle = TripLocations.filter(TripLocations.VIN == '1FMCU9J94GUC14197')
#SpecificTrip = TripLocations.filter(TripLocations.timestamp > 1468745052.918 & TripLocations.timestamp < 1468745420.402 & TripLocations.VIN == '1FMCU9J94GUC14197')

# COMMAND ----------

# The below scatterplot is an accurate representation without having a map overlay - the Ford C-Max was driven in San Diego, CA; one of the Ford Fiesta sedans was driven to Sunnyvale, CA; and the other cars were driven in the Sacramento, CA region. Also could use the Google Maps API to convert latitude and longitude coordinates to zip codes to produce a heat map by zip code, but would likely run into API limits without a paid account. 
display(TripLocations)

# COMMAND ----------

# This section is only meant to show the beginning of how custom analysis of additional vehicle data parameters could be handled (or data anlysis with vehicles not covered by proprietary OpenXC vehicle-specific firmware)

# First generate firmware to read raw CAN data, with documentation specified here: 
# http://vi-firmware.openxcplatform.com/en/latest/config/raw-examples.html
# Next, connect the VI to a laptop with the OpenXC Python library installed, and run "$ openxc-dump > filename.json"
# Upload the trace file to the dbfs

# Read in the raw trace file
FocusRaw = sqlContext.read.format('json').load("/FileStore/tables/sbaqmpcc1468294992567/RAW_LimitedDATAOUTPUT_1FADP3F21FL245135.json")

# Save dataframe to Hive
FocusRaw.write.mode("overwrite").saveAsTable("FocusRaw1")

# Below is the subset of data, showing PIDs supported by the vehicle. From this point, match with known PIDs (https://en.wikipedia.org/wiki/OBD-II_PIDs) and others you may have access to (as an automaker or another entity with access to proprietary PID information) and translate HEX values in the raw output, or formulate custom OpenXC firmware to output the desired values (e.g. binary, floating point, etc.) for analysis
sqlContext.sql("select distinct id from FocusRaw1 order by id asc").collect()

# Also, can use OpenXC Python CLI tools for finding PIDs and determining possible diagnostic requests, e.g. 
# "$ openxc-obd2scanner" http://python.openxcplatform.com/en/master/tools/obd2scanner.html
# "$ openxc-scanner" http://python.openxcplatform.com/en/master/tools/scanner.html
