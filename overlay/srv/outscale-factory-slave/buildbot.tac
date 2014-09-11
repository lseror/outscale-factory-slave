# -*- python -*-
# ex: set syntax=python:

import os

from twisted.application import service
from buildslave.bot import BuildSlave


def _load_slave_config_from_instance_userdata():
    global buildmaster_host
    global slavename
    global passwd

    import boto.utils

    (buildmaster_host,
    slavename,
    passwd) = boto.utils.get_instance_userdata().split('\n')


def _load_slave_config():
    global buildmaster_host
    global slavename
    global passwd

    import json

    config_filename = "/etc/outscale-factory-slave/slave.json"
    if not os.path.exists(config_filename):
        _load_slave_config_from_instance_userdata()
        return

    with open(config_filename) as f:
        config = json.load(f)
    if config['ec2_slave']:
        _load_slave_config_from_instance_userdata()
        return
    buildmaster_host = config['buildmaster_host']
    slavename = config['slavename']
    passwd = config['passwd']


basedir = r'/srv/outscale-factory-slave'
rotateLength = 10000000
maxRotatedFiles = 10

# if this is a relocatable tac file, get the directory containing the TAC
if basedir == '.':
    import os.path
    basedir = os.path.abspath(os.path.dirname(__file__))

# note: this line is matched against to check that this is a buildslave
# directory; do not edit it.
application = service.Application('buildslave')

try:
  from twisted.python.logfile import LogFile
  from twisted.python.log import ILogObserver, FileLogObserver
  logfile = LogFile.fromFullPath(os.path.join(basedir, "twistd.log"), rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
  application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
except ImportError:
  # probably not yet twisted 8.2.0 and beyond, can't set log yet
  pass

port = 9989
keepalive = 600
usepty = 0
umask = None
maxdelay = 300

_load_slave_config()

s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask, maxdelay=maxdelay)
s.setServiceParent(application)

