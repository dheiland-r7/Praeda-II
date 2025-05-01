# Konica default password validation check module 
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
from bs4 import BeautifulSoup
from pysnmp.hlapi import getCmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def MP0004(target, ports, web, output, logfile, data1):
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:

            # URL and data for the login  request
            initial_url = f"http{web}://{target}:{ports}/wcd/login.cgi?func=PSL_LP1_LOG&password=12345678&R_ADM=AdminAdmin"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Connection": "close"
            }



            # Sending the intial POST request
            try:

           # session = requests.Session()  # Using session to maintain cookies
                session = requests.Session()

                response = session.get(initial_url, headers=headers, verify=False)
                print("request response status code", response.status_code)
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                exit()

            # Checking the response for specific content indecating valid password
            if 'document.cookie="adm=AS_COU"' in response.text:
                print("\033[91mSUCCESS\033[0m: The Konica devices Admin password is 12345678\n")
                logFile.write(f"\033[91mSUCCESS\033[0m:1:Konica Device credential:{target}:{ports}:{data1}:AdminAdmin:12345678:::")



# Force logout after varifying the default password. This is required to allow furture authentication without timeout

            # Parsing HTML to find the h_token value
                soup = BeautifulSoup(response.text, 'html.parser')
                h_token_input = soup.find('input', {'id': 'h_token'})
                h_token_value = h_token_input['value'] if h_token_input else ''

            # Manually extract the "ID" cookie value
                # cookies = response.cookies.get_dict()
                # id_cookie = cookies.get('ID', '')  # Replace 'ID' with the correct cookie name if different

                # Constructing logout request with token data
                new_url = f"http{web}://{target}:{ports}/wcd/a_user.cgi?func=PSL_ACO_LGO&h_token={h_token_value}"

                # Manually setting the cookie for the next request
                # cookie_header = {'Cookie': f'ID={id_cookie}'}

                # Setup request to logout using session cookie and Token and send get request to attempt logout

                try:
                    #new_response = session.get(new_url, headers=cookie_header, verify=False)
                    new_response = session.get(new_url, headers=headers, verify=False)
                    # print("returned status code", new_response.status_code)
                    # print(f"Token={h_token_value} and cookie={id_cookie}")
                    # print(f"Token={h_token_value}")

                # Validate new_response was successful and if 404 error generate next_response to use HTTPS to logout
                # this is needed if the Konica is configured to force SSL for admin user. So when http request to login
                # with default creds succeed the logout attempt will only work over https
                
                    if new_response.status_code == 404:
                        # If 404, ensure URL is HTTPS and resend the request
                        # print("Received 404, switching POST request to HTTPS.")
                        next_url = f"https://{target}/wcd/a_user.cgi?func=PSL_ACO_LGO&h_token={h_token_value}"
                        # print("DEBUG1")
                        next_response = session.get(next_url, headers=headers, verify=False)
                        # print("Looks like it should have worked to log user outs")
                        # print("Request completed with status code:", next_response.status_code)
                    # elif new_response.status_code == 301:
                        # print("Received 301, note sure whats going on.")
                    # elif new_response.status_code == 302:
                        # print("Received 302, what the crap does this meen.")
                        
                except requests.exceptions.RequestException as e:
                    print(f"Error making the logout request: {e}")

            elif "<Item Code=\"Err_2\">AdminAnotherLoginError</Item>" in response.text:
                print("Admin is currently logged in on this Konica device  please retest at a later time.\n")
            elif "<Item Code=\"Err_2\">CommonLoginError</Item>" in response.text:
                print("FAIL: The Admin password has been changed on this Konica device.\n")
                logFile.write(f"FAIL:1:Konica device's admin password could not be determined:{target}:{ports}:{data1}:AdminAdmin:?:::")
            else:
                print("The response does not contain expected data.")

    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")

