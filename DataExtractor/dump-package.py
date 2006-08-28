#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import sys
import os.path
import DebPackage

for arg in sys.argv[1:]:
  try:
    pkg = DebPackage.DebPackage(arg)
    for info in pkg.files:
      print "%s /%s" % (info.unix_mode(), info.name)
  except IOError, e:
    sys.stderr.write("Unable to process '%s': %s\n" % (arg, e))
