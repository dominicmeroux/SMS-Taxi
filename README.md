# SMS_Taxi
Code to be uploaded soon.

# Introduction
I am a graduate student at the UC Davis Institute of Transportation Studies. This repository represents my solution for the 2016 Ford Code for Taxicabs Mobility Challenge.

# Web App

# AT&T Flow + M2X

# Databricks Big Data Analysis

This component is a big data analysis of historical OpenXC drive traces using Spark on Databricks to obtain performance information including fuel economy, driver behavior, and the ability to zoom in on specific critical time points, such as the moments leading up to an accident or occurrences of speeding. One crucial data value for the web app was average fuel economy values, which were added to the database used in the ride-matching algorithm when determining the lowest cost vehicle match. 

For a longer-term perspective, this big data analysis can be used to inform an optimal replacement strategy. This can play a significant role in fuel and emissions cost to the community, and Moroccan policymakers ran a program in 2014 to try to incentivize replacement of the common 1970’s and 80’s style Mercedes W123 taxis (Glon, 2014). A perfect analogy is the Ford Crown Victoria in the United States. Without data, an immediate decision could be to purchase the older inefficient vehicle at auction; however, a more fuel efficient vehicle like the Ford Focus, Fiesta, or C-Max may be more cost-effective when accounting for fuel and maintenance cost savings even if it is purchased new than to buy the older vehicle. The C++ dynamic programming algorithm included in this section is an early attempt of solving this problem, applying the classic “machine replacement” problem to indicating the optimal replacement age for a specified vehicle, taking into consideration the current vehicle and replacement vehicle specifications including fuel economy. 

# About the Algorithm Selection

Literature including Hayward (2016) suggest that the most cost-efficient transportation system is one with truly shared vehicles where all ride-matching in an urban area is optimized from a central dispatch. Furthermore, variants of the simulated annealing algorithm are often suggested as the most optimal solution, but as Jung, Jayakrishnan, & Choi (2015) note, in a taxi system with drivers (as opposed to autonomous taxis), the insertion heuristic approach is the best option to avoid driver confusion that could arise from reallocation of passenger pick-up assignments in the random perturbation process in simulated annealing. A future extension of this project could be a simulated annealing algorithm for an autonomous taxi system as in Jung, Jayakrishnan, & Park (2016), ideally with parallelized computation as accomplished with OpenMP in  Zbigniew J. Czech, Mikanik, and Skinderowicz (2010). The insertion heuristic however is an approach that is most plausible for optimizing the current paradigm of shared taxi passenger assignment. 
