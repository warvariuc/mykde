#!/usr/bin/env python3
__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

PYTHON_REQUIRED_VERSION = '3.4'  # tested with this version

import os
import sys
import subprocess
import shlex


cur_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(cur_dir)


def error(title, message):
    """Show error message dialog and exit.
    """
    print('%s: %s' % (title, message))
    subprocess.call(shlex.split('xmessage -center -title') + [title, message])
    sys.exit(1)


if sys.version < PYTHON_REQUIRED_VERSION:
    error('Bad Python version', 'Python %s or newer required (you are using %s).'
          % (PYTHON_REQUIRED_VERSION, sys.version.split(' ')[0]))

if os.geteuid() == 0:  # root privileges
    error('Root detected', 'Do not run this script as root.\n'
          'Run it as the user in whose session you want to proceed with the actions.')

# the distributor's ID
distro_id = subprocess.check_output(shlex.split('lsb_release --short --id'))
distro_id = distro_id.decode().strip().lower()
if distro_id != 'ubuntu':
    error('Wrong distro', 'Ubuntu not found:\n%s.' % distro_id)

# the release number of the currently installed distribution
distro_release_id = subprocess.check_output(shlex.split('lsb_release --short --release'))
distro_release_id = distro_release_id.decode().strip()
if distro_id < '14.04':
    error('Wrong release', 'Need Ubuntu 14.04 or later.')

try:
    import PyQt4, PyKDE4
except ImportError:
    error('PyQt4/PyKDE4 missing',
          'PyQt4/PyKDE4 libraries are not available on your system.\n'
          'These modules are necessary for this program to function.')


from mykde.main import main
import packages


main(packages)
