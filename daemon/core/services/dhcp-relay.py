import os

from core.service import CoreService, addservice
from core.misc.ipaddr import IPv4Prefix, IPv6Prefix

class DHCPRelayService(CoreService):
    _name = "DHCPRelay"
    _group = "SIR"
    _depends = ()
    _dirs = ()
    _configs = ('dhcp-relay.sh', )
    _startindex = 50
    _startup = ('sh dhcp-relay.sh',)
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        cfg = "#!/bin/sh\n"
        cfg += "#/usr/sbin/dhcrelay 192.168.1.10\n"
        cfg += "/usr/sbin/dhcrelay\n"
        return cfg

addservice(DHCPRelayService)

