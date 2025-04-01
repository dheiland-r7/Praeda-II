#!/usr/bin/env python3
#
#  _____                    _         _____ _____ 
# |  __ \                  | |       |_   _|_   _|
# | |__) | __ __ _  ___  __| | __ _    | |   | |  
# |  ___/ '__/ _` |/ _ \/ _` |/ _` |   | |   | |  
# | |   | | | (_| |  __/ (_| | (_| |  _| |_ _| |_ 
# |_|   |_|  \__,_|\___|\__,_|\__,_| |_____|_____|
#                                                 
#   Deral (Percent_x) Heiland - Rapid7 
#   Copywrite 2023, 2024
#   PRAEDA II version 1.25b 
###################################################


import sys
import os
import re
import socket
import time
import subprocess
from bs4 import BeautifulSoup
# from pysnmp.entity.rfc3413.oneliner import cmdgen  THIS IS BEING REMOVED
from pysnmp.hlapi import *
from netaddr import IPNetwork, IPAddress
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import requests
from requests.exceptions import RequestException
from pysnmp.hlapi import *
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import ssl

# Suppress SSL/TLS warnings
urllib3.disable_warnings(InsecureRequestWarning)

# Set Constants
SOCKET_IS_UP = 0
SOCKET_IS_DOWN = 1
SOCKET_IS_IGNORED = 2
REQUEST_TIMEOUT = 4
WAIT_FOR_RST = 1

# Set Variables
dirpath = "."
DataEntry = ""
number = ""
title = ""
server = ""
job = "job"
web = ""
data3 = "Q"

# Set Options
options = {
    "g": "",
    "n": "",
    "t": "",
    "p": "",
    "j": "",
    "l": "",
    "s": "",
    "i": "",
    "r": "",
}

# Parse Command Line Arguments
args = sys.argv[1:]
i = 0
while i < len(args):
    arg = args[i]
    if arg.startswith('-'):
        if i + 1 < len(args) and not args[i + 1].startswith('-'):
            options[arg[1:]] = args[i + 1]
            i += 1
        else:
            options[arg[1:]] = ""
    i += 1

