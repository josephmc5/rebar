#Derived from https://raw.github.com/nicholaskuechler/autoscale-rackspacecloud-fabric-celery/master/fabfile.py
import os
import sys
import datetime
import base64
import cloudservers
#import cloudlb
import urllib2
import time
import uuid
import settings
import datacenters

from time import sleep
import string
import random
from fabric.api import env

def password_gen(size=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def get_cs():
    return cloudservers.CloudServers(env.CLOUDSERVERS_USERNAME, env.CLOUDSERVERS_API_KEY)

def _get_server_image(cs, image_name):
    i = cs.images.find(name=image_name)
    return i

def _get_flavor(cs, ram_size):
    return cs.flavors.find(ram=ram_size)

def _get_file_contents(file_name):
    contents = open(file_name, 'r').read()
    return contents

def _reboot_server(cs, s):
    """ 
    reboot a cloud server 
    """
    
    s.reboot()
    sleep(90)
    return True

def create_server(cs, name, image_name, ram_size):
    '''
    Create server given a cloudserver object, name of the image,
    and instance size.
    '''

    print 'Creating server %s' % name
    
    image = _get_server_image(cs, image_name)
    if not image:
        raise Exception('Could not get server image "%s"' % image_name)
    
    flavor = _get_flavor(cs, ram_size)
    if not flavor:
        raise Exception('Could not get flavor with %s ram' % ram_size)
    
    server = cs.servers.create(
        name,
        image,
        flavor,
    )

    return server

def change_password(s, password):
    s.update(password=password)

def wait_for_server(cs, s, with_url_ping=False):
    while s.status != 'ACTIVE':
        sleep(30)
        s = cs.servers.get(s.id)
        print 'Status of ID %s: %s (%s%%)' % (s.id, s.status, s.progress)
    
    if with_url_ping:
        # Wait for a response
        url = 'http://%s/index.html' % s.public_ip
        tries = 0
        while True:
            try:
                print 'Attempting to connect to %s' % url
                urllib2.urlopen(url)
                print 'ping success, returning'
                break
            except urllib2.HTTPError, e:
                print e
                if e.code == 401:
                    print '401 not authorized'
                elif e.code == 404:
                    print '404 not found... waiting...'
                elif e.code == 503:
                    print '503 service unavailable'
                else:
                    print 'unknown error: %s' % e
                sleep(30)
            except urllib2.URLError, u:
                print u
                print 'Connection refused for now...'
                sleep(30)
            
            tries += 1
            if tries > 20: # 10 minutes
                raise Exception('URL ping timed out')