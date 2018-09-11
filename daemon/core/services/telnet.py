import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

class TelnetService(CoreService):
    name = "Telnet"
    group = "SIR"
    depends = ()
    dirs = ()
    configs = ('telnet.sh', )
    startindex = 50
    startup = ('sh telnet.sh',)
    shutdown = ()

    @classmethod
    def generate_config(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated\n"
        cfg += "/usr/sbin/inetd /etc/inetd.conf\n"
        return cfg
