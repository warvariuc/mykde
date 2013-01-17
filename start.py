#!/usr/bin/env python3
__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os
import sys
import subprocess


cur_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(cur_dir)


def show_error(title, message):
    """Show error message dialog and exit.
    """
    print(title)
    print(message)
    subprocess.call(['xmessage', '-center', '-title', title, message])
    sys.exit(1)


python_required_version = '3.2'  # tested with this version
if sys.version < python_required_version:
    show_error('Bad Python version', 'Python %s or newer required (you are using %s).'
               % (python_required_version, sys.version.split(' ')[0]))

if os.geteuid() == 0:  # root privileges
    show_error('Root detected', 'Do not run this script as root.\n'
          'Run it as the user in whose session you want to proceed with the actions.')

# the distributor's ID
distro_id = subprocess.check_output(['lsb_release', '--short', '--id'])
distro_id = distro_id.decode().strip().lower()
if distro_id != 'ubuntu':
    show_error('Wrong distro', 'Ubuntu not found:\n%s.' % distro_id)

# the release number of the currently installed distribution
distro_release_id = subprocess.check_output(['lsb_release', '--short', '--release'])
distro_release_id = distro_release_id.decode().strip()
if distro_id < '12.10':
    show_error('Wrong release', 'Need Ubuntu 12.10 or later.')

try:
    import PyQt4
    import PyKDE4
except ImportError:
    show_error('PyQt4/PyKDE4', 'PyQt4/PyKDE4 libraries are not available')


import packages
from mykde.main import main


main(packages)
