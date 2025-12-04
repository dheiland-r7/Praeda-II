# XEROX validate LDAP is enabled and current settings
######################################################
#                 PRAEDA II Module #MP0015           #
#                  Copyright (C) 2024                #
#              Deral 'percent_x' Heiland             #
######################################################
# This module will work on the following Xerox models:
#      VersaLink C7020, C7025, C7130, B7030, B7125
######################################################

import asyncio
import ipaddress

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

def MP0015(target, ports, web, output, logfile, data1):
    """ Main function to perform SNMP checks for Xerox LDAP configuration. """
    
    # OIDs to check
    ldap_server_oid = '1.3.6.1.4.1.253.8.74.6.2.1.9.7.155.114.11'
    ldap_oids = {
        "ldap_base_dn": '1.3.6.1.4.1.253.8.74.6.2.1.9.7.155.118.1',
        "ldap_service": '1.3.6.1.4.1.253.8.74.6.2.1.9.7.155.122.1',
        "ldap_auth_method": '1.3.6.1.4.1.253.8.74.6.2.1.9.7.155.136.1'
    }

    # Check ldap_server first
    ldap_server_value = get_snmp_data(ldap_server_oid, target)

    # Try to open output file for logging
    try:
        with open(f'{output}/{logfile}.log', 'a') as logFile:
            if ldap_server_value and is_valid_ip(ldap_server_value):
                # Gather the values of the other OIDs
                ldap_values = []
                for key, oid in ldap_oids.items():
                    value = get_snmp_data(oid, target)
                    if value:
                        ldap_values.append(value)
                    else:
                        ldap_values.append('N/A')  # In case no data is returned
        
                print(f"\033[91mSUCCESS\033[0m: The Xerox MFP {target} appears to be configured for LDAP services:")
                logFile.write(
                    f"\033[91mSUCCESS\033[0m:5:The LDAP service is enabled:{target}:{ports}:{data1}:"
                    f"LDAP User Name {ldap_values[1]}:LDAP Auth Type {ldap_values[2]}:::auxiliary/server/ldap"
                )
            else:
                print(f"FAILURE:  The Xerox MFP {target} does not appear to have LDAP services configured ")
                logFile.write(f"FAILURE: ldap_server OID {ldap_server_oid} returned no data")
    except Exception as e:
        print(f"Failed to make connection to URL \nError: {str(e)}")


# ---------------------------- SNMP helpers (PySNMP 7.x async; community='public') ----------------------------

async def _snmp_get_once(ip: str, oid: str, mp_model: int, timeout: float = 2.0, retries: int = 1) -> str | None:
    """
    Perform a single SNMP GET for the given OID using PySNMP 7.x asyncio HLAPI.
    mp_model: 1=v2c, 0=v1
    Returns the value string on success, or None on failure.
    """
    try:
        eng = SnmpEngine()
        # IMPORTANT: async transport factory is required in pysnmp 7.x
        transport = await UdpTransportTarget.create((ip, 161), timeout=timeout, retries=retries)
        iterator = get_cmd(
            eng,
            CommunityData('public', mpModel=mp_model),  # fixed community per project standard
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

async def _get_snmp_data_async(oid: str, ip: str) -> str | None:
    # Try v2c first
    v2 = await _snmp_get_once(ip, oid, mp_model=1)
    if v2:
        return v2
    # Fallback to v1
    v1 = await _snmp_get_once(ip, oid, mp_model=0)
    return v1

def get_snmp_data(oid: str, ip: str) -> str | None:
    """ Synchronous wrapper for SNMP GET that returns a string or None. """
    try:
        return asyncio.run(_get_snmp_data_async(oid, ip))
    except Exception:
        return None


# Function to validate the IP address in the Xerox OID is a valid address and not default of 0.0.0.0
def is_valid_ip(ldap_server_value: str) -> bool:
    """ Validate the IP address and ensure it's not the default 0.0.0.0.
        Expected format like '192.168.4.56.389' (IP + port). """
    try:
        parts = ldap_server_value.split('.')

        # If we have more than 4 parts, assume the last part is the port number
        if len(parts) == 5:
            ip = '.'.join(parts[:4])
            port = parts[4]
        else:
            print(f"Invalid format: {ldap_server_value}")
            return False

        # Validate the IP address
        ipaddress.ip_address(ip)

        # Check if it's not the default 0.0.0.0
        if ip == "0.0.0.0":
            return False

        # Validate the port
        if not port.isdigit() or not (0 < int(port) <= 65535):
            print(f"Invalid port: {port}")
            return False

        return True
    except ValueError:
        return False

