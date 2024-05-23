"""
Fixtures for tests

Mostly multiline strings of the xml from the devices
"""

IOSXR_GET_INTERFACE = """<?xml version="1.0" encoding="UTF-8"?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" \
    xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
   <interface-configuration>
    <active>act</active>
    <interface-name>Loopback0</interface-name>
    <interface-virtual/>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>10.0.0.1</address>
       <netmask>255.255.255.255</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
  </interface-configurations>
 </data>
"""

IOSXR_GET_INTERFACE_MISSING = """<?xml version="1.0" encoding="UTF-8"?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" \
    xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
 </data>
"""

IOSXR_GET_INTERFACES = """<?xml version="1.0" encoding="UTF-8"?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" \
    xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interface-configurations \
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
   <interface-configuration>
    <active>act</active>
    <interface-name>Loopback0</interface-name>
    <interface-virtual/>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>10.0.0.1</address>
       <netmask>255.255.255.255</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>Loopback100</interface-name>
    <interface-virtual/>
    <description>***TEST LOOPBACK****</description>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>1.1.1.100</address>
       <netmask>255.255.255.255</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>Loopback555</interface-name>
    <interface-virtual/>
    <description>PRUEBA_KV</description>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>Loopback999</interface-name>
    <interface-virtual/>
    <vrf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-infra-rsi-cfg">TEST</vrf>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>10.10.10.10</address>
       <netmask>255.255.255.255</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>MgmtEth0/RP0/CPU0/0</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>10.10.20.175</address>
       <netmask>255.255.255.0</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/0</interface-name>
    <description>test</description>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/1</interface-name>
    <description>test</description>
    <shutdown/>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/2</interface-name>
    <description>test</description>
    <shutdown/>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/3</interface-name>
    <description>test</description>
    <shutdown/>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/4</interface-name>
    <shutdown/>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/5</interface-name>
    <shutdown/>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/6</interface-name>
    <shutdown/>
   </interface-configuration>
  </interface-configurations>
 </data>
"""

IOSXR_CREATE_INTERFACE = """<config>
    <interface-configurations \
xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <interface-configuration>
            <active>act</active>
            <interface-name>vlan1</interface-name>
            <interface-virtual/>
            <ipv4-network \
xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
                <addresses>
                    <primary>
                        <address>10.0.0.1</address>
                        <netmask>255.255.255.255</netmask>
                    </primary>
                </addresses>
            </ipv4-network>
        </interface-configuration>
    </interface-configurations>
</config>"""

IOSXR_DELETE_INTERFACE = '''<config \
xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <interface-configurations \
xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <interface-configuration nc:operation="delete">
            <active>act</active>
            <interface-name>vlan1</interface-name>
        </interface-configuration>
    </interface-configurations>
</config>
'''
