#!/usr/bin/python
'''Set Buildbot master host, slavename and password
'''

import os
import subprocess

import json

from dialog_wrapper import Dialog

CONFIG_FILENAME = '/etc/outscale-factory-slave/slave.json'


def get_config():
    dlg = Dialog('Outscale Buildbot Slave - First boot configuration')

    is_plain = dlg.yesno('Build Slave Type', 'What type of slave must run on this system?',
                         yes_label='Plain Build Slave',
                         no_label='EC2 Build Slave')
    if not is_plain:
        return None
    buildmaster_host = dlg.get_input('Buildmaster Host', 'Enter the IP address of the buildmaster host')
    slavename = dlg.get_input('Slave Name', 'Enter the name of this slave, as defined in the buildmaster configuration')
    passwd = dlg.get_password('Slave Password', 'Enter the password of this slave, as defined in the buildmaster configuration')

    return {
        'buildmaster_host': buildmaster_host,
        'slavename': slavename,
        'passwd': passwd,
    }


def save_config(config):
    config_dirname = os.path.dirname(CONFIG_FILENAME)
    if not os.path.isdir(config_dirname):
        os.makedirs(config_dirname)
    with open(CONFIG_FILENAME, 'w') as f:
        json.dump(config, f, indent=4, separators=(',', ': '))
    os.chmod(CONFIG_FILENAME, 0600)


def main():
    config = get_config()
    if config is None:
        if os.path.exists(CONFIG_FILENAME):
            os.rename(CONFIG_FILENAME, CONFIG_FILENAME + '.old')
    else:
        save_config(config)
    subprocess.call(['invoke-rc.d', 'buildslave', 'restart'])


if __name__ == '__main__':
    main()

