# RICOH FTP anonymous access check module 
######################################################
#                 PRAEDA II Module #MP0013           #
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
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64
from pysnmp.hlapi import getCmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity


def MP0013(target, ports, web, output, logfile, data1):
	ftp_port = check_server(target)

	if "Connected" in str(ftp_port):
		try:
			filename = "prnlog-" + target
			urllib.request.urlretrieve('ftp://192.168.1.185/prnlog', filename)
			print("\033[91mSUCCESS\033[0m: The RICOH device allows anonymous access to FTP. Downloading prnlog as " + filename + ". Likely contains usernames.\n")
		except:
			print("\033[91mSUCCESS\033[0m: The RICOH device does not appear to allow anonymous access to FTP.\n")
	else:
		print("\033[91mFAIL\033[0m: The RICOH device does not have FTP open.\n")

#PYTHON SOCKET CHECK
def check_server(address):
	#check TCP socket
    port = 21
    # Create a TCP socket
    #timeout = 40 #timeout in seconds
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
