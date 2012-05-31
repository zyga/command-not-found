#!/usr/bin/env python

from distutils.core import setup
from DistUtilsExtra.command import (build_extra, build_i18n)
import glob
import os

setup(
    name='command-not-found',
    version='0.2.44',
    packages=['CommandNotFound'],
    scripts=['command-not-found'],
    cmdclass={"build": build_extra.build_extra,
                "build_i18n": build_i18n.build_i18n,
                },
    data_files=[
        ('share/command-not-found/programs.d', glob.glob("data/programs.d/*")),
        ('share/command-not-found/', ['data/priority.txt']),
        ('../etc', ['bash_command_not_found', 'zsh_command_not_found']),
    ])
