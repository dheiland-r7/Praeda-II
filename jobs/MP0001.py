# Xerox default password validation check module 
######################################################
#                 PRAEDA II Module #MP0001           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Xerox models
#      VersaLink C7020,C7025,C7130,B7030,B7125

import asyncio
import requests
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

# OID: Printer-MIB::prtGeneralSerialNumber.1
SERIAL_OID = ObjectType(ObjectIdentity('1.3.6.1.2.1.43.5.1.1.17.1'))

def MP0001(target, ports, web, output, logfile, data1):
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            # First test with common default xerox password "1111"
            if try_login(target, ports, web, "YWRtaW4=", encode_password("1111"), output, logfile):
                print("\033[91mSUCCESS\033[0m: The Xerox devices Admin password is 1111\n")
                logFile.write(f"\033[91mSUCCESS\033[0m:1:Xerox Device credential:{target}:{ports}:{data1}xxx:Admin:1111:::\n")
            else:
                # If password 1111 attempt fails, retrieve the serial number and try that
                serial = get_serial_via_snmp(target)
                if serial:
                    serial_base64 = encode_password(serial)
                    if try_login(target, ports, web, "YWRtaW4=", serial_base64, output, logfile):
                        print(f"\033[91mSUCCESS\033[0m: The Xerox device's Admin password is the serial number {serial}\n")
                        logFile.write(f"\033[91mSUCCESS\033[0m:1:Xerox Device credential:{target}:{ports}:{data1}xxx:Admin:{serial}:::")
                    else:
                        print("FAIL: Neither default password nor serial number worked.\n")
                        logFile.write(f"FAIL:1:Xerox device's admin password could not be determined:{target}:{ports}:{data1}xxx:Admin:?:::")
                else:
                    print("FAIL: Could not retrieve serial number via SNMP.\n")
                    logFile.write(f"FAIL:1:Could not retrieve serial number via SNMP:{target}:{ports}:{data1}xxx:::::")
    except Exception as e:
        print(f"Failed to open output file {output}\nError: {str(e)}")


def encode_password(password: str) -> str:
    return base64.b64encode(password.encode()).decode()


def try_login(target, ports, web, username_b64, password_base64, output, logfile) -> bool:
    """
    username_b64 should already be base64 ('YWRtaW4=' for 'admin')
    """
    url = f"http{web}://{target}:{ports}/LOGIN.cmd?NAME={username_b64}&PSW={password_base64}"
    expected_response = {
        "result": "0",
        "errorCode": "0",
        "koDefault": "0",
        "snmpDefault": "0",
        "globalIP": "0",
        "passwordChangeRequired": "0"
    }
    try:
        response = requests.get(url, verify=False, timeout=4)
        if response.status_code == 200:
            # Some devices return JSON, others return plain text. Try JSON first.
            try:
                if response.json() == expected_response:
                    return True
            except Exception:
                # Fallback: compare raw body if device isn't returning JSON-type header
                if response.text.strip().replace(" ", "") == str(expected_response).replace(" ", ""):
                    return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return False


# -------------------- SNMP helpers (PySNMP 7.x async; community='public') --------------------

async def _snmp_get_once_serial(target: str, mp_model: int, timeout: float = 2.0, retries: int = 1):
    """
    Single SNMP GET for prtGeneralSerialNumber.1 using PySNMP 7.x asyncio HLAPI.
    mp_model: 1=v2c, 0=v1
    Returns the string value on success, or None on failure.
    """
    try:
        eng = SnmpEngine()
        # IMPORTANT: async transport factory is required in pysnmp 7.x
        transport = await UdpTransportTarget.create((target, 161), timeout=timeout, retries=retries)
        iterator = get_cmd(eng, CommunityData('public', mpModel=mp_model), transport, ContextData(), SERIAL_OID)
        err_ind, err_stat, err_idx, var_binds = await iterator
        # release sockets
        eng.close_dispatcher()
        if err_ind or err_stat:
            return None
        # Return the serial as string
        return var_binds[0][1].prettyPrint()
    except Exception:
        return None


async def _get_serial_async(target: str) -> str | None:
    # Try v2c first
    v2 = await _snmp_get_once_serial(target, mp_model=1)
    if v2:
        return v2
    # Fallback to v1
    v1 = await _snmp_get_once_serial(target, mp_model=0)
    if v1:
        return v1
    return None


def get_serial_via_snmp(target: str) -> str | None:
    """
    Synchronous wrapper so Praeda-II can call this directly from the job.
    Community is fixed to 'public' (per project standard).
    """
    try:
        return asyncio.run(_get_serial_async(target))
    except Exception:
        return None

