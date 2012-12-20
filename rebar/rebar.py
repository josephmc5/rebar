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

from fabric.api import *
from cuisine import *
from fabric.colors import red, green, blue
from fabric.contrib.files import contains, append
from fabric.context_managers import *
from rackspace import *

"""
Fabric script to create and manage servers.
"""

def help_server():
    print("Available functions:")
    print("     add_user(username,password)")
    print("     cmd(command to run)")
    print("     add_user(username, password)")
    print("     add_key(username)")
    print("     passwd(username, password)")
    print("     install_hg()")

def boot_server(name):
    '''
    Boot a new server and change the root password.
    '''

    cs = get_cs()
    s = create_server(cs, name, settings.CLOUDSERVERS_IMAGE_TEMPLATE, 256)

    wait_for_server(cs, s, with_url_ping=False)

    print '%s: Server IP is %s (private: %s)' % (s.id, s.public_ip, s.private_ip)

    # small delay to allow the server to fully boot up
    sleep(60)

    env.host_string = s.private_ip
    env.user = 'root'
    env.password = password_gen()
    print "Password: %s" % env.password

    change_password(s, env.password)
    print "Waiting a bit for the password to change..."
    sleep(30)

def cmd(cmd):
    '''
    fab HOST_NAME cmd:UNIX_COMMAND
    e.g. fab vagrant cmd:uptime
    '''

    run(cmd)


def add_user(username, password):
    '''
    Add new user.
    '''

    mode_sudo()
    if not user_check(username):
        print('#' * 60)
        print(green("Creating user %s" % username))
        print('#' * 60)
        user_create(username, shell='/bin/bash')
        passwd(username, password)
        add_key(username)    
        sudo_group(username)
        print('#' * 60)
        print(green("Added user %s to %s" % (username, env.host)))
        print('#' * 60)
    else:
        print('#' * 60)
        print(red("User already exists"))
        print('#' * 60)

def sudo_group(username):
    '''
    Add user to sudo group
    '''

    print('#' * 60)
    print(green("Adding %s to sudo group" % username))
    print('#' * 60)
    redhat_release = '/etc/redhat-release'
    if file_exists(redhat_release):
        group = 'wheel'
    else:
        group = 'sudo'
    group_user_add(group, username)

def sudo_nopasswd(username):
    '''
    Add user to nopasswd sudo group. This will
    allow the user to sudo without a password.
    '''

    if not contains('/etc/sudoers','%s  ALL=(ALL) NOPASSWD:ALL' % username, use_sudo=True):
        append('/etc/sudoers','%s  ALL=(ALL) NOPASSWD:ALL' % username, use_sudo=True)
 
def passwd(username,newpasswd):
    '''
    Change password for user.
    '''

    sudo('echo "{username}:{password}" | chpasswd'.format(username=username, password=newpasswd))

def puppetlabs_apt():
    '''
    Add the puppetlabs repo.
    '''

    print('#' * 60)
    print(green("Setting up Puppetlabs Apt Repository"))
    print('#' * 60)
    apt_config = 'puppetlabs-release-lucid.deb'
    sudo('wget -O ~/ http://apt.puppetlabs.com/%s' % apt_config)
    sudo('dpkg -i ~/%s' % apt_config)
    sudo('rm -f ~/%s')
    package_update()

def install_puppet():
    '''
    Install the puppet agent and add configuration for connection
    to puppet master.
    '''

    puppetlabs_apt()
    print('#' * 60)
    print(green("Installing Puppet"))
    print('#' * 60)
    package_ensure('puppet')
    run('echo "[agent]" >> /etc/puppet/puppet.conf')
    run("echo -n 'server = %s' >> /etc/puppet/puppet.conf" % env.puppet_server)

def install_puppetmaster():
    '''
    Install puppet master. It will be the apache passenger configuration
    because puppet by itself can't handle any kind of scale.
    '''

    puppetlabs_apt()
    print('#' * 60)
    print(green("Installing Puppet Master"))
    print('#' * 60)
    package_ensure('puppetmaster-passenger')

def run_puppet():
    '''
    Run the puppet agent.
    '''

    print('#' * 60)
    print(green("Running Puppet on %s" % env.host))
    print('#' * 60)
    run('/usr/bin/puppet agent --no-daemonize --no-listen --onetime')

def resolve_conf():
    '''
    Setup nameserver configuration. This makes the puppet master
    connection much easier.
    '''

    print('#' * 60)
    print(green("Setting up nameserver on %s" % env.host))
    print('#' * 60)
    file_write("/etc/resolv.conf", "nameserver %s" % env.nameserver)

def setup_puppetmaster():
    '''
    Setup puppetmaster with modules and correct host.
    '''

    #run("sed -i 's//%s/g' /etc/puppet/puppet.conf" % env.puppet_server)
    run('/etc/init.d/apache2 restart')
    run_puppet()

def puppetmaster_bootstrap():
    '''
    Setup the puppet master.
    '''

    resolve_conf()
    install_puppetmaster()
    setup_puppetmaster()

def system_bootstrap(name):
    '''
    The fuction you will call from fabric to bring it all together
    and setup a machine.
    '''

    boot_server(name)
    resolve_conf()
    package_update()
    package_upgrade()
    install_puppet()
    user_create('%s','%s',gid=27,shell='/bin/bash' % (env.first_user, env.first_password))
    run_puppet()
