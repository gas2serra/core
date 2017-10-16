import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

class GreService(CoreService):
    _name = "Gre"
    _group = "SIR"
    _depends = ()
    _dirs = ()
    _configs = ('gre.sh', )
    _startindex = 50
    _startup = ('sh gre.sh',)
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated\n"
        cfg += "#ip tunnel add tun1 mode gre remote 192.168.0.10 local 192.168.3.20\n"
        cfg += "#ip link set tun1 up\n"
        cfg += "#ip addr add 10.0.1.2/30 dev tun1\n"
        cfg += "#ip route add 192.168.1.0/24 via 10.0.1.1\n"
        cfg += "/sbin/sysctl -w net.ipv4.conf.all.forwarding=1\n"
        return cfg
    

