# Konica test to see if LDAP is enabled and configured 
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Konica models
#
#
#
import requests
import xml.etree.ElementTree as ET

def MP0005(target, ports, web, output, logfile, data1):

    # Create a session object
    session = requests.Session()

    # URL for the initial connection to get the session cookie
    initial_url = f"http{web}://{target}:{ports}/wcd/index.html"


    xml_url = f"http{web}://{target}:{ports}/wcd/system_network.xml"
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            
        # Make an initial request to establish the session and get the cookie
            initial_response = session.get(initial_url, verify=False)
            initial_response.raise_for_status()

            # TEMP - Print out the session cookies
            # print("Session Cookies:")
            # for cookie in session.cookies:
                #print(f"{cookie.name}: {cookie.value}")

            xml_response = session.get(xml_url, verify=False)
            xml_response.raise_for_status() 

            if xml_response.headers['Content-Type'].lower().startswith('application/xml') or xml_response.headers['Content-Type'].lower().startswith('text/xml'):

            # Remove BOM if present
                content = xml_response.content.lstrip(b'\xef\xbb\xbf')
                # print(content[:100])

            # Parse the XML from the response
                root = ET.fromstring(content)

            # Find the <Ldap> element
                ldap_element = root.find('.//Ldap')
                #ldap_xml_str = ET.tostring(ldap_element, encoding='unicode')
                #print(ldap_xml_str)
            
                if ldap_element is not None:
                    enable_element = ldap_element.find('.//Enable')
                    server_address_element = ldap_element.find('.//ServerAddress')
                    server_auth_element = ldap_element.find('.//ServerAuthenticationMethod')
                    user_name_element = ldap_element.find('.//User')
                    auth_method_element = ldap_element.find('.//AuthenticationMethod')

                # Check if <Enable> is "true" and <ServerAddress> is not "0.0.0.0"
                if enable_element is not None and server_address_element is not None:
                    if enable_element.text == "true" and server_address_element.text != "0.0.0.0":
                        print(f"\033[91mSUCCESS\033[0m: The LDAP service is enabled : Server IP:{server_address_element.text} User Name:{user_name_element.text} Server Auth:{server_auth_element.text} Authentication Method:{auth_method_element.text}")
                        logFile.write(f"\033[91mSUCCESS\033[0m:2:The LDAP service is enabled:{target}:{ports}:{data1}:{user_name_element.text}:{server_auth_element.text}:{auth_method_element.text}::")
                    else:
                        print("LDAP is either not enabled or has an invalid server address.")
                else:
                    print("Required elements not found in the XML.")
            else:
                print("<Ldap> element not found in the XML.")

    except Exception as e:
        # print(f"Failed to open output file {output}\nError: {str(e)}")
        print(f"Failed to make connection to URL \nError: {str(e)}")

