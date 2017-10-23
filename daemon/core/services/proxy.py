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
    _dirs = ("/var/log/squid3","/etc/squid3")
    _configs = ('proxy.sh',"/etc/squid3/squid.conf","/etc/squid3/msntauth.conf","/etc/squid3/errorpage.css",)
    _startindex = 50
    _startup = ('sh proxy.sh',)
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated \n"
        if filename == cls._configs[0]:
            cfg += "/etc/init.d/squid3 start\n"
        elif filename == cls._configs[1]:
            cfg += """#Recommended minimum configuration:
#acl manager proto cache_object
acl localhost src 127.0.0.1/32
acl to_localhost dst 127.0.0.0/8
acl localnet src 0.0.0.0/8 192.168.100.0/24 192.168.101.0/24
acl SSL_ports port 443
acl Safe_ports port 80		# http
acl Safe_ports port 21		  # ftp
acl Safe_ports port 443		    # https
acl Safe_ports port 70		      # gopher
acl Safe_ports port 210		      	# wais
acl Safe_ports port 1025-65535		# unregistered ports
acl Safe_ports port 280			  # http-mgmt
acl Safe_ports port 488			    # gss-http
acl Safe_ports port 591			  # filemaker
acl Safe_ports port 777			  	# multiling http

acl CONNECT method CONNECT
 
http_access allow manager localhost
http_access deny manager
http_access deny !Safe_ports

http_access deny to_localhost
icp_access deny all
htcp_access deny all

http_port 3128
hierarchy_stoplist cgi-bin ?
access_log /var/log/squid3/access.log squid
#Suggested default:
refresh_pattern ^ftp:		1440	20%	10080
refresh_pattern ^gopher:	1440	0%	1440
refresh_pattern -i (/cgi-bin/|\?) 0 0% 0
refresh_pattern .  		  0 20%	4320
# Leave coredumps in the first cache dir
coredump_dir /var/spool/squid3
# Allow all machines to all sites
http_access allow all"""
        elif filename == cls._configs[2]:
            cfg += "# NT hosts to use. Best to put their IP addresses in /etc/hosts.\n"
            cfg += "server my_PDC		my_BDC		my_NTdomain\n"
            cfg += "server other_PDC	other_BDC	otherdomain\n"
            cfg += "# Denied and allowed users. Comment these if not needed.\n"
            cfg += "#denyusers	/usr/local/squid/etc/msntauth.denyusers\n"
            cfg += "#allowusers	/usr/local/squid/etc/msntauth.allowusers\n"
        elif filename == cls._configs[3]:
            cfg += """* {
font-family: verdana, sans-serif;
}
html body {
 margin: 0;
 padding: 0;
 background: #efefef;
 font-size: 12px;
	     color: #1e1e1e;
}
/* Page displayed title area */
#titles {
margin-left: 15px;
padding: 10px;
padding-left: 100px;
background: url('http://www.squid-cache.org/Artwork/SN.png') no-repeat left;
}

/* initial title */
#titles h1 {
color: #000000;
}
#titles h2 {
color: #000000;
}
/* special event: FTP success page titles */
#titles ftpsuccess {
background-color:#00ff00;
width:100%;
}
/* Page displayed body content area */
#content {
padding: 10px;
background: #ffffff;
}
/* General text */
p {
}
/* error brief description */
#error p {
}
/* some data which may have caused the problem */
#data {
}
/* the error message received from the system or other software */
#sysmsg {
}
pre {
font-family:sans-serif;
}
/* special event: FTP / Gopher directory listing */
#dirmsg {
font-family: courier;
color: black;
font-size: 10pt;
}
#dirlisting {
margin-left: 2%;
margin-right: 2%;
}
#dirlisting tr.entry td.icon,td.filename,td.size,td.date {
border-bottom: groove;
}
#dirlisting td.size {
width: 50px;
text-align: right;
padding-right: 5px;
}
/* horizontal lines */
hr {
margin: 0;
}
/* page displayed footer area */
#footer {
font-size: 9px;
padding-left: 10px;
}"""
        else:
            cfg += ""
        
        return cfg


