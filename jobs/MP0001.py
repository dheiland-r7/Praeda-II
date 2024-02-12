# Xerox default password validation check module 
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Xerox models
#     VersaLink C7*** & B7***
#
#
#
#
import requests

def MP0001(TARGET, PORTS, web, OUTPUT, LOGFILE):
    # Set global variables
    count = 1

    # Open output file for logging
    try:
        with open(f'./{OUTPUT}/{LOGFILE}.log', 'a') as logFile:

# URL to connect to
            url = f"http{web}://{TARGET}:{PORTS}/LOGIN.cmd?NAME=YWRtaW4%3D&PSW=MTExMQ%3D%3D" # incoming target data

# Expected JSON response
            expected_response = {
                "result": "0",
                "errorCode": "0",
                "koDefault": "0",
                "snmpDefault": "0",
                "globalIP": "0",
                "passwordChangeRequired": "0"
            } 

            try:
               # Send an HTTP(S) GET request to the Xerox MFPs URL
               response = requests.get(url, verify=False)

               # Check if the request was successful (status code 200)
               if response.status_code == 200:
                   # Parse the JSON response
                   json_response = response.json()

                   # Check if the JSON response matches the expected response
                   if json_response == expected_response:
                       #print("SUCCESS: The Xerox devices Admin password is 1111\n")
                       print("SUCCESS: The Xerox devices Admin password is 1111\n")
                       logFile.write(f"SUCCESS: Xerox Device credintial are default :{TARGET}:{PORTS}:Admin:1111\n")
                   else:
                      print("FAIL: The Xerox devices admin password has been changed\n")
                      logFile.write(f"FAIL: The Xerox devices admin password has been changed:{TARGET}:{PORTS}:Admin:?\n")
               else:
                  print(f"HTTP request failed with status code: {response.status_code}")
                  logFile.write(f"HTTP request failed with status code: {response.status_code}") 

            except requests.exceptions.RequestException as e:
               print(f"An error occurred while making the HTTP request: {str(e)}")
            except ValueError as ve:
               print(f"Failed to parse JSON response: {str(ve)}")

    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")


