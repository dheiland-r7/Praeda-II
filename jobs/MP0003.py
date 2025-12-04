# Xerox check device to see if Remote Control is enabled for unauthenticated users 
######################################################
#                 PRAEDA II Module #MP0003           #
#                  Copyright (C) 2023                #
#              Deral 'percent_x' Heiland             #
######################################################
# this module will work on the following Xerox models
#      VersaLink C7020, C7025, C7130, B7030, B7125
#
import asyncio
import requests

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

def MP0003(TARGET, PORTS, web, OUTPUT, LOGFILE, data1):
    # Set global variables
    OID = '1.3.6.1.4.1.253.8.53.13.2.1.6.1.180.200'  # Xerox Remote Control state

    # Open output file for logging
    try:
        with open(f'{OUTPUT}/{LOGFILE}.log', 'a') as logFile:
            result = query_snmp(TARGET, OID)  # returns int or None
            if result is not None:
                if result == 0:
                    print("FAILED: Unauthenticated Remote Control is Disabled")
                    logFile.write(f"FAILED:0:Unauthenticated Remote Control:{TARGET}:{PORTS}:{data1}xxx::::Disabled:")
                elif result == 3:
                    print("\033[91mSUCCESS\033[0m: Unauthenticated Remote Control is ENABLED")
                    logFile.write(f"\033[91mSUCCESS\033[0m:0:Unauthenticated Remote Control:{TARGET}:{PORTS}:{data1}xxx::::ENABLED:")
                else:
                    print(f"Status of Remote Control is Unknown ({result})")
            else:
                print("Couldn't get a read on Remote Control state.")
    except Exception as e:
        print(f"Failed to open output file {OUTPUT}\nError: {str(e)}")

# ---------------------------- SNMP helpers (PySNMP 7.x async) ------------------------

async def _snmp_get_oid_once(target: str, oid_str: str, mp_model: int, timeout: float = 2.0, retries: int = 1):
    """
    Perform a single SNMP GET for the given OID using PySNMP 7.x asyncio HLAPI.
    mp_model: 1=v2c, 0=v1
    Returns the value object on success, or None on failure.
    """
    try:
        eng = SnmpEngine()
        # IMPORTANT: async transport factory is required in pysnmp 7.x
        transport = await UdpTransportTarget.create((target, 161), timeout=timeout, retries=retries)
        iterator = get_cmd(
            eng,
            CommunityData('public', mpModel=mp_model),  # fixed community per project standard
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid_str))
        )
        err_ind, err_stat, err_idx, var_binds = await iterator
        # release sockets
        eng.close_dispatcher()
        if err_ind or err_stat:
            return None
        # Return the pysnmp value object
        return var_binds[0][1]
    except Exception:
        return None

def _to_int(val) -> int | None:
    """
    Best-effort conversion of pysnmp value to int.
    """
    if val is None:
        return None
    try:
        # many SNMP numeric types prettyPrint as decimal strings
        return int(val.prettyPrint())
    except Exception:
        try:
            # sometimes it's already numeric-like
            return int(val)
        except Exception:
            return None

async def _query_snmp_async(target: str, oid_str: str) -> int | None:
    # Try v2c first
    v2_val = await _snmp_get_oid_once(target, oid_str, mp_model=1)
    iv = _to_int(v2_val)
    if iv is not None:
        return iv
    # Fallback to v1
    v1_val = await _snmp_get_oid_once(target, oid_str, mp_model=0)
    return _to_int(v1_val)

def query_snmp(TARGET, OID) -> int | None:
    """
    Synchronous wrapper so Praeda-II can call this directly from the job.
    Returns an int (when possible) or None on failure.
    """
    try:
        return asyncio.run(_query_snmp_async(TARGET, OID))
    except Exception:
        return None

# ---------------------------------------------------

