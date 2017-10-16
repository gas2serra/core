import os

from core.service import CoreService, addservice
from core.misc.ipaddr import IPv4Prefix, IPv6Prefix

class TelnetService(CoreService):
    _name = "Telnet"
    _group = "SIR"
    _depends = ()
    _dirs = ()
    _configs = ('telnet.sh', )
    _startindex = 50
    _startup = ('sh telnet.sh',)
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated\n"
        cfg += "/usr/sbin/inetd /etc/inetd.conf\n"
        return cfg


