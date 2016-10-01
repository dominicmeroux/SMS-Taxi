# SMS Taxi Platform - Introduction

I am a graduate student at the UC Davis Institute of Transportation Studies. This repository represents my solution for the 2016 Ford Code for Taxicabs Mobility Challenge. My solution, called SMS taxi, receives ride requests via text message; matches passengers with taxis using OpenXC with AT&T’s iOT platforms Flow and M2X; and uses Spark on Databricks to analyze cumulative OpenXC data to inform the ride-matching algorithm’s fuel cost function, allow taxi fleet management to understand cost performance metrics, and use a data-driven strategy to provide customers with the most cost-efficient taxis. 

The web app can be accessed at http://dmeroux.pythonanywhere.com. 

The competition web page is located at http://code4cabs.devpost.com. 

# Web App

The Python Flask web app receives on-demand ride requests via text message through Twillio and matches these requests with vehicles using an insertion heuristic. In this approach, the algorithm determines whether there are any taxis within an acceptable driving time from the pickup location and with adequate seating capacity. Of the taxis meeting these criteria, the ride request is added to the taxi where the cumulative trip operational cost of taking on these additional passenger(s) is lowest. Users with similar origins and destinations are more likely to be paired, and taxis with a more fuel efficient driving record as indicated by OpenXC data are more likely to get rides because they have a lower operating cost per kilometer. 

To address the mini challenge of improving safety for female riders, when a user specifies preference for an all-female taxi, the algorithm includes a cost penalty for cabs with male passengers; however, if no female-only taxis are available, the algorithm still matches the requester with a ride, because it is less safe to have no access to transportation.

In addition to user ride requests, drivers notify the system when a passenger has been picked up or dropped off so that availability and passenger status are known. As a part of the next component I will describe, when OpenXC data indicates a fuel level that is below a predetermined critical threshold, the web app receives a notification text message and automatically adds a fuel station as a waypoint in the taxi’s itinerary; 


# AT&T Flow + M2X

Real-time vehicle information is gathered using AT&T Flow, based on IBM’s Node Red platform for internet of things devices, to parse incoming OpenXC messages for desired data points including location and fuel level. These values are then sent from Flow to the AT&T M2X time series data storage service only when values change. For example, OpenXC fuel level values are read in at a frequency of 2HZ, but the percentage fuel level remains the same over most of these observations. Sending only unique values reduces redundancy, which minimizes data storage and processing costs in a production environment.

The OpenXC data can be uploaded in real-time from a cellular device using a bluetooth connection to a vehicle interface or from a pre-recorded trace via the OpenXC Enabler app.

# Databricks Big Data Analysis

Big data analysis of historical OpenXC drive traces is performed using Spark on Databricks to obtain fleet performance metrics including average fuel economy, which is added to the database used in the ride-matching algorithm when determining the lowest cost vehicle match. Additional insights include driver behavior and the ability to zoom in on specific critical time points, such as the moments leading up to an accident or occurrences of speeding.

For a longer-term perspective, this big data analysis can be used to inform an optimal replacement strategy. This can play a significant role in fuel and emissions cost to the community. Moroccan policymakers ran a program in 2014 to incentivize replacement of the common 1970’s and 80’s style Mercedes W123 taxis (Glon, 2014). Without data, purchasing the older inefficient vehicle may seem to be the lowest cost option; however, a more fuel efficient vehicle may be more cost-effective when accounting for fuel and maintenance cost savings. The C++ dynamic programming algorithm included in this section is an early attempt at solving this problem, applying the classic “machine replacement” approach to indicate the optimal replacement age for a specified vehicle.

# About the Algorithm Selection

