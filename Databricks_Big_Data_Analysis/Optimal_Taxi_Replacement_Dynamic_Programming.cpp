// 
// DESCRIPTION: 
// 
// This program accepts user inputs on a specific vehicle and applies a dynamic programming
// "Machine Replacement Problem" approach. This program is still in development, but the concept
// is that OpenXC data insights obtained in the Databricks big data analysis could be used here
// by fleet management to determine the optimal age to replace a taxi, so that taxis are not kept 
// in service longer than is optimal. 
//
//  Copyright © 2016 Dominique Meroux. All rights reserved.
//
/////////////////////////////////////////////////////////////////////
// IMPROVEMENTS FOR PRODUCTION VERSION: 
// 1) Modify cost values
// 2) Add an outer to loop iterate over all vehicles in fleet
// 3) Automate output DP report
//
//
/////////////////////////////////////////////////////////////////////
#include <iostream>
#include <math.h>
#include <fstream>
#include <ctime>

using namespace std;

/////////////////////////////////////////////////////////////////////
// Declare variables
int PlanningHorizon;   // planning Horizon
int MY;                // current model year
int Current_Age;       // current age (calculated)
float Purchase_Price;  // purchase price
float Annual_Mileage;  // annual mileage (estimate)
float Current_FE;      // current vehicle's fuel economy (estimate)
float New_FE;          // new vehicle fuel economy

float break_pedal_status_ratio;
float accelerator_pedal_position_ratio;
float headlamp_status_ratio;
float highbeam_status_ratio;
float windshield_wiper_status_ratio;

float AggressiveDrivingCost = 0; 
float WeatherCost = 0; 
float LightReplacementCost;

float headlamp_price = 30; 
float highbeam_price = 50; 
int headlamp_hours = 30000;
int highbeam_hours = 30000; 

/////////////////////////////////////////////////////////////////////
// Define functions
// Maintenance cost
float Maintenance(float Veh_Age, float accelerator_pedal_position_ratio, float break_pedal_status_ratio, 
    float headlamp_status_ratio, float highbeam_status_ratio, float windshield_wiper_status_ratio,
    int headlamp_status_seconds, int highbeam_status_seconds){
    
    LightReplacementCost = 0

    // Now make (or draw from output of PySpark analysis) continuous function of age, breaking + acceleration + windshield wipers + lights + highbeams
    AggressiveDrivingCost = accelerator_pedal_position_ratio*100 +  break_pedal_status_ratio*100;
    WeatherCost = windshield_wiper_status_ratio*50 + highbeam_status_ratio*500;
    
    // Add in light replacement costs if use is projected to exceed the replacement threshold
    if(headlamp_status_seconds / 3600 >= headlamp_hours){
        LightReplacementCost += headlamp_price;
    }
    if (highbeam_status_seconds / 3600 >= highbeam_hours){
        LightReplacementCost += highbeam_price; 
    }

    return Veh_Age*100 + AggressiveDrivingCost + AggressiveDrivingCost + LightReplacementCost;
}

// Fuel cost
float Fuel(float L_per_100km, float Annual_km){
    // Now make function of MPG based on current vehicle vs. new vehicle (input would be vehicle type?)
    return A*3; 
}

// Salvage value
float Salvage(int Age){
    // Now make function of vehicle, age, breaking + acceleration + windshield wipers + lights + highbeams
    return Purchase_Price - exp(Age); 
}

