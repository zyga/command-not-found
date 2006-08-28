#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import os, os.path, sys, dbm

input_file = sys.argv[1]
key = sys.argv[2]
if input_file.endswith(".db"):
    input_file = input_file[:-3]
db = dbm.open(input_file, "r");
print db[key].split("|")
