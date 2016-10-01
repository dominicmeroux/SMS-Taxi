# OpenXC Stream
====================

In a nutshell
-----------------
This flow accepts streaming OpenXC data through a given endpoint once deployed,
filters the data for desired datapoints, and sends these values to the 
specified corresponding device in M2X. 

Prerequisites
-------------
Set up AT&T M2X and Flow accounts, set up a device in M2x, and
set up specified streams. Using this flow, the streams would be 
"fuel_level", "fuel_economy", "vehicle_speed", and "accelerator_pedal_position". 

Also, you must have a way to send streaming OpenXC data to the Flow endpoint. 
See http://openxcplatform.com for details on the OpenXC platform. 

Flow description
-----------------
This flow receives fuel level, fuel economy, vehicle speed, and 
accelerator pedal position. This flow serves as a template for adding 
functionality. For example, if you want to add a text trigger using Twillio, 
send data to a database, apply Watson insights, etc. this is all possible.

Furthermore, if you want to add more data points, follow the approach specified
in the other nodes. 

Additional information
----------------------
This flow was created as one part to an entry in the 2016 Ford Code for 
Taxicabs challenge hosted by DevPost. 




