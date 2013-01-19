'''
Define datacenters.
'''
from fabric.api import env

def DC_testing():
    env.puppet_server = 'puppet.dev'
    env.nameserver = '8.8.8.8'
    env.CLOUDSERVERS_USERNAME = 
    env.CLOUDSERVERS_API_KEY = 
    env.CLOUDSERVERS_DATA_CENTER = "ord"

def DC_production():
    env.puppet_server = 'puppet.prod'
    env.nameserver = '8.8.8.8'
    env.CLOUDSERVERS_USERNAME =
    env.CLOUDSERVERS_API_KEY =
    env.CLOUDSERVERS_DATA_CENTER = "ord"
    env.all_servers = { 'web':
                            { 'template': 'Ubuntu 10.04 LTS',
                              'size': 1024,
                              'quantity': 2 },
                        'services':
                            { 'template': 'Ubuntu 10.04 LTS',
                              'size': 512,
                              'quantity': 1 },
                        'memcached':
                            { 'template': 'Ubuntu 10.04 LTS',
                              'size': 256,
                              'quantity': 1 },
                        'db':
                            { 'template': 'Ubuntu 10.04 LTS',
                              'size': 256,
                              'quantity': 1 }
                      }
