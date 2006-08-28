#!/usr/bin/env python

import sys, DebPackage

for filename in sys.argv[1:]:
    try:
        pkg = DebPackage.DebPackage(filename)
        contents = pkg.getControlFile("postinst")
        if contents == None:
            continue
        for line in contents.replace("\\\n","").split("\n"):
            words = line.split()
            if "update-alternatives" in words and "--install" in words:
                offset = words.index("--install")
                link = words[offset + 1]
                target = words[offset + 3]
                print "%s|%s|%s|%s" % (filename, pkg.getPackageName(), link, target)
    except IOError, e:
        print >> sys.stderr, "Unable to process '%s': %s" % (filename, e)
    except SystemError, e:
        print >> sys.stderr, "Unable to process '%s': %s" % (filename, e)