/////////////////////////////////////////////////////////////////////
// Main function
int main(){
    
    /////////////////////////////////////////////////////////////////////
    // Fleet Administrator enters planning horizon and new vehicle information
    // Ideal for assessing a group of vehicles (e.g. all of the MY 2007 Ford Focus 2.0L gas cars)

    // Planning horizon
    cout << "Planning Horizon: "; 
    cin >> PlanningHorizon; 

    // New vehicle information
    cout << "Minimum cost desired new vehicle information" << endl; 
    
    // New vehicle fuel economy 
    cout << "Fuel Economy: ";
    cin >> New_FE; 

    // 
    cout << "Age (0 if new, 1 or more if used): ";
    
    // New vehicle purchase price
    cout << "Purchase Price: ";
    cin >> Purchase_Price;

    // Current vehicle information
    cout << endl << "Now enter information on your current vehicle" << endl; 

    // Current vehicle fuel economy
    cout << "Fuel Economy: ";
    cin >> Current_FE; 

    // OpenXC break_pedal_status true to false ratio
    cout << "Break pedal status true to false ratio: ";
    cin >> break_pedal_status_ratio;

    // OpenXC accelerator_pedal_position 
    // share of measurements greater than 30%
    cout << "Share of accelerator pedal position measurements greater than 30%: ";
    cin >> accelerator_pedal_position_ratio; 

    // headlamp_status true to false ratio
    cout << "Headlamp status true to false ratio: ";
    cin >> headlamp_status_ratio;

    // highbeam_status true to false ratio
    cout << "Highbeam status true to false ratio: ";
    cin >> highbeam_status_ratio;

    // windshield_wiper_status true to false ratio
    cout << "Windshield wiper status true to false ratio: ";
    cin >> windshield_wiper_status_ratio;

    // ...
    
    /////////////////////////////////////////////////////////////////////
    // Read input files
    // Model Year, calculate vehicle age
    ifstream MYval("/Users/dmeroux/MY.txt");
    
    // Error catching - if there is no file found as indicated
    if(!MYval){
        // print error message
        cout << "Didn't find a file with this filename in the specified directory" << endl;
        
        // terminate program
        exit (EXIT_FAILURE);
    }
    
    // Read in model year
    cout << "Vehicle Model Year: " << "\t";
    MYval >> MY; 
    cout << MY << endl; 
    
    // Calculate vehicle age based on model year
    Current_Age = 2016 - MY;
    time_t now = time(0);
    tm *ltm = localtime(&now);
    Current_Age = (1900 + ltm->tm_year) - MY;

    // Annual mileage
    Annual_Mileage = 59000; 

    
    
    /////////////////////////////////////////////////////////////////////
    // Dynamically allocate memory for matrix representing each stage and state
    // Matrix f:        cost function
    // Matrix Plan: 
    // Array PermPath:  final path
    // 
    float** f = new float*[PlanningHorizon]; bool** Plan = new bool*[PlanningHorizon];
    for (int i = 0; i <= PlanningHorizon; i++){
        f[i] = new float[PlanningHorizon];
        Plan[i] = new bool[PlanningHorizon];
    }
    int* PermPath = new int[PlanningHorizon];
    
    // Initialize matrix with all zero values
    for (int t = 0; t <= PlanningHorizon; t++) {
        PermPath[t] = 0;
        for (int i = 0; i <= PlanningHorizon; i++){
            f[i][t] = 0;
        }
    }
    
    /////////////////////////////////////////////////////////////////////
    // For each time step in planning horizon
    for (int t = PlanningHorizon; t >= 0; t--) {
        
        //////// NOW EXTEND AGE RANGE FROM 0 TO PLANNING HORIZON + AGE
        //for (int Veh_Age = 1; Veh_Age <= PlanningHorizon + Current_Age; Veh_Age++){
        for (int Veh_Age = 1; Veh_Age <= PlanningHorizon; Veh_Age++){
            /////////////////////////////////////////////////////////////////////
            //
            //if (t >= Current_Age + Veh_Age){
            if (t >= Veh_Age){
                // At the final stage - end of the planning horizon
                if (t == PlanningHorizon){
                    f[t][Veh_Age] = - Salvage(Veh_Age);
                }
        
                /////////////////////////////////////////////////////////////////////
                // DYNAMIC PROGRAMMING DECISION: KEEP OR REPLACE? 
                // All other stages k = T...1, and vehicle is not new or at maximum age
                else if (t > 0){
                    // If optimal decision is keep (cost and < 3 yrs old)
                    if (// Current vehicle
                        Maintenance(Veh_Age, accelerator_pedal_position_ratio, break_pedal_status_ratio, headlamp_status_ratio, 
                        highbeam_status_ratio, windshield_wiper_status_ratio) + Fuel(Current_FE) + f[t + 1][Veh_Age + 1] 
                        // New vehicle
                        < Maintenance(1, accelerator_pedal_position_ratio, break_pedal_status_ratio, headlamp_status_ratio, 
                        highbeam_status_ratio, windshield_wiper_status_ratio) + Fuel(New_FE) + Purchase_Price - Salvage(Veh_Age) + f[t + 1][1]){
                        
                        f[t][Veh_Age] = Maintenance(Veh_Age + 1, accelerator_pedal_position_ratio, break_pedal_status_ratio, headlamp_status_ratio, 
                        highbeam_status_ratio, windshield_wiper_status_ratio) + Fuel(Current_FE) + f[t + 1][Veh_Age + 1]; 
                    }
                    // If optimal decision is replace
                    else{
                        // If index indicating replacement is false, assign in value true
                        if (Plan[t][Veh_Age] == false){
                            Plan[t][Veh_Age] = true;
                            PermPath[t + 1] = Veh_Age;

                            // Calculate cost in new year
                            //f[t][0] = Maintenance(1) + Fuel(1) + Purchase_Price - Salvage(Veh_Age) + f[t + 1][1];
                    
                            // Re-set age to 0    
                            //Veh_Age = 0; 
                        }
                        f[t][Veh_Age] = Maintenance(1, accelerator_pedal_position_ratio, break_pedal_status_ratio, headlamp_status_ratio, 
                        highbeam_status_ratio, windshield_wiper_status_ratio) + Fuel(New_FE) + Purchase_Price - Salvage(Veh_Age) + f[t + 1][1];
                    
                        // Future age - vehicle is removed from fleet
                        //f[t + 1][Veh_Age + 1] = 0;
                    }
                }

                
                // Increment vehicle age by 1
                //Veh_Age -= 1; 
            }
            else if (t == 0){
                    f[t][0] = Purchase_Price + Maintenance(1) + f[t + 1][1];
            }
            


            
        }
        
        
    }
    /////////////////////////////////////////////////////////////////////
    // print out results
    cout << "Cost Results" << endl;
    for (int t = 0; t <= PlanningHorizon; t++) {
        for (int i = 0; i <= PlanningHorizon; i++){
            cout << f[i][t] << "\t";
        }
        cout << endl;
    }
    cout << endl; 
    
    cout << "Optimal Replacement Year" << endl;
    for (int i = 0; i <= PlanningHorizon; i++){
        cout << PermPath[i] << endl;
    }
    cout << endl; 
    
    //cout << "" << endl;
    //for (int t = PlanningHorizon - 1; t >= 0; t--) {
    //    for (int age = 0; age < PlanningHorizon; age++){
    //        cout << Plan[age][t] << "\t";
    //    }
    //    cout << endl;
    //}
    
    /////////////////////////////////////////////////////////////////////
    // free memory
    for (int i = 0; i <= PlanningHorizon; i++){
        delete [] f[i];
        delete [] Plan[i];
    }
    delete [] f; delete [] Plan; delete [] PermPath;
    
    return 0;
}
