import csv
import os
import json
import logging
from datetime import datetime
from pysnmp.hlapi import *

# Global variable to include OID in CSV cells
INCLUDE_OID_IN_CSV = True  # Set to True to include OID in the CSV

# Configure logging
logging.basicConfig(
    filename='snmp_debug.log',  # Log file
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    filemode='w'  # Overwrite the log file each time the script runs
)

def load_oid_mapping(oid_file_path):
    with open(oid_file_path, 'r') as file:
        oid_data = json.load(file)
   
    if isinstance(oid_data, list):
        oid_to_name = oid_data[0]
    else:
        oid_to_name = oid_data
   
    return oid_to_name

def snmp_v3_walk(target, user, auth_key, priv_key, oid_to_name, oid_file_name):
    results = []
    instances = {}

    # Determine the OID segment logic based on the JSON file being processed
    for name, oid in oid_to_name.items():
        iterator = bulkCmd(
            SnmpEngine(),
            UsmUserData(user, authKey=auth_key, privKey=priv_key,
                        authProtocol=usmHMACSHAAuthProtocol,
                        privProtocol=usmAesCfb128Protocol),
            UdpTransportTarget((target, 161)),
            ContextData(),0,100,
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
        )

        for errorIndication, errorStatus, errorIndex, varBinds in iterator:
            if errorIndication:
                logging.error(f"Error: {errorIndication}")
                break
            elif errorStatus:
                logging.error(f"Error Status: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                break
            else:
                for varBind in varBinds:
                    oid_returned, value = [x.prettyPrint() for x in varBind]
                    logging.debug(f"OID: {oid_returned}, Name: {name}, Value: {value}")

                    # Adjust segment count based on specific file and OID structure
                    if 'bsnDot11EssEntry.json' in oid_file_name:
                        # Use all segments after the base OID for this table
                        base_oid_length = len(oid.split('.'))
                        instance_id = '.'.join(oid_returned.split('.')[base_oid_length:])
                    else:
                        # Default behavior for other files
                        segment_count = 3 if 'bsnAPEntry.json' in oid_file_name else 1
                        instance_id = '.'.join(oid_returned.split('.')[-segment_count:])

                    logging.debug(f"Instance ID: {instance_id}")

                    if instance_id not in instances:
                        instances[instance_id] = {}

                    if INCLUDE_OID_IN_CSV:
                        instances[instance_id][name] = f"{oid_returned}: {value}"
                    else:
                        instances[instance_id][name] = value

    # Convert the instances dictionary to a list of rows for the CSV
    results = [data for instance_id, data in instances.items()]

    # Log each complete row before returning the results
    for row in results:
        logging.debug(f"Complete row: {row}")
   
    return results

def save_to_csv(data, oid_to_name, oid_file_name):
    if not data:
        logging.warning("No data to save.")
        return

    headers = sorted(oid_to_name.keys())
   
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{now}_{oid_file_name.replace('.json', '')}.csv"

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            aligned_row = {header: row.get(header, '') for header in headers}
            logging.debug(f"Writing row: {aligned_row}")
            writer.writerow(aligned_row)

    logging.info(f"Data saved to {csv_filename}")

if __name__ == '__main__':
    target = '10.16.79.246'
    user = 'NOCAnsible'
    auth_key = 'veryQuick5and!'
    priv_key = 'veryQuick5and!#'

    oid_file_path = r'C:\Users\p-langles3\Documents\Gitlab\route\8021xconfig.json'
   
    oid_to_name = load_oid_mapping(oid_file_path)
   
    snmp_data = snmp_v3_walk(target, user, auth_key, priv_key, oid_to_name, os.path.basename(oid_file_path))
   
    save_to_csv(snmp_data, oid_to_name, os.path.basename(oid_file_path))
