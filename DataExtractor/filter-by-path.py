#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import os, os.path, sys

stuff=set()

path_bits = os.getenv("PATH").split(":")
for line in [line.strip() for line in file(sys.argv[1])]:
    try:
        (path_to_deb, package, command) = map(str.strip, line.split(":", 2))
    except ValueError, e:
        print "problem with '%s': %s" % (line, e)
    if os.path.dirname(command) in path_bits:
        stuff.add((package, command))

for foo in stuff:
    print "%s|%s" % foo
