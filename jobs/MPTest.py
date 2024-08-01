# Generic finger print validation  
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will print results for positive fingerprints 
#
#
import requests

def MPTest(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Set global variables
    count = 1

    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:

            logFile.write(f"Device validated on network with Finger Print of {data1}\n")
            print(f"MFP device validated on network with Finger Print of {data1}\n")

    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")


