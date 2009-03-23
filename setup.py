#!/usr/bin/env python

from distutils.core import setup
import glob
import os

GETTEXT_NAME="command-not-found"
I18NFILES = []
for filepath in glob.glob("po/mo/*/LC_MESSAGES/*.mo"):
    lang = filepath[len("po/mo/"):]
    targetpath = os.path.dirname(os.path.join("share/locale",lang))
    I18NFILES.append((targetpath, [filepath]))

# HACK: make sure that the mo files are generated and up-to-date
# os.system("cd po && make update-po")

setup(name='command-not-found',
        version='0.1',
        packages=['CommandNotFound'],
        scripts=['command-not-found'],
        data_files=[
        ('share/command-not-found/programs.d', glob.glob("data/programs.d/*")),
        ('share/command-not-found/', ['data/priority.txt']),  
        ('../etc', ['bash_command_not_found', 'zsh_command_not_found']),
        ]+I18NFILES,
        )


