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

#
#Imports
#

import sys
import libvirt
from xml.dom import minidom
from gettext import gettext as _
from optparse import OptionParser
import pexpect

#
# Constants
#

USAGE = _('%prog <options>')

DESCRIPTION = _('Obtain interface attributes for active libvirt domain on specified hypervisor.')

SERVER = _('Set the hostname or ip address of the hypervisor to be interogated.')

USERNAME = _('Set the username for SSH authentication.')

PASSWORD = _('Set the password for SSH authentication.')


def get_options():
    """
    Parse and return command line options.
    Sets defaults and validates options.
    :return: The options passed by the user.
    :rtype: optparse.Values
    """
    parser = OptionParser(usage=USAGE, description=DESCRIPTION)
    parser.add_option("-s", "--server", dest="server", help=SERVER)
    parser.add_option("-u", "--username", dest="username", help=USERNAME)
    parser.add_option("-p", "--password", dest="password", help=PASSWORD)

    (opts, args) = parser.parse_args()

    # validate
    if opts.server is not None:
        if not opts.username or not opts.password: 
            print "Please enter a valid username & password combination. (see -h for help)"
            sys.exit(1)

    return opts


def construct_interface_structure(active_hosts, conn):

    domains = []

    for id in active_hosts:
        dom = conn.lookupByID(id)
        domain = {}
        domain['name'] = dom.name()

        raw_xml = dom.XMLDesc(0)

        dom_interfaces = []
        xml = minidom.parseString(raw_xml)
        interfaceTypes = xml.getElementsByTagName('interface')
        for interfaceType in interfaceTypes:
            dom_interface = {}
            dom_interface['type'] = interfaceType.getAttribute('type')

            interfaceNodes = interfaceType.childNodes
            for interfaceNode in interfaceNodes:
                if interfaceNode.nodeName[0:1] != '#':

                    for attr in interfaceNode.attributes.keys():
                        dom_interface[interfaceNode.nodeName + ' ' + interfaceNode.attributes[attr].name] = interfaceNode.attributes[attr].value

            dom_interfaces.append(dom_interface)

        domain['interfaces'] = dom_interfaces
        domains.append(domain)

    return domains

def print_interface_info(domain_data):

    for d in domain_data:
        print 'Domain Name: ' + d['name']
        print '  Interfaces:'
        for i in d['interfaces']:
            print "    MAC Address: " + i['mac address'] + " (" + i['alias name'] + ")"
        print " "



def main():
    """
    The command entry point.
    """

    URI = "qemu:///system"

    options = get_options()

    if options.server:
        URI = "qemu+ssh://" + options.username + "@" + options.server + "/system"

    #Connect to Hypervisor
    conn = libvirt.openReadOnly(URI)
    if conn == None:
        print 'Failed to open connection to the hypervisor.'
        sys.exit(1)

    active_hosts = conn.listDomainsID()

    print_interface_info(construct_interface_structure(active_hosts, conn))

    conn.close()


## MAIN
if __name__ == "__main__":
    main()
