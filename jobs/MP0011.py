# RICOH default password validation check module 
######################################################
#                 PRAEDA II Module #MP0011           #
#                  Copyright (C) 2024                #
#                Sam 'C7berC0wb0y' Moses             #
######################################################
# this module has been tested on the following RICOH models:
#      RICOH IM C4500
#
#
#
#
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64
from pysnmp.hlapi import getCmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def MP0011(target, ports, web, output, logfile, data1):
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            # First test with common default RICOH password "[BLANK]"
            if try_login(target, ports, web, "YWRtaW4=", encode_password(""), output, logfile):
                print("\033[91mSUCCESS\033[0m: The RICOH devices admin password is [BLANK]\n")
                logFile.write(f"\033[91mSUCCESS\033[0m:1:RICOH Device credential:{target}:{ports}:{data1}xxx:admin:[BLANK]:::\n")
            else:
                #If the password is not blank, retrieve the serial number and attempt it
                serial = get_serial_via_snmp(target)
                if serial:
                    serial_base64 = encode_password(serial)
                    if try_login(target, ports, web, "YWRtaW4=", serial_base64, output, logfile):
                        print(f"\033[91mSUCCESS\033[0m: The RICOH device's admin password is the serial number {serial}\n")
                        logFile.write(f"\033[91mSUCCESS\033[0m:1:RICOH Device credential:{target}:{ports}:{data1}xxx:admin:{serial}:::\n")
                    else:
                        print("FAIL: Neither default password nor serial number worked.\n")
                        logFile.write(f"FAIL:1:RICOH device's admin password could not be determined:{target}:{ports}:{data1}xxx:admin:?:::\n")
                else:
                    print("FAIL: Could not retrieve serial number via SNMP.\n")
                    logFile.write(f"FAIL:1:Could not retrieve serial number via SNMP:{target}:{ports}:{data1}xxx:::::\n")
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")



def encode_password(password):
    #base64 encode password
    return base64.b64encode(password.encode()).decode()

def try_login(target, ports, web, username, password_base64, output, logfile):
    #attempt login 
    cookies = {'risessionid': '192514866108490', 'cookieOnOffChecker': 'on', 'wimsesid': '--',}
    data = {
    'wimToken': '9876543211',
    'userid_work': '',
    'userid': 'YWRtaW4=',
    'password_work': '',
    'password': '',
    'open': '',}
    data['password'] = password_base64
    try:
        response = requests.post(f"http{web}://{target}:{ports}/web/guest/en/websys/webArch/login.cgi",cookies=cookies,data=data,verify=False,)
        if response.status_code == 200 and "getEasySecurity.cgi" in str(response.content):
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




