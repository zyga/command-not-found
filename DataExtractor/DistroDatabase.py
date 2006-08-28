#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import os, os.path
from SmartFile import smart_file

class CommandInfo:
    def __init__(self, name, package):
        self.name = name
        self.package = package
    def __str__(self):
        return "command from package '%s': '%s'" % (self.package, self.name)
    def __repr__(self):
        return "%s::%s" % (self.package, self.name)
    def __eq__(self, other):
        return (self.name, self.package) == (other.name, other.package)
    def __hash__(self):
        return hash((self.name, self.package))

class SymlinkInfo:
    def __init__(self, name, target, package):
        self.name = name
        self.target = target
        self.package = package
    def __str__(self):
        return "symlink from package '%s': '%s' -> '%s'" % (self.package, self.name, self.target)
    def __repr__(self):
        return "%s::%s->%s" % (self.package, self.name, self.target)
    def __eq__(self, other):
        return (self.name, self.target, self.package) == (other.name, self.target, other.package)
    def __hash__(self):
        return hash((self.name, self.target, self.package))

class AggregatedCommandInfo:
    def __init__(self, name, packages):
        self.name = name
        self.packages = packages
    def __str__(self):
        return "command '%s' can be found in packages: %s" % (self.name, ", ".join(self.packages))
    def __repr__(self):
        return "%s::%s" % (self.package, self.name)
    def __eq__(self, other):
        return (self.name, self.packages) == (other.name, other.packages)
    def __hash__(self):
        return hash((self.name, self.packages))

class CommandDatabaseReader:
    def __init__(self, path):
        self.path = path
    def __iter__(self):
        for line in smart_file(self.path):
            (package, command) = line.strip().split("|")
            yield CommandInfo(command, package)

class SymlinkDatabaseReader:
    def __init__(self, path):
        self.path = path
    def __iter__(self):
        for line in smart_file(self.path):
            (deb_path, package, link_path, link_dest) = line.strip().split("|")
            if link_dest.startswith("/"):
                # Absolute link okay :-)
                pass
            else:
                # Relative links are based on the directory component of link_name
                link_dest = os.path.sep.join([os.path.dirname(link_path), link_dest])
            # collapse '..'
            link_dest = os.path.normpath(link_dest)
            yield SymlinkInfo(link_path, link_dest, package)

class SymlinkDatabase:
    def __init__(self, distro):
        self.distro = distro
    def __iter__(self):
        for filename in os.listdir(os.path.sep.join(["distro.d", self.distro, "links.d"])):
            pathname = os.path.sep.join(["distro.d", self.distro, "links.d", filename])
            print "Processing: %s" % pathname
            for info in SymlinkDatabaseReader(pathname):
                yield info

class CommandDatabase:
    def __init__(self, distro):
        self.distro = distro
    def __iter__(self):
        for filename in os.listdir(os.path.sep.join(["distro.d", self.distro, "xbits.d"])):
            pathname = os.path.sep.join(["distro.d", self.distro, "xbits.d", filename])
            print "Processing: %s" % pathname
            for info in CommandDatabaseReader(pathname):
                yield info

class AggregatedCommandDatabase:
    def __init__(self, distro):
        self.distro = distro
    def __iter__(self):
        def infoToDictOfSets(infos):
            result = dict()
            for info in infos:
                if not result.has_key(info.name):
                    result[info.name] = set()
                result[info.name].add(info)
            return result
        # group by command name
        commands = infoToDictOfSets(CommandDatabase(self.distro))
        symlinks = infoToDictOfSets(SymlinkDatabase(self.distro))
        print "Analyzing..."
        aggregated = dict()
        for name in commands:
            bn = os.path.basename(name)
            if not aggregated.has_key(bn):
                aggregated[bn] = set()
            aggregated[bn] |= commands[name]
        for name in symlinks:
            info_seen = set()
            info_to_check = set()
            info_to_check |= symlinks[name]
            assert info_to_check == symlinks[name]
            while len(info_to_check) > 0:
                info = info_to_check.pop()
                if info in info_seen:
                    continue
                info_seen.add(info)
                if symlinks.has_key(info.target):
                    print "S2S: %s::%s->(%s)" % (info.package, info.name, set([target_info.target for target_info in symlinks[info.target]]))
                    info_to_check.update(set([SymlinkInfo(info.name, target_info.target, info.package) for target_info in symlinks[info.target]]))
            for info in info_to_check:
                if info.target in commands:
                    print "S2B: %s::%s->%s" % (info.package, info.name, info.target)
                    bn = os.path.basename(info.name)
                    if not aggregated.has_key(bn):
                        aggregated[bn] = set()
                    aggregated[bn].add(info)
        print "Writing..."
        for name in aggregated:
            yield AggregatedCommandInfo(name, set([info.package for info in aggregated[name]]))
