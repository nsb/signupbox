# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
from fabric.api import *

def staging():
    """
    staging env
    """
    env.hosts = ['niels@signupbox.com']
    env.directory = '~/webapps/signupbox3/'
    env.activate = 'workon signupbox3'
    env.settings = 'settings_local'

## set staging as default
staging()

def test():
    """
    run tests before deploy
    """
    local('python manage.py test signupbox quickpay objperms --settings=' + env.settings, capture=False)

def update():
    """
    update src from svn
    """
    with cd(env.directory + 'src'):
        run('git pull')

def reload():
    """
    make the webserver reload the code
    """
    with cd(env.directory):
        run('apache2/bin/restart')

def install_requirements():
    """
    install requirements
    """
    with cd(env.directory + 'src'):
        virtualenv('pip install -q -r requirements.txt')

def migrate():
    """
    migrate the database
    """
    with cd(env.directory + 'src'):
        #virtualenv('python manage.py migrate --settings=' + env.settings)
        virtualenv('python manage.py syncdb --noinput --settings=' + env.settings)

def deploy():
    """
    deploy
    """
    test()
    update()
    install_requirements()
    migrate()
    reload()

def virtualenv(command):
    """
    run command in a virtual env
    """
    run(env.activate + ' && ' + command)
