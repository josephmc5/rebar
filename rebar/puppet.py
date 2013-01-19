'''
Functions for installing, configuring, and running puppet
'''
from fabric.api import env
from cuisine import (run, sudo, package_ensure, file_read,
                    text_ensure_line, file_write, file_exists)
from fabric.colors import red, green, blue
from fabric.context_managers import cd, settings
from misc import get_hostname, distro_family
from network import resolv_conf
from config import DEFAULT_USER

def puppetlabs_repo():
    '''
    Setup puppetlabs apt/yum repo.
    '''
    family = distro_family()
    if family == 'debian':
        apt_config = '/etc/apt/sources.list.d/puppetlabs.list'
        if file_exists(apt_config) != True:
            print(green("Setting up Puppetlabs Apt Repository"))
            with cd('/tmp'):
                sudo('wget http://apt.puppetlabs.com/\
puppetlabs-release-precise.deb')
                sudo('dpkg -i puppetlabs-release-precise.deb')
    elif family == 'redhat':
        yum_config = '/etc/yum.repos.d/puppetlabs.repo'
        if file_exists(yum_config) != True:
            print(green("Setting up Puppetlabs Yum Repository"))
            sudo('rpm -ivh http://yum.puppetlabs.com/\
el/6/products/i386/puppetlabs-release-6-6.noarch.rpm')

def install_puppet():
    '''
    Install puppet client.
    '''
    print(green("Installing Puppet"))
    package_ensure('puppet')

def config_puppet():
    '''
    Ensure the server directive is in puppet.conf
    '''
    print(green("Writing puppet config file"))
    config_file = '/etc/puppet/puppet.conf'
    line1 = "[agent]"
    line2 = "server = %s" % env.puppet_server
    config_content = file_read(config_file)
    updated_config = text_ensure_line(config_content, line1, line2)
    file_write(config_file, updated_config)

def install_puppetmaster():
    '''
    Install the Apache Passenger puppet master package
    '''
    print(green("Installing Puppet Master"))
    package_ensure('puppetmaster-passenger')

def puppet_cert_sign():
    '''
    Connet to the puppet master and sign the client cert.
    '''
    client = get_hostname()
    print(green("Signing cert for %s on %s" % (client, env.puppet_server)))
    with settings(user=DEFAULT_USER, host_string=env.puppet_server):
        sudo("puppet cert sign %s" % client)

def first_run_puppet():
    '''
    First run on puppet. We do this three times.
        1. Generate and send the cert to the master
        2. Apply config with default environment in puppet.conf
        3. Run again after environment directive has been changed
            in puppet.conf
    '''
    print(green("First run of puppet on %s" % env.host_string))
    run('/usr/bin/puppet agent -t', warn_only=True)
    puppet_cert_sign()
    print(green("Running Puppet on %s" % env.host_string))
    run('/usr/bin/puppet agent -t', warn_only=True)
    print(green("Running Puppet one more time on %s" % env.host_string))
    print(blue("We need to mamke sure this server is \
setup to the right environment"))
    run('/usr/bin/puppet agent -t', warn_only=True)

def setup_puppetmaster():
    '''
    Setup a puppet master.
    '''
    run('/etc/init.d/apache2 restart')
    first_run_puppet()

def puppetmaster_bootstrap():
    '''
    Setup a puppet master
    '''
    resolv_conf()
    install_puppetmaster()
    setup_puppetmaster()
