from pysnmp.hlapi import *

class SwitchSNMP:
    def __init__(self, ip, timeout=2, retries=1):
        self.ip = ip
        self.device_name = "Switch"
        self.timeout = timeout
        self.retries = retries
        self.snmp_table = [
            {"oid": "1.3.6.1.2.1.1.1.0", "description": "System Description"},
            {"oid": "1.3.6.1.2.1.1.3.0", "description": "System Uptime"},
            {"oid": "1.3.6.1.2.1.1.5.0", "description": "System Name"},
            {"oid": "1.3.6.1.2.1.2.2.1.1.1", "description": "Port 1 Status"},
            {"oid": "1.3.6.1.2.1.2.2.1.1.2", "description": "Port 2 Status"}
        ]

    def get_snmp_data(self, oid, community='public'):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((self.ip, 161), timeout=self.timeout, retries=self.retries),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            return str(errorIndication)
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                 errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            for varBind in varBinds:
                return varBind.prettyPrint().split('=')[1].strip()

    def set_snmp_data(self, oid, value, community='private'):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            setCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=0),
                UdpTransportTarget((self.ip, 161), timeout=self.timeout, retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid), Integer(value))
            )
        )

        if errorIndication:
            return str(errorIndication)
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                 errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            return True

    def reset_switch(self):
        reset_oid = '1.3.6.1.4.1.2021.10.1.100'
        result = self.set_snmp_data(reset_oid, 1)
        if result is True:
            return "Switch reset successfully"
        else:
            return f"Failed to reset switch: {result}"

    def toggle_port(self, port_number, state):
        port_oid = f'1.3.6.1.2.1.2.2.1.7.{port_number}'
        result = self.set_snmp_data(port_oid, state)
        if result is True:
            return f"Port {port_number} set to state {state} successfully"
        else:
            return f"Failed to set port {port_number} state: {result}"
