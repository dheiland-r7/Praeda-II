# RICOH authenticated address book retrieval (uses default creds) 
######################################################
#                 PRAEDA II Module #MP0012           #
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
# from pysnmp.hlapi import get_cmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity


def MP0012(target, ports, web, output, logfile, data1):
	try:
		with open(f'{output}/{logfile}.log', 'a') as logFile:

        #URL for address book
			url = f"http{web}://{target}:{ports}/web/entry/en/address/adrsList.cgi"

        #Set Up Cookie For App Interaction
			cookies = {'risessionid': '192514866108490', 'cookieOnOffChecker': 'on', 'wimsesid': '--',}

        #HTTP(S) request to check access
			response = requests.get(url,cookies=cookies,verify=False)

		#Review Results
			#print('Status Code:')
			#print(response.status_code)
			#print('Content:')
			#print(response.content)

		#Check If Address Book Accessible
			if response.status_code == 200 and "Address List" in str(response.content):
				print("\033[91mSUCCESS\033[0m: The RICOH device Address Book is accessible.\n")
			elif response.status_code == 200 and "form1" in str(response.content):
				print("\033[91mFAIL\033[0m: The RICOH device Address Book appears to be behind a login portal.\n")
				#if :
				#print("Code for Trying if Admin Login default already discovered...")

	except Exception as e:
		print(f"An error occurred: {str(e)}")