Literature including Hayward (2016) suggest that the most cost-efficient transportation system is one with truly shared vehicles where all ride-matching in an urban area is optimized from a central dispatch. Furthermore, variants of the simulated annealing algorithm are often suggested as the most optimal solution, but as Jung, Jayakrishnan, & Choi (2015) note, in a taxi system with drivers (as opposed to autonomous taxis), the insertion heuristic is the best option to avoid driver confusion that could arise from reallocation of passenger pick-up assignments in the random perturbation process of simulated annealing. A future extension of this project could be a simulated annealing algorithm for an autonomous taxi system as in Jung, Jayakrishnan, & Park (2016), ideally with parallelized computation as accomplished with OpenMP by Zbigniew J. Czech, Mikanik, and Skinderowicz (2010). The insertion heuristic however is an approach that is most plausible considering the current paradigm.

# References

Czech, Zbigniew J., Wojciech Mikanik, and Rafał Skinderowicz. “Implementing a Parallel Simulated Annealing Algorithm.” In Parallel Processing and Applied Mathematics, edited by Roman Wyrzykowski, Jack Dongarra, Konrad Karczewski, and Jerzy Wasniewski, 6067:146–55. Berlin, Heidelberg: Springer Berlin Heidelberg, 2010. http://link.springer.com/10.1007/978-3-642-14390-8_16.

Fatnassi, Ezzeddine, Olfa Chebbi, and Jouhaina Chaouachi. “Discrete Honeybee Mating Optimization Algorithm for the Routing of Battery-Operated Automated Guidance Electric Vehicles in Personal Rapid Transit Systems.” Swarm and Evolutionary Computation 26 (February 2016): 35–49. doi:10.1016/j.swevo.2015.08.001.

“Fuel Economy and CO2 Emissions of Light-Duty Vehicles in Morocco.” Centre for Environment and Development for the Arab Region and Europe (CEDARE), February 2015. http://www.unep.org/Transport/new/pcfv/pdf/GFEI_Morocco_Report_English.pdf.

Glon, Ronan. “Morocco Encouraging Taxi Drivers to Scrap Mercedes w123s.” Ran When Parked, May 6, 2014. https://ranwhenparked.net/2014/05/06/morocco-encouraging-taxi-drivers-to-scrap-w123s/.
Hayward, Leslie. “OECD’s International Transport Forum Models Ideal Yet Simple Urban Transit System.” The Fuse, July 29, 2016. http://energyfuse.org/oecds-international-transport-forum-models-ideal-yet-simple-urban-transit-system/.

Jung, Jaeyoung, Joseph Y.J. Chow, R. Jayakrishnan, and Ji Young Park. “Stochastic Dynamic Itinerary Interception Refueling Location Problem with Queue Delay for Electric Taxi Charging Stations.” Transportation Research Part C: Emerging Technologies 40 (March 2014): 123–42. doi:10.1016/j.trc.2014.01.008.

Jung, Jaeyoung, R. Jayakrishnan, and Keechoo Choi. “A Dually Sustainable Urban Mobility Option: Shared-Taxi Operations With Electric Vehicles.” International Journal of Sustainable Transportation, September 30, 2015, 150930131156001. doi:10.1080/15568318.2015.1092057.

Jung, Jaeyoung, R. Jayakrishnan, and Ji Young Park. “Dynamic Shared-Taxi Dispatch Algorithm with Hybrid-Simulated Annealing: Dynamic Shared-Taxi Dispatch Algorithm.” Computer-Aided Civil and Infrastructure Engineering 31, no. 4 (April 2016): 275–91. doi:10.1111/mice.12157.

Lin, Yeqian, Wenquan Li, Feng Qiu, and He Xu. “Research on Optimization of Vehicle Routing Problem for Ride-Sharing Taxi.” Procedia - Social and Behavioral Sciences 43 (2012): 494–502. doi:10.1016/j.sbspro.2012.04.122.

Sdoukopoulos, Eleftherios, Pinar Kose, Ayelet Gal-Tzur, Mohamed Mezghani, Maria Boile, Ebtihal Sheety, and Lambros Mitropoulos. “Assessment of Urban Mobility Needs, Gaps and Priorities in Mediterranean Partner Countries.” Transportation Research Procedia 14 (2016): 1211–20. doi:10.1016/j.trpro.2016.05.192.
