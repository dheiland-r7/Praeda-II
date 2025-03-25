# HP consumer grade printer finger print validation  
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will print results for positive fingerprints 
#
#
from pysnmp.hlapi import SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, CommunityData, getCmd
import re

# Function to extract the device model from SNMP response data
def extract_device_model(snmp_data):
    match = re.search(r'MDL:([^;]+)', snmp_data)
    if match:
        return match.group(1)  # Return the model string
    return "Unknown Model"

# Function to perform SNMP GET request using pysnmp 4.4.12 synchronous API
def get_device_model_snmp(target, community, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((target, 161)),  # Use default SNMP port 161
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    ))

    # Handle SNMP errors
    if errorIndication:
        print(f"Error: {errorIndication}")
        return None
    elif errorStatus:
        print(f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
        return None
    else:
        for varBind in varBinds:
            return str(varBind[1])  # Return the SNMP response data

# Function that runs the SNMP check and logs the result
def MPHP(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # OID for device model
    device_model_oid = '1.3.6.1.4.1.11.2.3.9.1.1.7.0'
    community = 'public'  # Assuming 'public' as the community string, modify if needed

    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            # Perform the SNMP GET request
            snmp_data = get_device_model_snmp(TARGET, community, device_model_oid)
            
            if snmp_data:
                # Extract the model from SNMP data
                device_model = extract_device_model(snmp_data)
                # logFile.write(f"Device validated on network with Finger Print of {device_model}\n")
                logFile.write(f"\033[93mIDENTIFIED\033[0m:5:Finger Printed:{TARGET}:{PORTS}:{device_model}:::::\n")
                print(f"MFP device validated on network with Finger Print of {device_model}\n")
            else:
                logFile.write("Failed to retrieve SNMP data.\n")
                print("Failed to retrieve SNMP data.\n")

    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")

