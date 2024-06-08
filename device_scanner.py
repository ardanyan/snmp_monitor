from pysnmp.hlapi import *
import concurrent.futures

class SNMPManager:
    def __init__(self, community='public', timeout=2, retries=1):
        self.community = community
        self.timeout = timeout
        self.retries = retries

    def get(self, host, oid):
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(self.community, mpModel=0),
                   UdpTransportTarget((host, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if error_indication:
            return None
        elif error_status:
            return None
        else:
            for var_bind in var_binds:
                return var_bind[1].prettyPrint()

class DeviceScanner:
    def __init__(self, ip_range):
        self.ip_range = ip_range
        self.snmp_manager = SNMPManager()

    def scan(self):
        devices = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.snmp_manager.get, f"{self.ip_range}.{i}", '1.3.6.1.2.1.1.1.0') for i in range(1, 3)]
            for future in concurrent.futures.as_completed(futures):
                sys_descr = future.result()
                if sys_descr:
                    ip = futures.index(future) + 1
                    devices.append({'ip': f"{self.ip_range}.{ip}", 'sys_descr': sys_descr})
        return devices
