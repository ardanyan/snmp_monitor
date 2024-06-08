from pysnmp.hlapi import *

class PrinterSNMP:
    def __init__(self, ip):
        self.ip = ip
        self.device_name = "Printer"
        self.snmp_tree = {
            "1.3.6.1.2.1.1": {
                "description": "System Information",
                "explanation": "General system information",
                "children": {
                    "1.3.6.1.2.1.1.1.0": {"description": "System Description", "explanation": "The description of the system"},
                    "1.3.6.1.2.1.1.3.0": {"description": "System Uptime", "explanation": "The time since the system was last restarted"},
                    "1.3.6.1.2.1.1.5.0": {"description": "System Name", "explanation": "The name of the system"},
                }
            },
            "1.3.6.1.2.1.43": {
                "description": "Printer Information",
                "explanation": "Detailed information about the printer",
                "children": {
                    "1.3.6.1.2.1.43.5": {
                        "description": "General Printer Information",
                        "explanation": "Basic information about the printer",
                        "children": {
                            "1.3.6.1.2.1.43.5.1.1.1.2.1": {"description": "Printer Name", "explanation": "The name of the printer"},
                            "1.3.6.1.2.1.43.5.1.1.1.3.1": {"description": "Serial Number", "explanation": "The serial number of the printer"},
                        }
                    },
                    "1.3.6.1.2.1.43.10.2.1.4.1.1": {"description": "Toner Level", "explanation": "Current toner level"},
                    "1.3.6.1.2.1.43.10.2.1.4.1.2": {"description": "Paper Level", "explanation": "Current paper level"},
                }
            }
        }

    def get_snmp_data(self, oid, community='public'):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((self.ip, 161), timeout=5, retries=3),
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
