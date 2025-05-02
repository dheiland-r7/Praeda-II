# Konica test to see if SMB & FTP Scan mode is configured via /wcd/abbr.xml
######################################################
#                 PRAEDA II Module #MP0019           #
#                  Copyright (C) 2025                #
#              Deral 'percent_x' Heiland             #
######################################################
# This module will work on Konica printers exposing
# /wcd/abbr.xml and using SMB scan destinations.
#
#
import requests
import xml.etree.ElementTree as ET

def MP0019(target, ports, web, output, logfile, data1):

    # Create a session object
    session = requests.Session()

    # URL for the initial connection to get the session cookie
    initial_url = f"http{web}://{target}:{ports}/wcd/index.html"
    xml_url = f"http{web}://{target}:{ports}/wcd/abbr.xml"

    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:

            # Make an initial request to establish the session and get the cookie
            initial_response = session.get(initial_url, verify=False)
            initial_response.raise_for_status()

            xml_response = session.get(xml_url, verify=False)
            xml_response.raise_for_status()

            if xml_response.headers['Content-Type'].lower().startswith('application/xml') or xml_response.headers['Content-Type'].lower().startswith('text/xml'):

                # Remove BOM if present
                content = xml_response.content.lstrip(b'\xef\xbb\xbf')

                # Parse the XML from the response
                root = ET.fromstring(content)

                # Find all <SendMode> elements
                sendmode_elements = root.findall('.//SendMode')

                found_smb = False
                for elem in sendmode_elements:
                    if elem.text and elem.text.strip().lower() == "smb":
                        found_smb = True
                        print(f"\033[91mSUCCESS\033[0m: SMB Scan is enabled in Konica Address book")
                        logFile.write(f"\033[91mSUCCESS\033[0m:2:SMB Scan is enabled in Konica Address book:{target}:{ports}:{data1}::::konica_minolta_pwd_extract\n")
                        break

                if not found_smb:
                    print("No SMB scan settings found.")
                found_ftp = False
                for elem in sendmode_elements:
                    if elem.text and elem.text.strip().lower() == "ftp":
                        found_ftp = True
                        print(f"\033[91mSUCCESS\033[0m: FTP Scan is enabled in Konica Address book")
                        logFile.write(f"\033[91mSUCCESS\033[0m:2:FTP Scan is enabled in Konica Address book:{target}:{ports}:{data1}::::konica_minolta_pwd_extract\n")
                        break

                if not found_ftp:
                    print("No FTP scan settings found.")

            else:
                print("Received non-XML content at /wcd/abbr.xml.")

    except Exception as e:
        print(f"Failed to make connection to URL \nError: {str(e)}")

