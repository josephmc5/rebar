'''
Hosts are specified here so we can manage them.
'''
from fabric.api import sudo, env, run
from fabric.contrib.files import comment

from misc import sudo_nopasswd

def default():
    '''
    example host
    '''
    env.name = 'prod'
    env.user = 'root'
    env.hosts = ['myhost'] 

    sudo_nopasswd('joe')
    comment('/etc/ssh/sshd_config', '^PasswordAuthentication', use_sudo=True)
    sudo('service ssh reload')
