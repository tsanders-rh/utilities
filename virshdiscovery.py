#! /usr/bin/env python
#! /usr/bin/env python
#
# Copyright (c) 2016 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import paramiko

HOST="mustang.usersys.redhat.com"
USERNAME="root"
PASSWORD="dog8code"

def print_interface_info(domain_data):

	for d in domain_data:
		print 'Domain Name: ' + d['name']
		print '  Interfaces:'
		for i in d['interfaces']:
			print "    MAC Address: " + i['mac address'] + " (" + i['alias name'] + ")"
		print ""

domains_list = []

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD)

stdin, stdout, stderr = ssh.exec_command("virsh list --all | awk '$1 == \"-\" || $1+0 > 0 { print $2 }'")
domains = stdout.channel.recv(1024)

for d in domains.split():

	domain = {}
	domain['name'] = d

	stdin, stdout, stderr = ssh.exec_command("virsh dumpxml " + d + " | xmllint --xpath '//interface/mac | //interface/alias' - |  awk -F'\"' '{ for (i=2;i<=NF;i+=2) print $i }'")
	interfaces_attrs = stdout.channel.recv(1024)

	interfaces = []
	interface = {}

	for idx, iface in enumerate(interfaces_attrs.split()):

		if idx % 2 == 0:
			interface['mac address'] = iface
		else:
			interface['alias name'] = iface
			interfaces.append(interface)
			interface = {}

	domain['interfaces'] = interfaces
	domains_list.append(domain)


print_interface_info(domains_list)




		
