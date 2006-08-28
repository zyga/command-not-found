#! /usr/bin/env python
#

import os
import os.path
import tarfile
import sys
import apt
import apt_pkg
import apt_inst
import os.path
import re
import tempfile
import subprocess
import string
import shutil
import urllib
import logging
import apt_inst

import dbm

# init
PATH=["/usr/local/sbin",
      "/usr/local/bin",
      "/usr/sbin",
      "/usr/bin",
      "/sbin",
      "/bin",
      "/usr/bin/X11",
      "/usr/games"]

name2pkg = {}

def get_component(pkgname):
  pkg = cache[pkgname]
  if "/" in pkg.section:
    return pkg.section.split("/")[0]
  return "main"

def processDeb(debPath, pkgname, section,
               outputdir=os.path.join(os.getcwd(), "menu-data")):
  """ extract the desktop file and the icons from a deb """
  logging.debug("processing: %s" % debPath)
  
  def cb(what, name, link, mode, uid, gid, size, mtime, maj, min):
    if what == "DIR":
      return
    for p in PATH:
      if name.startswith(p):
	# strip away the path information
	name = os.path.basename(name)
        if not name in name2pkg.keys():
          name2pkg[name] = []
        if not pkgname in name2pkg[name]:
          name2pkg[name].append(pkgname)
          logging.info("found %s in %s" % (name, pkgname))
  try:
	apt_inst.debExtract(open(debPath), cb, "data.tar.gz")
  except:
	pass


#------------------------------- BOILERPLATE ----------------

def inspectDeb(filename):
  """ check if the deb is interessting for us (our arch etc) """
  #logging.debug("inspectDeb '%s'"% filename)
  m = re.match(".*/(.*)_(.*)_(.*).deb", filename)
  pkgname = m.group(1)
  ver = m.group(2)
  # fix the quoting
  ver = urllib.unquote(ver)
  pkgarch = m.group(3)
  
  # not for our arch
  if pkgarch != "all" and arch != pkgarch:
    #logging.debug("Skipping because of not-for-us arch '%s'" % pkgarch)
    return
    
  # check if the deb is in the current distro at all
  candVer = "xxx"
  if cache.has_key(pkgname):
    candVer = cache[pkgname].candidateVersion
    # strip the epoch
    if candVer and ":" in candVer:
      candVer = candVer.split(":")[1]
  if candVer != ver:
    #logging.debug("Skipping because '%s' it's not in our distro release"%pkgname)
    return

  # valid deb
  section = cache[pkgname].section
  if not "/" in section:
    component = "main"
  else:
    component = section[0:section.find("/")]
  #print "%s in: %s" % (filename, component)
  logging.debug("Found interessting deb '%s' in section '%s'" % (filename, component))

  # found somethat worth looking at
  processDeb(filename, pkgname, component)

def dir_walk(cache, dirname, names):
  #print "Looking at: %s" % dirname
  #logging.debug("Entering dir: '%s' " % dirname)
  for filename in names:
    if filename.endswith(".deb"):
      inspectDeb(dirname+"/"+filename)



if __name__ == "__main__":

  logging.basicConfig(level=logging.DEBUG,
                      filename="data-extract.log",
                      format='%(asctime)s %(levelname)s %(message)s',
                      filemode='w')

  try:
    pooldir = sys.argv[1]
  except:
    print "Usage: getMenuData.py pooldir"
    sys.exit()

    
  for arch in ["i386"]:

    apt_pkg.Config.Set("APT::Architecture",arch)
    apt_pkg.Config.Set("Dir::state","./apt/")
    apt_pkg.Config.Set("Dir::Etc","./apt")
    cache = apt.Cache(apt.progress.OpTextProgress())

    try:
      os.makedirs("apt/lists/partial")
    except OSError:
      pass

    logging.info("Starting extraction in %s for %s" % (pooldir,arch))
    try:
      prog = apt.progress.TextFetchProgress() 
    except:
      prog = apt.progress.FetchProgress()

    # update the cache
    cache.update(prog)
    cache.open(apt.progress.OpTextProgress())


    # now do the postmans walk!
    os.path.walk(pooldir, dir_walk, cache)

    
  # finished, write out the info  
  db = dbm.open("edgy","n")
  for name in name2pkg:
    db[name] = "|".join(name2pkg[name])
  db.close()

  print name2pkg
