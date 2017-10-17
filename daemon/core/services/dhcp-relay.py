import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

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
        cfg += "#/usr/sbin/dhcrelay <dhcp server>\n"
        cfg += "\n"
        return cfg


