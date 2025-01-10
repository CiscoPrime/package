from pysnmp.hlapi import *
import os


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
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                print(' = '.join([x.prettyPrint() for x in varBind]))
                

if __name__ == '__main__':
    target = '10.23.20.138'
    user = 'NOCAnsible'
    auth_key = 'veryQuick5and!'
    priv_key = 'veryQuick5and!#'
    base_oid = '.1.3.6.1.4.1.9.9.599.1.3.1.1.38'  # OID for system (change as needed)
    
    snmp_v3_walk(target, user, auth_key, priv_key, base_oid)