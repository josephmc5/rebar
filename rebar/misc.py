'''
Miscellaneous functions
'''
from fabric.api import run, env, hide
from fabric.colors import red, green, blue
from fabric.contrib.files import contains, append, exists
from fabric.context_managers import settings
from config import DEPLOYMENT_PASSWORD, DEFAULT_USER, DEFAULT_PASSWORD
from cuisine import (package_ensure, mode_sudo, user_check,
    user_create, sudo, group_user_add, group_ensure,
    user_create, select_package)

def get_hostname():
    '''
    Return hostname of host.
    '''
    return run('hostname')

def package_exists(package):
    '''
    Check to see if a package exists.
    '''
    family = distro_family()
    if family == 'redhat':
        if run("rpm -qa|grep %s" % package, quiet=True).succeeded:
            return True
    elif family == 'debian':
        if run("dpkg -l|grep %s" % package, quiet=True).succeeded:
            return True
    
#has_binary(), distro_name() and distro_family() from 
#https://github.com/alekibango/patchwork/blob/ \
#fb740a7a67e0c051e038962bbc5cff500e4d03c8/patchwork/info.py
def has_binary(name, runner=run):
    '''
    Check if binary exists in path on system
    '''
    with settings(hide('everything'), warn_only=True):
        return runner("which %s" % name).succeeded

def distro_name():
    """
    Return simple Linux distribution name identifier, e.g. ``"fedora"``.

    Uses files like ``/etc/os-release`` (or ``/etc/*-release``) and
    tools like ``/etc/issue``, and ``lsb_release``, trying to identify
    short id of the system. Examples:

    * ``fedora``
    * ``rhel``
    * ``centos``
    * ``ubuntu``
    * ``debian``
    * ``other``
    """
    with hide('running', 'stdout'):
        if has_binary('lsb_release'):
            distro_id = run('lsb_release -s -i').strip().lower()
            if distro_id:
                return distro_id

        if exists('/etc/lsb-release'):
            distro_id = run('''awk -F '=' '$1 == "DISTRIB_ID" \
                {print $2; exit }' \
                /etc/lsb-release ''',
            shell=False).strip().lower()
            if distro_id:
                return distro_id

        if exists('/etc/os-release'):
            distro_id = run('''awk -F '=' '$1 == "ID" \
                {print $2; exit }' \
                /etc/os-release''',
            shell=False).strip().lower()
            if distro_id:
                return distro_id

    # and now the fallback method (guess by existing files)
    sentinel_files = (
        ('fedora', ('fedora-release',)),
        ('centos', ('centos-release',)),
        ('debian', ('debian_version',)),
        ('gentoo', ('gentoo-release',)),
    )

    for name, sentinels in sentinel_files:
        for sentinel in sentinels:
            if exists('/etc/%s' % sentinel):
                return name
    return "other"


def distro_family():
    """
    Returns basic "family" ID for the remote system's distribution.

    Currently, options include:

    * ``debian``
    * ``redhat``

    If the system falls outside these categories, its specific family or
    release name will be returned instead.
    """
    families = {
        'debian': "debian ubuntu".split(),
        'redhat': "rhel centos fedora".split()
    }
    distro = distro_name()
    for family, members in families.iteritems():
        if distro in members:
            return family
    return distro

def set_pkg_os():
    '''
    Set the OS for cuisine to do packaging
    '''
    family = distro_family()
    if family == 'debian':
        select_package("apt")
    elif family == 'redhat':
        select_package("yum")
    
def sudo_group(username):
    '''
    Add a user to the sudo group.
    '''
    print(green("Adding %s to sudo group" % username))
    group_ensure('sudo')
    group_user_add('sudo', username)

def add_user(username, password):
    '''
    Add user.
    '''
    mode_sudo()
    if not user_check(username):
        print(green("Creating user %s" % username))
        user_create(username, shell='/bin/bash')
        passwd(username, password)
        sudo_group(username)
        print(green("Added user %s to %s" % (username, env.host_string)))
    else:
        print(red("User already exists"))

def sudo_nopasswd(username):
    '''
    Add user to nopasswd sudo group.
    '''
    if not contains('/etc/sudoers','%s  ALL=(ALL) NOPASSWD:ALL' \
                     % username, use_sudo=True):
        append('/etc/sudoers','%s  ALL=(ALL) NOPASSWD:ALL' \
                % username, use_sudo=True)
 
def passwd(username, newpasswd):
    '''
    Change user password.
    '''
    sudo('echo "{username}:{password}" | chpasswd'.format( \
            username=username, password=newpasswd))

def install_hg():
    '''
    Install mercurial.
    '''
    package_ensure('mercurial')

def centos_fixes():
    '''
    Things that prevent us from installing on CentOS from the get go.
    *mysql-libs percona clash
    '''
    if distro_family() == 'redhat':
        if package_exists('mysql-libs'):
            print(green("Removing mysql-libs"))
            run('rpm --nodeps -e mysql-libs')

def create_default_user():
    '''
    Create a default user so we can still login after puppet runs 
    and disables root login
    '''
    if user_check(DEFAULT_USER) == None:
        print(green("Creating default user %s" % DEFAULT_USER))
        user_create(DEFAULT_USER, DEFAULT_PASSWORD, uid=503, shell='/bin/bash')
        print(green("Adding %s to sudo group" % DEFAULT_USER))
        sudo_group(DEFAULT_USER)
    else:
        print(green("Default user %s already exists" % DEFAULT_USER))

def create_deployment_user():
    '''
    Create the deployment user
    '''
    if user_check('deployment') == None:
        print(green("Creating deployment user"))
        user_create('deployment', DEPLOYMENT_PASSWORD, uid=502, \
                        shell='/bin/bash', home='/opt/apps')
    else:
        print(red("Deployment user already exists"))

def print_root_password():
    '''
    Print the root password that was assigned to env.root_password.
    '''
    print(green("Password for root: %s" % env.root_password))
