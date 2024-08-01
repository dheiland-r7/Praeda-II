# Xerox check device to see if Remote Control is enabled for unauthenticated users 
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Xerox models
#      VersaLink C7020,C7025,C7130,B7030,B7125
#
#
import requests
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def MP0003(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Set global variables
    count = 1
    OID = '1.3.6.1.4.1.253.8.53.13.2.1.6.1.180.200'
    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            result = query_snmp(TARGET, OID)
            if result is not None:
                if result == 0:
                    print("FAILED: Unauthenticated Remote Control is Disabled")
                    logFile.write(f"FAILED:0:Unauthenticated Remote Control:{TARGET}:{PORTS}:{data1}xxx::::Disabled:\n")
                elif result == 3:
                    print("\033[91mSUCCESS\033[0m: Unauthenticated Remote Control is ENABLED")
                    logFile.write(f"\033[91mSUCCESS\033[0m:0:Unauthenticated Remote Control:{TARGET}:{PORTS}:{data1}xxx::::ENABLED:\n")
                else:
                    print("Status of Remote Control is Unknown")
            else:
                print("Couldn't get a read on Remote Control state.")            
    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")
# ----------------------------sub routine------------------------
def query_snmp(TARGET, OID):
   iterator = getCmd(
      SnmpEngine(),
      CommunityData('public', mpModel=0),
      UdpTransportTarget((TARGET, 161)),
      ContextData(),
      ObjectType(ObjectIdentity(OID))
   )

   errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

   if errorIndication:
       print(f"Error: {errorIndication}")
   elif errorStatus:
       print(f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
   else:
       for varBind in varBinds:
           return varBind[1]
   return None

#---------------------------------------------------


