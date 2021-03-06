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

from charms.reactive import when_not, set_state
from charmhelpers import fetch
from charmhelpers.core import (
    hookenv,
    host
)


_USERNAME = 'ubuntu'
_HOME = os.path.join('/home', _USERNAME)
_DOTFILES_REPO = 'https://github.com/elopio/dotfiles'


@when_not('remote-comms.installed')
def install_remote_comms():
    os.makedirs(os.path.join(_HOME, 'workspace'), exist_ok=True)
    _setup_locale()
    _install_email()
    _install_chat()
    _install_social()
    _install_utils()
    _install_dotfiles()
    host.chownr(
        _HOME, owner=_USERNAME, group=_USERNAME,
        follow_links=True, chowntopdir=True)
    set_state('remote-comms.installed')


def _setup_locale():
    subprocess.check_call(['locale-gen', 'en_US.UTF-8'])
    os.environ['LC_ALL'] = 'en_US.UTF-8'


def _install_email():
    # imap synchronization.
    _install_offlineimap()
    # smtp client.
    fetch.apt_install('msmtp')
    # mail reader.
    fetch.apt_install('mutt')
    # html to text.
    fetch.apt_install('links')


def _install_offlineimap():
    fetch.apt_install('offlineimap')
    os.makedirs(os.path.join(_HOME, 'Mail'), exist_ok=True)
    # Run offlineimap every three minutes.
    cron = '*/3 * * * * {} offlineimap -u quiet\n'.format(_USERNAME).encode(
        'utf-8')
    host.write_file(os.path.join('/etc', 'cron.d', 'offlineimap'), cron)


def _install_chat():
    fetch.apt_install('weechat')


def _install_social():
    subprocess.check_call(['pip', 'install', 'rainbowstream'])


def _install_utils():
    fetch.apt_install('emacs-nox')
    fetch.apt_install('byobu')
    _install_mosh()


def _install_mosh():
    fetch.apt_install('mosh')
    hookenv.open_port('60000-61000', 'UDP')


def _install_dotfiles():
    fetch.apt_install('git')
    dotfiles_workspace = os.path.join(_HOME, 'workspace', 'dotfiles')
    subprocess.check_call(['git', 'clone', _DOTFILES_REPO, dotfiles_workspace])
    subprocess.check_call(
        ['env', 'HOME=' + _HOME,
         os.path.join(dotfiles_workspace, 'install.sh'),
         'comms'])
