# XEROX validate LDAP is enabled and current settings
######################################################
#                 PRAEDA II Module #MP0016           #
#                  Copyright (C) 2024                #
#              Deral 'percent_x' Heiland             #
######################################################
# This module will work on the following Xerox models:
#      VersaLink C7020, C7025, C7130, B7030, B7125
######################################################

from pysnmp.hlapi import *
import ipaddress

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
            # logFile.write(f"### Xerox LDAP Configuration Check for {TARGET} ###\n\n")
            
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
                logFile.write(f"\033[91mSUCCESS\033[0m:5:The LDAP service is enabled:{target}:{ports}:{data1}:LDAP User Name {ldap_values[1]}:LDAP Auth Type {ldap_values[2]}:::auxiliary/server/ldap\n")


            else:
                print(f"FAILURE:  The Xerox MFP {target} does not appear to have LDAP services configured ")
                logFile.write(f"FAILURE: ldap_server OID {ldap_server_oid} returned no data")

    except Exception as e:
        print(f"Failed to make connection to URL \nError: {str(e)}")


def get_snmp_data(oid, ip, community='public'):
    """ Function to perform SNMP GET on an OID. """
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    error_indication, error_status, error_index, var_binds = next(iterator)

    if error_indication:
        print(f'Error: {error_indication}')
        return None
    elif error_status:
        print(f'Error: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1] or "?"}')
        return None
    else:
        for var_bind in var_binds:
            _, value = var_bind
            return str(value)



#Function to validate the IP address in the Xerox OID is a valid address and not default of 0.0.0.0

def is_valid_ip(ldap_server_value):
    """ Function to validate the IP address and ensure it's not the default 0.0.0.0. """
    try:
        # The OID might return something like '192.168.4.56.389', so we need to handle that
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

        # Optionally, validate the port (e.g., check it's within a valid range)
        if not port.isdigit() or not (0 < int(port) <= 65535):
            print(f"Invalid port: {port}")
            return False

        return True

    except ValueError:
        # If splitting or validating the IP fails, return False
        return False

