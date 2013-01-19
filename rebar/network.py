'''
Network related functions
'''
from fabric.api import env
from cuisine import file_write, run
from fabric.colors import green
from misc import distro_family

def resolv_conf():
    '''
    Add our nameserver to /etc/resolv.conf
    '''
    print(green("Setting up nameserver %s on %s" \
                    % (env.nameserver, env.host_string)))
    file_write("/etc/resolv.conf", "nameserver %s" % env.nameserver)

def disable_ipv6():
    '''
    Disable IPv6.
    '''
    family = distro_family()
    print(green("Disabling IPv6"))
    if family == 'debian':
        run('echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6')
    elif family == 'redhat':
        run('echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6')
        run('echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6')
        
