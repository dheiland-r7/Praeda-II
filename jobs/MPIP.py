# Industrial Thermal  print validation  
######################################################
#                 PRAEDA II Module #MPIP             #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will print results for positive fingerprints 
#
#
import requests

def MPIP(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Set global variables
    count = 1

    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:

            # logFile.write(f"Printer validated on Network as  {data1}\n")
            logFile.write(f"\033[93mIDENTIFIED\033[0m:5:Finger Printed:{TARGET}:{PORTS}:{data1}:::::\n")
            print(f" Commercial printer validated on network with Finger Print of {data1}\n")

    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")