# Validate Command Line Arguments
if (options["g"] and (options["t"] or options["p"])) or (options["g"] and (options["n"] or options["p"])) or (
        options["g"] and options["n"]):
    print("Error block 1")
    print("-g and -t or -p options are not allowed at the same time")
    print("The correct options syntax are:")
    print("For GNMAP input:  Praeda.py -g GNMAP_FILE -i IGNORE_PORTS -j PROJECT_NAME -l OUTPUT_LOG_FILE")
    print("For target input: Praeda.py -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
    print("For CIDR input:   Praeda.py -n CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
    print("To resume a prevous job:  praeda.py -r true -j PROJECT_NAME -l OUTUT_LOG_FILE -s SSL")
    sys.exit(1)
elif options["g"] and (not options["j"] or not options["l"]):
    print("Error block 2")
    print("Options -j and -l are both required when using option -g")
    print("The correct options syntax for using gnmap as input is:")
    print("praeda.py -g GNMAP_FILE -i IGNORE_PORTS -j PROJECT_NAME -l OUTPUT_LOG_FILE")
    sys.exit(1)
elif options["n"] and (options["i"]):
    print("Error block 3")
    print("Option -i can only be used with -g")
    print("The correct options syntax for using network CIDR or CIDR list file as input is:")
    print("For CIDR input: praeda.py -n CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
elif options["t"] and (options["i"]):
    print("Error block 4")
    print("Option -i can only be used with -g")
    print("The correct options syntax for using target ip list file as input is:")
    print("praeda.py -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
elif options["n"] and (not options["p"] or not options["j"] or not options["l"]):
    print("Error block 5")
    print("Options -p, -j, and -l are all required when using option -n")
    print("The correct options syntax for using network CIDR or CIDR list file as input is:")
    print("For CIDR input: praeda.py -n CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
    sys.exit(1)
elif options["t"] and (not options["p"] or not options["j"] or not options["l"]):
    print("Error block 6")
    print("Options -p, -j, and -l are all required when using option -t")
    print("The correct options syntax for using target ip list file as input is:")
    print("praeda.py -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
    sys.exit(1)
elif (options["r"] and (options["t"] or options["g"] or options["n"])) or (options["r"] and not options["j"] and not options["l"]):
    print("Error block 7")
    print("Option -r should only be used to resume an incomplete scan.")
    print("The only options appropriate for use with -r are -j, -l and -s. (-s is optional)")
    print("To resume an unfinished session:  praeda.py -r true -j PROJECT_NAME -l TARGET_FILE -s SSL")
    print("PROJECT_NAME must match the project name used in the original scan. TARGET_FILE should match")
    print("the name of the output file requested during the original job run.")
    sys.exit(1)
elif not options["g"] and not options["t"] and not options["n"] and not options["r"]:
    print("Error block 8")
    print("Required options are missing")
    print("The correct options syntax are:")
    print("For GNMAP input:  praeda.py -g GNMAP_FILE -i IGNORE_PORTS -j PROJECT_NAME -l OUTPUT_LOG_FILE")
    print("For target input: praeda.py -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
    print("For CIDR input:   praeda.py -n CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL")
    print("To resume a prevous job:  praeda.py -r true -j PROJECT_NAME -l OUTUT_LOG_FILE -s SSL")
    sys.exit(1)

# Read Data File
data_file = os.path.join(dirpath, "data", "data_list")
with open(data_file, 'r') as f:
    raw_data = f.read().splitlines()

# Enable SSL
if options["s"].lower() == "ssl":
    web = 's'

# Set Ignore Invalid Certs
os.environ['PERL_LWP_SSL_VERIFY_HOSTNAME'] = '0'

# Create Project Folder
if not os.path.exists(options["j"]):
    os.mkdir(options["j"])

#-----------------------------------------------subroutines------------------------------------------------------#

# Check if port is open and contains http
def check_port(target, ports, ignore_ports=""):
    status = SOCKET_IS_DOWN
    if ports in ignore_ports:
        return SOCKET_IS_IGNORED
    else:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock.setdefaulttimeout(0)
            sock.settimeout(REQUEST_TIMEOUT)
            sock.connect((target, int(ports)))
            status = SOCKET_IS_UP
            sock.close()
        except Exception:
            pass
    return status


# gnmap parsing routine
def gnmap_parse(GNMAPFILE, OUTPUT):
    try:
        current_host = None
        with open(GNMAPFILE, 'r') as myinputfile:
            with open(f'{OUTPUT}/targetdata.txt', 'w') as outfile:
                for line in myinputfile:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if 'Host:' in parts:
                        current_host = parts[1]  # Get the IP address

                    if 'Ports:' in parts:
                        ports_info = line.split('Ports:')[1].split(',')
                        for port_info in ports_info:
                            port_info_parts = port_info.strip().split('/')
                            if len(port_info_parts) >= 5 and 'open' in port_info_parts:
                                port = port_info_parts[0].strip()  # Remove any leading/trailing whitespace
                                protocol = port_info_parts[4].strip()
                                if 'http' in protocol:  # Check if "http" is present (case-insensitive)
                                    outfile.write(f"{current_host}:{port}:{protocol}\n")
                                else:
                                    smile = "Its a Beautiful Day"

    except Exception as e:
        print(f"Error: {str(e)}")
    return


# cidr input parse routine
def cidr_parse(CIDRFIL, OUTPUT):
    targetdata_file = f'{OUTPUT}/targetdata.txt'
    try:
        if os.path.exists(targetdata_file):
           os.remove(targetdata_file)

        with open(targetdata_file, 'a') as outfile:
            if os.path.exists(CIDRFIL):
                with open(CIDRFIL, 'r') as hand:
                    cidr_list = hand.readlines()
                    for cidr in cidr_list:
                        cidr = cidr.strip()
                        ip_network = IPNetwork(cidr)
                        for ip in ip_network:
                            outfile.write(f"{ip}:{TCP_PORT}\n")  # Replace PORTS with the desired port value
            else:
                cidr = CIDRFIL
                ip_network = IPNetwork(cidr)
                for ip in ip_network:
                    outfile.write(f"{ip}:{TCP_PORT}\n")  # Replace PORTS with the desired port value
 
    except Exception as e:
        print(f"Error: {str(e)}")
    return

def parse_output_files(project_folder, output_file):
    if (os.path.exists("./" + project_folder + "/" + output_file + "-WebHost.txt") and os.path.exists("./" + project_folder + "/targetdata.txt")):
        print("Files exist! Resuming session.")
        with open("./" + project_folder + "/" + output_file + "-WebHost.txt") as f:
            allDoneTargets = f.readlines()
            lastTargetFields = allDoneTargets[len(allDoneTargets) - 1].split(':')
            lastTarget = lastTargetFields[0] + ":" + lastTargetFields[1]
            print(lastTarget)
            with open("./" + project_folder + "/targetdata.txt") as t:
                allTargets = t.readlines()
                for line in allTargets:
                    if lastTarget in line:
                        lastTarget = allTargets.index(line)
                        break
#            lastTarget = allTargets[lastTargetIndex]
            print(lastTarget)
        return lastTarget
    else:
        print("Error! Can't resume. Necessary files don't exist.")
    sys.exit(1)

# snmp device identifier routine
def snmp_get(target):
    # Create an SNMP GET request
    error_indication, error_status, error_index, var_binds = next(
        getCmd(
            SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget((target, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
        )
    )

    # Check for SNMP errors
    if error_indication:
        return "N/A"
    else:
        # Extract the value of the sysDescr OID
        sys_descr_value = var_binds[0][1].prettyPrint()
        return sys_descr_value

# Create a custom adapter to set the SECLEVEL
class SSLAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        # Create a default SSL context
        self.ssl_context = ssl.create_default_context()
        # Set the ciphers to lower SECLEVEL
        self.ssl_context.set_ciphers('DEFAULT:@SECLEVEL=1')
        # Disable hostname checking to handle CERT_NONE
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


#--------------------------------------------END--Subroutines---------------------------------------------------#

IGNORE_PORTS = ""
# GNMAP Parse options routine call
if options["g"]:
    GNMAPFILE = options["g"]
    IGNORE_PORTS = options["i"].strip().split(',')
    OUTPUT = options["j"]
    NAME = options["l"]
    gnmap_parse(GNMAPFILE, OUTPUT)

# CIDR Parse options routin call
if options["n"]:
    CIDRFIL = options["n"]
    OUTPUT = options["j"]
    NAME = options["l"]
    TCP_PORT = options["p"]
    cidr_parse(CIDRFIL, OUTPUT)

# IP file list options routin call 
if options["t"]:
    FILE = options["t"]
    PORTS = options["p"]
elif options["n"]:
    FILE = os.path.join(options["j"], "targetdata.txt")
    PORTS = options["p"]
else:
    FILE = os.path.join(options["j"], "targetdata.txt")

NEXT_TARGET = 0

# Resume option. Parse output files from previous run and pick up where you left off
if options["r"]:
    PROJECT_FOLDER = options["j"]
    NAME = options["l"]
    LAST_TARGET = parse_output_files(PROJECT_FOLDER, NAME)
    NEXT_TARGET = LAST_TARGET + 1


OUTPUT = options["j"]
LOGFILE = options["l"] 

# Read Target Input
with open(FILE, 'r') as f:
    fileTargets = f.read().splitlines()
    targets = fileTargets[NEXT_TARGET:len(fileTargets)]

for TARGET in targets:
    if options["g"]:
        TARGET, PORTS, N = TARGET.split(':')
        if "https" in N.lower() or "ssl" in N.lower():
            web = "s"
        else:
            web = ""
    elif options["n"]:
        #TARGET = TARGET.strip()
        TARGET, PORTS = TARGET.split(':')
    elif options["r"]:
        IGNORE_PORTS = options["i"].strip().split(',')
        if (len(TARGET.split(':')) == 3):
            TARGET, PORTS, N = TARGET.split(':')
        else:
            TARGET, PORTS = TARGET.split(':')
    
# Call Port Check Routine
    if options["i"]:
        status = check_port(TARGET, PORTS, IGNORE_PORTS)
    else:
        status = check_port(TARGET, PORTS)
    
    if status == SOCKET_IS_DOWN:
        print(f"{TARGET}:{PORTS}:NO ANSWER RETURNED")
    elif status == SOCKET_IS_IGNORED:
        print(f"{TARGET}:{PORTS}:IGNORED BY REQUEST")


# Perform HTTP request to gather title/server data and call SNMP routin for gather SNMP device name data
    else:
        try:
            # Create a session and attach the custom SSL adapter
            session = requests.Session()
            session.mount('https://', SSLAdapter())
            session.mount('http://', SSLAdapter())
        # Make an HTTP request
            url = f"http{web}://{TARGET}:{PORTS}/"  
            #response = requests.get(url, verify=False)  # `verify=False` skips SSL certificate verification. 
            response = session.get(url, verify=False, timeout=(REQUEST_TIMEOUT))  # `verify=False` skips SSL certificate verification. 

        # Check if the request was successful
            if response.status_code == 200:
            # Extract data from the HTTP response
                d1 = response.headers.get("Title", "")
                d1 = d1.replace(":", ";")
                d2 = response.headers.get("Server", "")
                d2 = d2.replace(":", ";")
            # call snmp routine for target data
                d3 = snmp_get(TARGET)
                d3 = d3.replace(":", ";")

            # print to screen targeted device inforation
                print(f"{TARGET}:{PORTS}:{d1}:{d2}:{d3}")

                with open(f"{OUTPUT}/{LOGFILE}-WebHost.txt", 'a') as webFile:
                    webFile.write(f"{TARGET}:{PORTS}:{d1}:{d2}:{d3}\n")

                for DataEntry in raw_data:
                    values = DataEntry.split('|')
                    data = values[0]
                    data1 = values[1]
                    data2 = values[2]
                    #if (data1.lower() in data.lower() and data2.lower() in d3.lower()) or (
                    #         #"SNMP" in data2 and data1.lower() in d3.lower()):
                    #         "SNMP" in data2 and data1.lower() in d3.lower()):
                    if ("HEADER" in data2 and data1.lower() in d2.lower()) or (
                             "SNMP" in data2 and data1.lower() in d3.lower()) or (
                             "SERVER" in data2 and data1.lower() in d2.lower()):

                        num = len(values)
                        for i in range(3, num):
                            if values[i] != '':
                                with open(f"{OUTPUT}/{LOGFILE}.log", 'a') as logFile:
                                    logFile.write(f"\n{TARGET}:{PORTS}:{data1}:{data2}:\n")
                                job = values[i]
                                module = __import__(f'jobs.{job}', fromlist=[job])
                                job_func = getattr(module, job)
                                result = job_func(TARGET, PORTS, web, OUTPUT, LOGFILE, data1)

            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
        except RequestException as e:
            # Handles any request-related errors
                print(f"An error occurred while trying to retrieve data from {url}: {e}")
        except Exception as e:
            # A catch-all for any other errors that were not anticipated
                print(f"An unexpected error occurred: {e}")


#-----------------------------------------------END OF ALL------------------------------------------------------#
