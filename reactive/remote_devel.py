#!/usr/bin/python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016 Leonardo Arias
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess

from charms.reactive import when, when_not, set_state
from charmhelpers import fetch
from charmhelpers.core import host


_USERNAME = 'ubuntu'
_HOME = os.path.join('/home', _USERNAME)
_DOTFILES_REPO = 'https://github.com/elopio/dotfiles'


@when_not('remote-devel.installed')
def install_remote_devel():
    os.makedirs(os.path.join(_HOME, 'workspace'))
    install_email()
    install_dotfiles()
    host.chownr(
        _HOME, owner=_USERNAME, group=_USERNAME,
        follow_links=True, chowntopdir=True)
    set_state('remote-devel.installed')

def install_email():
    fetch.apt_install('offlineimap')
    os.makedirs(os.path.join(_HOME, 'Mail'))
    # Run offlineimap every three minutes.
    cron = '*/3 * * * * su -u {} -c "offlineimap -u quiet"'.format(_USERNAME)
    host.write_file(os.path.join('/etc', 'cron.d', 'offlineimap'))

def install_dotfiles():
    fetch.apt_install('git')
    dotfiles_workspace = os.path.join(_HOME, 'workspace', 'dotfiles')
    subprocess.check_call(['git', 'clone', _DOTFILES_REPO, dotfiles_workspace])
    subprocess.check_call(
        ['env', 'HOME=' + _HOME,
         os.path.join(dotfiles_workspace, 'install.sh')])
