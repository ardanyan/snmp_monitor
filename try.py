from pysnmp.hlapi import *

def snmp_walk(ip, community='public'):
    oid = '1.3.6.1.2.1'
    result = []

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                result.append(f'{varBind[0].prettyPrint()} = {varBind[1].prettyPrint()}')

    return result

def save_snmp_walk(ip, filename, community='public'):
    data = snmp_walk(ip, community)
    with open(filename, 'w') as file:
        for line in data:
            file.write(line + '\n')

if __name__ == "__main__":
    ip = '192.168.0.1'  # IP adresini gerektiği gibi güncelleyin
    community = 'public'
    filename = 'snmpwalk_output.txt'
    save_snmp_walk(ip, filename, community)
    print(f"SNMP Walk data saved to {filename}")
