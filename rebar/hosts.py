from fabric.api import sudo, env, run, local
from fabric.contrib.files import contains,append,comment
from fabric.context_managers import cd
from cuisine import *

from rebar import *

def help_server():
    print(green("Available functions:"))
    print("     add_user(username,password)")
    print("     cmd(command to run)")
    print("     add_user(username, password)") 
    print("     add_ssh_key(username)") 
    print("     passwd(username, password)") 
    print("     install_hg()")


def default():
    env.name = 'prod'
    env.user = 
    env.hosts = ['myhost'] 

    sudo_nopasswd('joe')
    comment('/etc/ssh/sshd_config','^PasswordAuthentication', use_sudo=True)
    sudo('service ssh reload')