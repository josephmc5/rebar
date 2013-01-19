"""
Copyright (C) 2012  CashStar Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Rebar
-----
Author: Joe McWilliams <jmcwilliams@cashstar.com>
Location: https://github.com/CashStar/rebar/

"""
from fabric.api import hide, env
from cuisine import (package_update, package_upgrade)
from fabric.colors import red, green, blue
from rackspace import boot_server
from puppet import (puppetlabs_repo, install_puppet, config_puppet,
                    first_run_puppet)
from misc import (set_pkg_os, create_default_user,
                    create_deployment_user, print_root_password,
                    centos_fixes)
from network import resolv_conf, disable_ipv6

def help_server():
    '''
    Print help.
    '''
    print("Available functions:")
    print("     system_bootstrap(name, image, size)")
    print("     system_setup(ip)")


def system_setup(name):
    '''
    Setup an existing server that has been booted. User will
    be prompted for root password.
    '''
    env.host_string = name
    env.user = 'root'
    resolv_conf()
    set_pkg_os()
    puppetlabs_repo()
    disable_ipv6()
    centos_fixes()
    print(green("Updating system"))
    print(blue("This can take a few minutes. Hang tight..."))
    with hide('stdout'):
        package_update()
        package_upgrade()
    install_puppet()
    config_puppet()
    create_default_user()
    create_deployment_user()
    first_run_puppet()

def system_bootstrap(name, *args):
    '''
    Boot and setup a server
    '''
    boot_server(name, *args)
    system_setup(env.private_ip)
    print_root_password()
    
def boot_datacenter():
    '''
    Boot entire datacenter based on all_servers dict set by the datacenter function in datacenters.py.
    '''
    for role in env.all_servers:
        print(green("Building %s servers" % role))
        i = 0
        while i < env.all_servers[role]['quantity']:
            server = "%s%s.%s" % (role, i+1, env.domain)
            system_bootstrap(server, env.all_servers[role]['template'], \
                                env.all_servers[role]['size'])
            i += 1
