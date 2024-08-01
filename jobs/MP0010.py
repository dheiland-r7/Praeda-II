# Sharp default password validation check module 
######################################################
#                 PRAEDA II Module #MP0010           #
#                  Copyright (C) 2024                #
#              Deral 'percent_x' Heiland             #
#                     Austin Guidry                  #
######################################################

###############################################
#   This module still need further testing    #
###############################################

import requests
from bs4 import BeautifulSoup

def MP0010(target, ports, web, output, logfile, data1):
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            mfpsessionid = get_mfpsessionid(target, ports, web)
            if not mfpsessionid:
                log_and_print_failure(logFile, target, ports, data1, "Could not retrieve MFPSESSIONID")
                return

            token2 = get_token2(target, ports, web, mfpsessionid)
            if not token2:
                log_and_print_failure(logFile, target, ports, data1, "Could not retrieve Token2")
                return

            if test_default_password(target, ports, web, mfpsessionid, token2):
                log_and_print_success(logFile, target, ports, data1, "admin")
            else:
                log_and_print_failure(logFile, target, ports, data1, "Admin password is not default")
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")

def get_mfpsessionid(target, ports, web):
    url = f"http{web}://{target}:{ports}/login.html?/nw_quick.html"
    headers = create_headers()
    #print(f"Sending GET request to {url}")
    try:
        response = requests.get(url, headers=headers, verify=False)
        #print(f"Response Status Code: {response.status_code}")
        if 'Set-Cookie' in response.headers:
            cookies = response.headers['Set-Cookie']
            #print(f"Received cookies: {cookies}")
            mfpsessionid = cookies.split(';')[0].split('=')[1]
            #print(f"Extracted MFPSESSIONID: {mfpsessionid}")
            return mfpsessionid
    except Exception as e:
        print(f"An error occurred while retrieving MFPSESSIONID: {str(e)}")
    return None

def get_token2(target, ports, web, mfpsessionid):
    url = f"http{web}://{target}:{ports}/login.html?/nw_quick.html"
    headers = create_headers(mfpsessionid)
    #print(f"Sending GET request to {url} with MFPSESSIONID: {mfpsessionid}")
    try:
        response = requests.get(url, headers=headers, verify=False)
        #print(f"Response Status Code: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        token2 = soup.find('input', {'name': 'token2'})['value']
        #print(f"Extracted token2: {token2}")
        return token2
    except Exception as e:
        print(f"An error occurred while retrieving Token2: {str(e)}")
    return None

def test_default_password(target, ports, web, mfpsessionid, token2):
    url = f"http{web}://{target}:{ports}/login.html?/nw_quick.html"
    headers = create_headers(mfpsessionid)
    headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': f"http{web}://{target}:{ports}",
        'Referer': f"http{web}://{target}:{ports}/login.html?/nw_quick.html"
    })
    
    payload = {
        'ggt_select(10009)': '3',
        'ggt_textbox(10003)': 'admin',
        'action': 'loginbtn',
        'token2': token2,
        'ordinate': '0',
        'ggt_hidden(10008)': '5'
    }
    
    print(f"Sending POST request to {url} with payload: {payload} and MFPSESSIONID: {mfpsessionid}")
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else ""
        #print(f"Page Title: {title}")
        if "Quick Settings" in title:
            print("Login successful, authenticated access to settings are available")
            return True  # Admin password is default
        else:
            print("Login failed, authenticated access to setting unavailable")
    except Exception as e:
        print(f"An error occurred during login attempt: {str(e)}")
    return False

def create_headers(mfpsessionid=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1'
    }
    if mfpsessionid:
        headers['Cookie'] = f'MFPSESSIONID={mfpsessionid}; sideBarflag=1'
    return headers

def log_and_print_success(logFile, target, ports, data1, password):
    message = f"\033[91mSUCCESS\033[0m: The MFP device's Adminitrator password is {password}\n"
    print(message)
    logFile.write(f"\033[91mSUCCESS\033[0m:1:MFP Device credential:{target}:{ports}:{data1}:Administrator:{password}:::\n")

def log_and_print_failure(logFile, target, ports, data1, reason):
    message = f"FAIL: {reason}\n"
    print(message)
    logFile.write(f"FAIL:1:{reason}:{target}:{ports}:{data1}:::::\n")
