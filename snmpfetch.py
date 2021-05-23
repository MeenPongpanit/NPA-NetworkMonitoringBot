from pysnmp.hlapi import *
from pysnmp.proto.rfc1905 import VarBind
from visualize import utilize_cal

class DEVICE():
    def __init__(self, ip):
        self.ip = ip
        self.interfaces = fetch_interfaces(ip, True)
        self.getifspeed()
        self.inoctets = {index:[] for index in self.interfaces}


    def update_utilization(self, deltatime):
        for index in self.interfaces:
            if len(self.inoctets[index]) < 2:
                return
            speed = self.interfaces[index]['speed']
            inoct1, inoct2 = self.inoctets[index][-2:]
            self.interfaces[index]['util'] = utilize_cal(inoct1, inoct2, speed, deltatime)
            print(self.interfaces[index]['util'])

    def update_inoct(self):
        """Update Interval"""
        self.inoctets = {index:[] for index in self.interfaces}
    
    def lookup_octet(self):
        interfaces_inoct = iter(snmp_walk(self.ip, '1.3.6.1.2.1.2.2.1.10'))
        for index in self.interfaces:
            self.inoctets[index].append(int(next(interfaces_inoct)))
        # print(self.inoctets)

    def getifspeed(self):
        interfaces_desc = iter(snmp_walk(self.ip, '1.3.6.1.2.1.2.2.1.5'))
        for index in self.interfaces:
            self.interfaces[index]['speed'] = int(next(interfaces_desc))

def fetch_oid(target, oid, walk_lenght):
    """Fetch Target's Object at OID"""
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((target, 161)),
        ContextData(), 
        ObjectType(ObjectIdentity(oid))
    )

    result = []
    for _ in range(walk_lenght):
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)  
        if errorIndication:
            return errorIndication
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            # print('hello')
            result.append(varBinds[0][1].prettyPrint())
            # result += '\n'.join([' = '.join([x.prettyPrint() for x in varBind]) for varBind in varBinds]) + '\n'
    # print(result)
    return result

def fetchstr_oid(target, oid, walk_lenght):
    """Fetch Target's Object at OID and return as string"""
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((target, 161)),
        ContextData(), 
        ObjectType(ObjectIdentity(oid)), 
        lexicographicMode=False
    )

    result = ""
    for _ in range(walk_lenght):
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)  
        if errorIndication:
            return errorIndication
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            # print('hello')
            result += '\n'.join([' = '.join([x.prettyPrint() for x in varBind]) for varBind in varBinds]) + '\n'
    # print(result)
    return result

def snmp_walk(target, oid):
    """walk till deepest of mib tree's branch"""
    result = []
    for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(SnmpEngine(), 
                          CommunityData('public'),
                          UdpTransportTarget((target, 161)),
                          ContextData(),                                                           
                          ObjectType(ObjectIdentity(oid)),
                          lexicographicMode=False):
        if errorIndication:
            return str(errorIndication)
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            result.append(varBinds[0][1].prettyPrint())
    return result


def fetch_interfaces(target, returnif=False):
    """Fetch Target's Interfaces"""
    if snmp_walk(target, '1.3.6.1.2.1.2.2.1') == 'No SNMP response received before timeout':
        return 'Time out.'

    interfaces = {index:{} for index in map(int, snmp_walk(target, '1.3.6.1.2.1.2.2.1.1'))}
    interfaces_desc = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.2'))
    interfaces_adminstat = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.7'))
    interfaces_operstat = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.8'))
    interfaces_ip = iter(snmp_walk(target, '1.3.6.1.2.1.4.20.1.1'))
    interfaces_netmask = iter(snmp_walk(target, '1.3.6.1.2.1.4.20.1.3'))

    

    for index in interfaces:
        interfaces[index]['desc'] = next(interfaces_desc)
        interfaces[index]['adminstat'] = ('UP', 'DOWN', 'TESTING')[int(next(interfaces_adminstat)) - 1]
        interfaces[index]['operstat'] = ('UP', 'DOWN', 'TESTING')[int(next(interfaces_operstat)) - 1]

    for index in map(int, snmp_walk(target, '1.3.6.1.2.1.4.20.1.2')):
        interfaces[index]['ip'] = next(interfaces_ip)
        interfaces[index]['netmask'] = next(interfaces_netmask)

    if returnif:
        return interfaces
    reply = f'Device: {target}\n------------------------\nINDEX   DESC                IP             MASK           STATUS\n'
    for index in interfaces:
        desc = interfaces[index]['desc']
        ip = interfaces[index].get('ip', 'unassigned')
        mask = interfaces[index].get('netmask', 'unassigned')
        adminstat = interfaces[index]['adminstat']
        operstat = interfaces[index]['operstat']

        reply += f'{"%-8s"%index}{"%-20s"%desc}{"%-15s"%ip}{"%-15s"%mask}{"%-15s"%(adminstat + "/" + operstat)}\n'
        # print(reply)
    return reply
    
def fetch_ifutilization(target):
    """Fetch interfaces ultilization of target device"""
    interfaces_desc = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.2'))
    interfaces_speed = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.5'))
    interfaces_operstat = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.8'))

    # interface


# print(snmp_walk('10.0.15.213', '1.3.6.1.2.1.2.2.1.5'))
# 1.3.6.1.2.1.2.2.1.5
# print(fetch_interfaces('10.0.15.213'))