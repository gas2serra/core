import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

class GreService(CoreService):
    name = "Gre"
    group = "SIR"
    depends = ()
    dirs = ()
    configs = ('gre.sh', )
    startindex = 50
    startup = ('sh gre.sh',)
    shutdown = ()

    @classmethod
    def generate_config(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated\n"
        cfg += "#remote=192.168.0.10\n"
        cfg += "#local=192.168.3.20\n"
        cfg += "#tun_addr=10.0.1.2/30\n"
        cfg += "#tun_remote_ip=10.0.1.1\n"
        cfg += "#tun_forwarding_net=192.168.1.0/24\n"
        cfg += "#ip tunnel add tun1 mode gre remote $remote local $local\n"
        cfg += "#ip link set tun1 up\n"
        cfg += "#ip addr add $tun_addr dev tun1\n"
        cfg += "#ip route add $tun_forwarding_net via $tun_remote_ip\n"
        cfg += "/sbin/sysctl -w net.ipv4.conf.all.forwarding=1\n"
        return cfg
