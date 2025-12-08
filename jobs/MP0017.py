# Zebra default password validation check module 
######################################################
#                 PRAEDA II Module #MP0017           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
import requests

def MP0017(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            # Build login POST request
            url = f"http{web}://{TARGET}:{PORTS}/authorize"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": f"http{web}://{TARGET}",
                "Referer": f"http{web}://{TARGET}/settings",
                "User-Agent": "Mozilla/5.0",
            }
            payload = "0=admin&1=1234"

            response = requests.post(url, headers=headers, data=payload, verify=False)

            if response.status_code == 200:
                if "Access Granted" in response.text:
                    print(f"\033[91mSUCCESS\033[0m: Zebra printer at {TARGET} uses default credentials (admin:1234)\n")
                    logFile.write(f"\033[91mSUCCESS\033[0m:1:Zebra default credential:{TARGET}:{PORTS}:{data1}:admin:1234:::\n")

                elif "incorrect password" in response.text:
                    print(f"FAILED: Zebra printer rejected default credentials (admin:1234)\n")
                    logFile.write(f"FAILED:1:Zebra default credentials failed:{TARGET}:{PORTS}:{data1}:::::\n")
                else:
                    print(f"WARNING: Unexpected response from Zebra printer at {TARGET}\n")
                    logFile.write(f"WARNING:1:Zebra default credential response unrecognized:{TARGET}:{PORTS}:{data1}:::::\n")
            else:
                print(f"FAILED: Zebra login endpoint returned status code {response.status_code}\n")
                logFile.write(f"FAILED:1:Zebra login request failed with status {response.status_code}:{TARGET}:{PORTS}:{data1}:::::\n")

    except Exception as e:
        print(f"FAILED: Could not complete Zebra default credential test on {TARGET}\nError: {str(e)}\n")
