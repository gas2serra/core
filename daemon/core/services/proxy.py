import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

class ProxyService(CoreService):
    _name = "Proxy"
    _group = "SIR"
    _depends = ()
    _dirs = ("/var/log/squid3",)
    _configs = ('proxy.sh', )
    _startindex = 50
    _startup = ('sh proxy.sh',)
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated \n"
        cfg += "/etc/init.d/squid3 start\n"
        return cfg


