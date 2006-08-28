#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import os, dbm
from DistroDatabase import *

if __name__ == "__main__":
    for distro in os.listdir("distro.d"):
        db = dbm.open(distro, "n")
        for info in AggregatedCommandDatabase(distro):
            db[info.name] = '|'.join(info.packages)
        db.close()
#        file("%s-links.dump" % distro, "w").writelines(["%s\n" % info for info in SymlinkDatabase(distro)])
#        file("%s-commands.dump" % distro, "w").writelines(["%s\n" % info for info in CommandDatabase(distro)])
#        file("%s-all-commands.dump" % distro, "w").writelines(["%s|%s\n" % (info.name, ':'.join(info.packages)) for info in AggregatedCommandDatabase(distro)])
