# RICOH rsh anonymous access check module 
######################################################
#                 PRAEDA II Module #MP0014           #
#                  Copyright (C) 2024                #
#                Sam 'C7berC0wb0y' Moses             #
######################################################
# this module has been tested on the following RICOH models:
#      RICOH IM C4500
#
#
#
#
import urllib.request
import socket
import requests
import subprocess
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64
from pysnmp.hlapi import getCmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity


def MP0014(target, ports, web, output, logfile, data1):
    rsh_port = check_server(target)

    if "Connected" in str(rsh_port):
        filename = "rsh-prnlog-" + target
        command = "rsh " + target + " prnlog"
        output = subprocess.check_output(command,shell=True)
        if "User" in str(output):
            print("\033[91mSUCCESS\033[0m: The RICOH device allows anonymous access to RSH port 514. Running prnlog will likely obtain usernames.\n")
            #print(output.decode())
        else:
            print("\033[91mFAIL\033[0m: The RICOH device doesn't allow anonymous access to RSH port 514.\n")
    else:
        print("\033[91mFAIL\033[0m: The RICOH device does not appear to have RSH open.\n")


#PYTHON SOCKET CHECK
def check_server(address):
    #check TCP socket
    port = 514
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.settimeout(timeout)
    #print ("Attempting to connect to %s on port %s" % (address, port))
    try:
        s.connect((address, port))
        #print ("Connected to %s on port %s" % (address, port))
        return "Connected to %s on port %s" % (address, port)
    except socket.error as error:
        #print ("Connection to %s on port %s failed: %s")
        return "Connection to %s on port %s failed: %s" % (address, port, error)
    finally:
        s.close()
