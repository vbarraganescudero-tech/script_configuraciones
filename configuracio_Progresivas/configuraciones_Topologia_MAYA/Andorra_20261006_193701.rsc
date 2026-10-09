# 2026-10-06 17:37:23 by RouterOS 7.24.2
# system id = 9OjDH5KDonL
#
/interface ethernet
set [ find default-name=ether1 ] disable-running-check=no
set [ find default-name=ether2 ] disable-running-check=no
set [ find default-name=ether3 ] disable-running-check=no
set [ find default-name=ether4 ] disable-running-check=no
set [ find default-name=ether5 ] disable-running-check=no
set [ find default-name=ether6 ] disable-running-check=no
set [ find default-name=ether7 ] disable-running-check=no
set [ find default-name=ether8 ] disable-running-check=no
set [ find default-name=ether9 ] disable-running-check=no
set [ find default-name=ether10 ] disable-running-check=no
/routing ospf instance
add name=ospf-v4 router-id=2.2.2.2
add name=ospf-v6 router-id=2.2.2.2 version=3
/routing ospf area
add instance=ospf-v4 name=area0-v4
add instance=ospf-v6 name=area0-v6
/user group
add name=backup policy="ssh,ftp,read,!local,!telnet,!reboot,!write,!policy,!te\
    st,!winbox,!password,!web,!sniff,!sensitive,!api,!romon,!rest-api"
/ip address
add address=192.168.122.3/24 interface=ether10 network=192.168.122.0
add address=10.2.0.1/16 interface=ether3 network=10.2.0.0
add address=10.255.255.2/30 interface=ether1 network=10.255.255.0
add address=10.255.255.5/30 interface=ether2 network=10.255.255.4
add address=10.255.255.29/30 comment="L4 Australia" interface=ether4 network=\
    10.255.255.28
add address=10.255.255.33/30 comment="L5 Argentina" interface=ether5 network=\
    10.255.255.32
/ip dhcp-client
add interface=ether1 name=client1
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,1.1.1.1
/ip route
add gateway=192.168.122.1
/ip service
set ftp disabled=yes
set telnet disabled=yes
set www disabled=yes
/ipv6 address
add address=2021:16:17:2::1 interface=ether3
add address=2021:16:17:10::2 interface=ether1
add address=2021:16:17:11::1 interface=ether2
add address=2021:16:17:17::1 advertise=no interface=ether4
add address=2021:16:17:18::1 advertise=no interface=ether5
/routing ospf area
add instance=*0 name=area0-v4
add instance=*1 name=area0-v6
/routing ospf interface-template
add area=area0-v4 interfaces=all
add area=area0-v6 interfaces=all
