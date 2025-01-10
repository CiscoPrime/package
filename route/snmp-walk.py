from pysnmp.hlapi import *
import os
import logging

# Configure logging
log_file = "snmp_walkAAA.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def snmp_v3_walk(target, user, auth_key, priv_key, base_oid):
    iterator = nextCmd(
        SnmpEngine(),
        UsmUserData(user, authKey=auth_key, privKey=priv_key,
                    authProtocol=usmHMACSHAAuthProtocol,
                    privProtocol=usmAesCfb128Protocol),
        UdpTransportTarget((target, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(base_oid)),
        lexicographicMode=False
    )

    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            logging.error(f"SNMP error: {errorIndication}")
            break
        elif errorStatus:
            error_message = ('%s at %s' % (errorStatus.prettyPrint(),
                             errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            logging.error(error_message)
            break
        else:
            for varBind in varBinds:
                message = ' = '.join([x.prettyPrint() for x in varBind])
                logging.info(message)

if __name__ == '__main__':
    target = '10.42.41.61'
    user = 'NOCAnsible'
    auth_key = 'veryQuick5and!'
    priv_key = 'veryQuick5and!#'
    base_oid = '.1.3.6.1.4.1.9.'  # OID for system (change as needed)

    try:
        snmp_v3_walk(target, user, auth_key, priv_key, base_oid)
        logging.info("SNMP walk completed successfully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
