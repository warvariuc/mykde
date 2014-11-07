#!/usr/bin/env python3
__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

# tested with these versions
REQUIRED_PYTHON_VERSION = '3.4'
REQUIRED_UBUNTU_VERSION = '14.10'


import os
import shlex
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)


def error(title, message):
    """Show error message dialog and exit.
    """
    print('%s: %s' % (title, message))
    subprocess.call(shlex.split('xmessage -center -title') + [title, message])
    sys.exit(1)


if sys.version < REQUIRED_PYTHON_VERSION:
    error('Bad Python version', 'Python %s or newer required (you are using %s).'
          % (REQUIRED_PYTHON_VERSION, sys.version.split(' ')[0]))

if os.geteuid() == 0:  # root privileges
    error('Root detected', 'Do not run this script as root.\n'
          'Run it as the user in whose session you want to run the actions.')

# the distributor's ID
distro_id = subprocess.check_output(shlex.split(
    'lsb_release --short --id')).decode().strip().lower()
if distro_id != 'ubuntu':
    error('Unsupported Linux distribution',
          'You distribution (%s) is not supported.\n'
          'Are you rinning Kubuntu?.' % distro_id)

# the release number of the currently installed distribution
distro_release_id = subprocess.check_output(shlex.split(
    'lsb_release --short --release')).decode().strip()
if distro_id < REQUIRED_UBUNTU_VERSION:
    error('Wrong release', 'Need Kubuntu %s or later.' % REQUIRED_UBUNTU_VERSION)

try:
    import PyQt4, PyKDE4
except ImportError:
    error('PyQt4/PyKDE4 missing',
          'PyQt4/PyKDE4 libraries were not found on your system.\n'
          'These modules are necessary for this application.\n'
          'Are you running Kubuntu?')


import mykde.main
import packages


mykde.main.main(packages)
