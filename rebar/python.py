'''
Functions related to python and python tools
'''
from cuisine import package_ensure, sudo
from misc import distro_family

def install_python_dev():
    '''
    Install python development libraries
    '''
    family = distro_family()
    if family == 'debian':
        package_ensure('python-dev')
    elif family == 'redhat':
        package_ensure('python-devel')

def install_pip():
    '''
    Install pip package manager. Will install on CentOS > 6.
    '''
    family = distro_family()
    if family == 'debian':
        package_ensure('python-pip')
    elif family == 'redhat':
        package_ensure('python-pip')
        sudo('pip-python install --upgrade pip')
