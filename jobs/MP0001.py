# Xerox default password validation check module 
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Xerox models
#      VersaLink C7020,C7025,C7130,B7030,B7125
#
#
#
#
import requests
import base64
from pysnmp.hlapi import getCmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def MP0001(target, ports, web, output, logfile, data1):
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            # First test with common default xerox password "1111"
            if try_login(target, ports, web, "YWRtaW4=", encode_password("1111"), output, logfile):
                print("\033[91mSUCCESS\033[0m: The Xerox devices Admin password is 1111\n")
                logFile.write(f"\033[91mSUCCESS\033[0m:1:Xerox Device credential:{target}:{ports}:{data1}xxx:Admin:1111:::\n")
            else:
                # If password 1111 attempt fails, retrieve the serial number and try that
                serial = get_serial_via_snmp(target)
                if serial:
                    serial_base64 = encode_password(serial)
                    if try_login(target, ports, web, "YWRtaW4=", serial_base64, output, logfile):
                        print(f"\033[91mSUCCESS\033[0m: The Xerox device's Admin password is the serial number {serial}\n")
                        logFile.write(f"\033[91mSUCCESS\033[0m:1:Xerox Device credential:{target}:{ports}:{data1}xxx:Admin:{serial}:::\n")
                    else:
                        print("FAIL: Neither default password nor serial number worked.\n")
                        logFile.write(f"FAIL:1:Xerox device's admin password could not be determined:{target}:{ports}:{data1}xxx:Admin:?:::\n")
                else:
                    print("FAIL: Could not retrieve serial number via SNMP.\n")
                    logFile.write(f"FAIL:1:Could not retrieve serial number via SNMP:{target}:{ports}:{data1}xxx:::::\n")
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")


def encode_password(password):
    return base64.b64encode(password.encode()).decode()

def try_login(target, ports, web, username, password_base64, output, logfile):
    url = f"http{web}://{target}:{ports}/LOGIN.cmd?NAME={username}&PSW={password_base64}"
    expected_response = {
        "result": "0",
        "errorCode": "0",
        "koDefault": "0",
        "snmpDefault": "0",
        "globalIP": "0",
        "passwordChangeRequired": "0"
    }
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200 and response.json() == expected_response:
            return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return False

def get_serial_via_snmp(target):
    # SNMP call to retrieve device serial to be tested as password
    for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((target, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.43.5.1.1.17.1'))
    ):
        if errorIndication:
            print(errorIndication)
            return None
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            return None
        else:
            for varBind in varBinds:
                return varBind[1].prettyPrint()
