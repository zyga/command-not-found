#! /usr/bin/env python
#
# (c) 2008 Canonical, GPL
# Authors:
#  Michael Vogt

import apt
import apt_pkg
import sys

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "need scan.data argument"
        sys.exit(1)

    scandata = sys.argv[1]
    apt_pkg.Config.Set("APT::Get::List-Cleanup", "false")
    for arch in ("i386","amd64"):
        print "Starting verification for '%s'" % arch
        apt_pkg.Config.Set("APT::Architecture",arch)
        cache = apt.Cache(rootdir="./apt/")
        cache.update()
        cache.open(apt.progress.OpProgress())
        for line in open(scandata):
            (march, comp, pkg, bin) = line.split("|")
            if march != arch:
                continue
            # check if package is in cache
            if not pkg in cache:
                print "ERROR: '%s' is not in cache" % pkg
                continue
            # check if the component is correct
            if not "/" in cache[pkg].section:
                realcomp = "main"
            else:
                realcomp = cache[pkg].section.split("/")[0]
            if comp != realcomp:
                print "ERROR: '%s' is in wrong component (claims '%s' but is in '%s'" % (pkg, comp, realcomp)
        print "done\n"
