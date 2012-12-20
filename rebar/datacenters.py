from fabric.api import env
from fabric.contrib import console

#Specify datacenters here

def DC_testing():
    env.puppet_server = 'puppet.dev'
    env.nameserver = 
    env.CLOUDSERVERS_USERNAME = 
    env.CLOUDSERVERS_API_KEY = 
    env.CLOUDSERVERS_DATA_CENTER = "ord"

def DC_production():
    env.puppet_server = 'puppet.prod'
    env.nameserver = 
    env.CLOUDSERVERS_USERNAME = =
    env.CLOUDSERVERS_API_KEY = =
    env.CLOUDSERVERS_DATA_CENTER = "ord"