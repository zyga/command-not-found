#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import sys
import os.path
import DebPackage

def filter(info):
    # lib*.so* are usualy +x so we'll exclude them
    return isinstance(info, DebPackage.FileInfo) and info.is_executable() and os.path.basename(info.name)[:3] != "lib"
    

for filename in sys.argv[1:]:
    try:
        pkg = DebPackage.DebPackage(filename)
        for info in [ info for info in pkg.files if filter(info)]:
            print "%s|%s|/%s" % (filename, pkg.getPackageName(), info.name)
    except IOError, e:
        print >> sys.stderr, "Unable to process '%s': %s" % (filename, e)
    except SystemError, e:
        print >> sys.stderr, "Unable to process '%s': %s" % (filename, e)
      
