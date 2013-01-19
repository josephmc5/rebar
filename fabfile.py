from rebar.rebar import system_bootstrap, system_setup
from rebar.datacenters import *
from fabric.colors import green

def help():
    '''
    Print help
    '''
    print(green("Server Setup Functions"))
    help_server()
