#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import sys
import os.path
import DebPackage

for filename in sys.argv[1:]:
    try:
        pkg = DebPackage.DebPackage(filename)
        for info in [ info for info in pkg.files if isinstance (info, DebPackage.SymbolicLinkInfo)]:
            print "%s|%s|/%s|%s" % (filename, pkg.getPackageName(), info.name, info.link)
    except IOError, e:
        print >> sys.stderr, "Unable to process '%s': %s" % (filename, e)
    except SystemError, e:
        print >> sys.stderr, "Unable to process '%s': %s" % (filename, e)
