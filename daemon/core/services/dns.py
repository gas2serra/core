import os

from core import constants
from core.enumerations import LinkTypes, NodeTypes
from core.misc import ipaddress
from core.misc import nodeutils
from core.service import CoreService

class DnsService(CoreService):
    _name = "Dns"
    _group = "SIR"
    _depends = ()
    _dirs = ("/var/run/named","/var/cache/bind","/etc/bind")
    _configs = ('dns.sh',"/etc/bind/named.conf", "/etc/bind/db.root", "/etc/bind/db.local", "/etc/bind/db.127", "/etc/bind/db.0", "/etc/bind/db.255", "/etc/bind/db.mydom","/etc/bind/rndc.key",)
    _startindex = 50
    _startup = ('sh dns.sh',)
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        cfg = ""
        if filename == cls._configs[0]:
            cfg = "#!/bin/sh\n"
            cfg += "# auto-generated \n"
            cfg += "/etc/init.d/bind9 start\n"
        elif filename == cls._configs[1]:
            cfg += """
options {
	directory "/var/cache/bind";
        dnssec-validation auto;
        auth-nxdomain no;    # conform to RFC1035
	listen-on-v6 { any; };
};
// prime the server with knowledge of the root servers
zone "." {
	type hint;
	file "/etc/bind/db.root";
};

// be authoritative for the localhost forward and reverse zones, and for
// broadcast zones as per RFC 1912

zone "localhost" {
	type master;
	file "/etc/bind/db.local";
};

zone "127.in-addr.arpa" {
	type master;
	file "/etc/bind/db.127";
};

zone "0.in-addr.arpa" {
	type master;
	file "/etc/bind/db.0";
};

zone "255.in-addr.arpa" {
	type master;
	file "/etc/bind/db.255";
};


zone "mydom.lan" { 
            type master; 
            file "/etc/bind/db.mydom"; 
};

"""
        elif filename == cls._configs[2]:
            cfg += """
;db.root
;
;
;

"""
        elif filename == cls._configs[3]:
            cfg += """
;db.local;
; BIND data file for local loopback interface
;
$TTL	604800
@	IN	SOA	localhost. root.localhost. (
			      2		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	localhost.
@	IN	A	127.0.0.1
@	IN	AAAA	::1

"""
        elif filename == cls._configs[4]:
            cfg += """
; db.127
;
;
; BIND reverse data file for local loopback interface
;
$TTL	604800
@	IN	SOA	localhost. root.localhost. (
			      1		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	localhost.
1.0.0	IN	PTR	localhost.

"""
        elif filename == cls._configs[5]:
            cfg += """
; db.0;
;
; BIND reverse data file for broadcast zone
;
$TTL	604800
@	IN	SOA	localhost. root.localhost. (
			      1		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	localhost.

"""
        elif filename == cls._configs[6]:
            cfg += """
; db.255;
;
; BIND reverse data file for broadcast zone
;
$TTL	604800
@	IN	SOA	localhost. root.localhost. (
			      1		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	localhost.

"""
        elif filename == cls._configs[7]:
            cfg += """
; db.mydom;
$ORIGIN .
; ---Area 1---
$TTL 86400      ; 1 day

; ---Area 2---
mydom.lan       IN      SOA     ns1.mydom.lan. hostmaster.mydom.lan. (
            2007081501 ; serial
            86400      ; refresh (1 giorno)
            28800      ; retry (8 ore)
            604800     ; expire (1 settimana)
            86400      ; minimum (1 giorno)
															
            );
															
; ---Area 3---
															
            IN      NS      ns1.mydom.lan.

; ---Area 4---
$ORIGIN mydom.lan.
;NOTA: ns1 è il nome del server che funge da DNS server
ns1             IN      A       192.168.1.1
; Qui potete inserire gli IP dei client-server che hanno un IP statico
pippo          IN      A       192.168.0.20
pluto	    IN 	    A	    192.168.1.1

"""
        elif filename == cls._configs[8]:
            cfg += """
key "rndc-key" {
	algorithm hmac-md5;
	secret "CiU2ZuHGbSxt9wZT3gXS7w==";
};
"""
        elif filename == cls._configs[9]:
            cfg += """

"""
        else:
            cfg += ""
            
        return cfg


