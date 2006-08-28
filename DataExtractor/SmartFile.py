#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import sys, bz2, gzip

def smart_file(filename, mode="r"):
    if filename.endswith(".gz"):
        return gzip.GzipFile(filename, mode)
    elif filename.endswith(".bz2"):
        return bz2.BZ2File(filename, mode)
    else:
        return file(filename, mode)
