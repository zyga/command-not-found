#!/usr/bin/env python

import sys
import apt
import apt_pkg
import re
import os
import string

if len(sys.argv) < 2:
    print "need argument"
    sys.exit(1)

apt_pkg.Config.Set("Dir::Etc","./lists/")
apt_pkg.Config.Set("Dir::state",".")

cache = apt.Cache(apt.progress.OpTextProgress())
try:
	prog = apt.progress.TextFetchProgress() 
except:
	prog = apt.progress.FetchProgress()

cache.update(prog)

cache.open(apt.progress.OpTextProgress())

out = open(sys.argv[1]+".distro_filtered","w")
for line in file(sys.argv[1]):
    try:
        (path_to_deb, package, command) = string.split(line,"|",2)
    except ValueError, e:
        print "problem with '%s': %s" % (line, e)

    deb = os.path.basename(path_to_deb)
    m = re.match("(.*)_(.*)_.*.deb",deb)
    pkgname = m.group(1)
    ver = m.group(2)
    if cache.has_key(pkgname):
        if cache[pkgname].candidateVersion == ver:
            out.write(line)
