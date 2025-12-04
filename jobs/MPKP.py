# KYOCERA Document Solutions Printing System finger print validation  
######################################################
#                 PRAEDA II Module #MPHP
#                  Copyright (C) 2023
#              Deral 'percent_x' Heiland
######################################################
# this module will print results for positive fingerprints
#
import re
import asyncio

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

# OID for device model string (HP)
DEVICE_MODEL_OID = '1.3.6.1.4.1.1347.40.35.1.1.2.1'  # returns string"

# ------------------------ helpers ------------------------

def extract_device_model(snmp_data: str) -> str:
    """
    Return SNMP model data exactly as provided by the OID.
    No parsing.
    """
    if snmp_data and snmp_data.strip():
        return snmp_data.strip()
    return "Unknown Model"


async def _snmp_get_once(target: str, oid: str, mp_model: int, timeout: float = 2.0, retries: int = 1) -> str | None:
    """
    Perform a single SNMP GET using PySNMP 7.x asyncio HLAPI.
    mp_model: 1=v2c, 0=v1
    Returns the value string on success, or None on failure.
    """
    try:
        eng = SnmpEngine()
        # REQUIRED in pysnmp 7.x: async transport factory
        transport = await UdpTransportTarget.create((target, 161), timeout=timeout, retries=retries)
        iterator = get_cmd(
            eng,
            CommunityData('public', mpModel=mp_model),  # fixed community
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        err_ind, err_stat, err_idx, var_binds = await iterator
        # release sockets
        eng.close_dispatcher()
        if err_ind or err_stat:
            return None
        return var_binds[0][1].prettyPrint()
    except Exception:
        return None

async def _get_device_model_snmp_async(target: str, oid: str) -> str | None:
    # Try v2c first
    v2 = await _snmp_get_once(target, oid, mp_model=1)
    if v2:
        return v2
    # Fallback to v1
    v1 = await _snmp_get_once(target, oid, mp_model=0)
    return v1

def get_device_model_snmp(target: str, oid: str) -> str | None:
    """
    Synchronous wrapper used by Praeda-II job runner.
    Returns the SNMP value as a string or None on failure.
    """
    try:
        return asyncio.run(_get_device_model_snmp_async(target, oid))
    except Exception:
        return None

# ------------------------ job entry ------------------------

def MPKP(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            snmp_data = get_device_model_snmp(TARGET, DEVICE_MODEL_OID)

            if snmp_data:
                device_model = extract_device_model(snmp_data)
                logFile.write(f"\033[93mIDENTIFIED\033[0m:5:Finger Printed:{TARGET}:{PORTS}:{device_model}:::::\n")
                print(f"MFP device validated on network with Finger Print of {device_model}\n")
            else:
                logFile.write("Failed to retrieve SNMP data.\n")
                print("Failed to retrieve SNMP data.\n")

    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")

