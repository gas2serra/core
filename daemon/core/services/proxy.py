import os

from core.service import CoreService, addservice
from core.misc.ipaddr import IPv4Prefix, IPv6Prefix

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

addservice(ProxyService)

