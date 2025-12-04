# RICOH default password validation check module 
######################################################
#                 PRAEDA II Module #MP0011           #
#                  Copyright (C) 2024                #
#                Sam 'C7berC0wb0y' Moses             #
######################################################
# this module has been tested on the following RICOH models:
#      RICOH IM C4500
#
import asyncio
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64

# PySNMP 7.x asyncio HLAPI (PEP8 names)
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
)

# Printer-MIB::prtGeneralSerialNumber.1
SERIAL_OID = ObjectType(ObjectIdentity('1.3.6.1.2.1.43.5.1.1.17.1'))

def MP0011(target, ports, web, output, logfile, data1):
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            # First test with common default RICOH password "[BLANK]"
            if try_login(target, ports, web, "YWRtaW4=", encode_password(""), output, logfile):
                print("\033[91mSUCCESS\033[0m: The RICOH devices admin password is [BLANK]\n")
                logFile.write(f"\033[91mSUCCESS\033[0m:1:RICOH Device credential:{target}:{ports}:{data1}xxx:admin:[BLANK]:::\n")
            else:
                # If the password is not blank, retrieve the serial number and attempt it
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


def encode_password(password: str) -> str:
    # base64 encode password
    return base64.b64encode(password.encode()).decode()


def try_login(target, ports, web, username_b64, password_base64, output, logfile) -> bool:
    """
    username_b64 should already be base64 ('YWRtaW4=' for 'admin')
    """
    # attempt login 
    cookies = {
        'risessionid': '192514866108490',
        'cookieOnOffChecker': 'on',
        'wimsesid': '--',
    }
    data = {
        'wimToken': '9876543211',
        'userid_work': '',
        'userid': 'YWRtaW4=',
        'password_work': '',
        'password': '',
        'open': '',
    }
    data['password'] = password_base64
    try:
        response = requests.post(
            f"http{web}://{target}:{ports}/web/guest/en/websys/webArch/login.cgi",
            cookies=cookies,
            data=data,
            verify=False,
            timeout=4
        )
        if response.status_code == 200 and "getEasySecurity.cgi" in str(response.content):
            return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return False


# -------------------- SNMP helpers (PySNMP 7.x async; community='public') --------------------

async def _snmp_get_serial_once(target: str, mp_model: int, timeout: float = 2.0, retries: int = 1) -> str | None:
    """
    Single SNMP GET for prtGeneralSerialNumber.1 using PySNMP 7.x asyncio HLAPI.
    mp_model: 1=v2c, 0=v1
    Returns serial string on success, or None on failure.
    """
    try:
        eng = SnmpEngine()
        # IMPORTANT: async transport factory is required in pysnmp 7.x
        transport = await UdpTransportTarget.create((target, 161), timeout=timeout, retries=retries)
        iterator = get_cmd(
            eng,
            CommunityData('public', mpModel=mp_model),  # fixed community
            transport,
            ContextData(),
            SERIAL_OID
        )
        err_ind, err_stat, err_idx, var_binds = await iterator
        # release sockets
        eng.close_dispatcher()
        if err_ind or err_stat:
            return None
        return var_binds[0][1].prettyPrint()
    except Exception:
        return None

async def _get_serial_async(target: str) -> str | None:
    # Try v2c first
    v2 = await _snmp_get_serial_once(target, mp_model=1)
    if v2:
        return v2
    # Fallback to v1
    v1 = await _snmp_get_serial_once(target, mp_model=0)
    if v1:
        return v1
    return None

def get_serial_via_snmp(target: str) -> str | None:
    """
    Synchronous wrapper so Praeda-II can call this directly from the job.
    Community is fixed to 'public'.
    """
    try:
        return asyncio.run(_get_serial_async(target))
    except Exception:
        return None

