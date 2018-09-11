import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

class DHCPRelayService(CoreService):
    name = "DHCPRelay"
    group = "SIR"
    depends = ()
    dirs = ()
    configs = ('dhcp-relay.sh', )
    startindex = 50
    startup = ('sh dhcp-relay.sh',)
    shutdown = ()

    @classmethod
    def generate_config(cls, node, filename, services):
        cfg = "#!/bin/sh\n"
        cfg += "#/usr/sbin/dhcrelay <dhcp server>\n"
        cfg += "\n"
        return cfg


