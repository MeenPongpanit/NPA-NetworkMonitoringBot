from pysnmp.hlapi import *
from pysnmp.proto.rfc1905 import VarBind

class INTERFACE():
    def __init__(self, index, desc, ip, adminstat, operstat):
        self.index = index
        self.desc = desc
        self.ip = ip
        self.adminstat = adminstat
        self.operstat = operstat

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
    """Fetch Target's Object at OID"""
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
    result = []
    for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(SnmpEngine(), 
                          CommunityData('public'),
                          UdpTransportTarget((target, 161)),
                          ContextData(),                                                           
                          ObjectType(ObjectIdentity(oid)),
                          lexicographicMode=False):
        if errorIndication:
            return errorIndication
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            result.append(varBinds[0][1].prettyPrint())
    return result


def fetch_interfaces(target):
    """Fetch Target's Interfaces"""
    # interfaces_amount = int(fetch_oid(target, '1.3.6.1.2.1.2.1', 1)[0]) - 2
    interfaces = {index:{} for index in map(int, snmp_walk(target, '1.3.6.1.2.1.2.2.1.1'))}
    interfaces_desc = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.2'))
    interfaces_adminstat = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.7'))
    interfaces_operstat = iter(snmp_walk(target, '1.3.6.1.2.1.2.2.1.8'))
    interfaces_ip = iter(snmp_walk(target, '1.3.6.1.2.1.4.20.1.1'))
    interfaces_netmask = iter(snmp_walk(target, '1.3.6.1.2.1.4.20.1.3'))


    # print(interfaces_desc)
    for index in interfaces:
        interfaces[index]['desc'] = next(interfaces_desc)
        interfaces[index]['adminstat'] = ('UP', 'DOWN', 'TESTING')[int(next(interfaces_adminstat)) - 1]
        interfaces[index]['operstat'] = ('UP', 'DOWN', 'TESTING')[int(next(interfaces_operstat)) - 1]

    for index in map(int, snmp_walk(target, '1.3.6.1.2.1.4.20.1.2')):
        interfaces[index]['ip'] = next(interfaces_ip)
        interfaces[index]['netmask'] = next(interfaces_netmask)

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
    
    # # 1.3.6.1.2.1.2.2.1.1
    # interfaces_adminstat = fetch_oid(target, '1.3.6.1.2.1.2.2.1.7', interfaces_amount)
    # interfaces_adminstat = [('up', 'down', 'testing')[int(stat)-1] for stat in interfaces_adminstat]
    # interfaces_operstat = fetch_oid(target, '1.3.6.1.2.1.2.2.1.8', interfaces_amount)
    # interfaces_operstat = [('up', 'down', 'testing')[int(stat)-1] for stat in interfaces_operstat]
    # print(interfaces_desc)
    # print(interfaces_adminstat)
    # print(interfaces_operstat)
    # return interfaces_amount

# print(fetch_interfaces('10.0.15.213'))