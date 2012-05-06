# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

from __future__ import print_function

import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)

import apt
import apt_inst
import apt_pkg


class GenericFileInfo(object):

    BASE_STICKY = 8
    BASE_READ = 4
    BASE_WRITE = 2
    BASE_EXEC = 1

    O_STICKY = BASE_STICKY << 0
    O_READ = BASE_READ << 0
    O_WRITE = BASE_WRITE << 0
    O_EXEC = BASE_EXEC << 0

    G_STICKY = BASE_STICKY << 3
    G_READ = BASE_READ << 3
    G_WRITE = BASE_WRITE << 3
    G_EXEC = BASE_EXEC << 3

    U_STICKY = BASE_STICKY << 6
    U_READ = BASE_READ << 6
    U_WRITE = BASE_WRITE << 6
    U_EXEC = BASE_EXEC << 6

    STICKY = O_STICKY | G_STICKY | U_STICKY
    READ = O_READ | G_READ | U_READ
    WRITE = O_WRITE | G_WRITE | U_WRITE
    EXEC = O_EXEC | G_EXEC | U_EXEC

    def __init__(self, name, mode, uid, gid, size, mtime):
        self.name = name
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.size = size
        self.mtime = mtime

    def is_executable(self):
        return self.mode & self.EXEC

    def is_readable(self):
        return self.mode & self.READ

    def is_writable(self):
        return self.mode & self.WRITE

    def unix_mode(self):
        """ Returns a ls -l like mode string. """
        def mode_str(mode):
            out = ""
            if mode & self.BASE_EXEC:
                out += 'x'
            else:
                out += '-'
            if mode & self.BASE_READ:
                out += 'r'
            else:
                out += '-'
            if mode & self.BASE_WRITE:
                out += 'w'
            else:
                out += '-'
            return out

        def kind_str():
            if isinstance(self, FileInfo) or isinstance(self, HardLinkInfo):
                return '-'
            elif isinstance(self, DirectoryInfo):
                return 'd'
            elif isinstance(self, SymbolicLinkInfo):
                return 'l'
            else:
                return '?'

        return "%s%s%s%s" % (kind_str(self), mode_str(self.mode >> 6 & 7), mode_str(self.mode >> 3 & 7), mode_str(self.mode & 7))


class FileInfo(GenericFileInfo):

    def __init__(self, name, mode, uid, gid, size, mtime):
        GenericFileInfo.__init__(self, name, mode, uid, gid, size, mtime)


class DirectoryInfo(GenericFileInfo):

    def __init__(self, name, mode, uid, gid, size, mtime):
        GenericFileInfo.__init__(self, name, mode, uid, gid, size, mtime)


class LinkInfo(GenericFileInfo):

    (SOFT, HARD) = list(range(2))

    def __init__(self, name, target, mode, uid, gid, size, mtime):
        GenericFileInfo.__init__(self, name, mode, uid, gid, size, mtime)
        self.target = target

    def get_link_type(self):
        raise NotImplemented


class SymbolicLinkInfo(LinkInfo):

    def __init__(self, name, target, mode, uid, gid, size, mtime):
        LinkInfo.__init__(self, name, target, mode, uid, gid, size, mtime)

    def get_link_type(self):
        return self.SOFT


class HardLinkInfo(LinkInfo):

    def __init__(self, name, target, mode, uid, gid, size, mtime):
        LinkInfo.__init__(self, name, target, mode, uid, gid, size, mtime)

    def get_link_type(self):
        return self.HARD


class DeviceInfo(GenericFileInfo):

    (CHAR, BLOCK) = list(range(2))

    def __init__(self, name, mode, uid, gid, size, mtime, major, minor):
        GenericFileInfo.__init__(self, name, mode, uid, gid, size, mtime)
        self.major = major
        self.minor = minor

    def get_device_type(self):
        pass


class CharDeviceInfo(DeviceInfo):

    def __init__(self, name, mode, uid, gid, size, mtime, major, minor):
        DeviceInfo.__init__(self, name, mode, uid, gid, size, mtime, major, minor)

    def get_device_type(self):
        return self.CHAR


class BlockDeviceInfo(DeviceInfo):

    def __init__(self, name, mode, uid, gid, size, mtime, major, minor):
        DeviceInfo.__init__(self, name, mode, uid, gid, size, mtime, major, minor)

    def get_device_type(self):
        return self.BLOCK


class FifoInfo(GenericFileInfo):
    def __init__(self, name, mode, uid, gid, size, mtime):
        GenericFileInfo.__init__(self, name, mode, uid, gid, size, mtime)


def load(filename):
    return DebPackage(filename)


class DebPackage(object):

    def __init__(self, filename):
        self.filename = filename
        self._sections = apt_pkg.TagSection(self.getControlFile("control"))

    arch = property(lambda self: self._sections["Architecture"], None, None, "Architecture the package is compiled for")

    name = property(lambda self: self._sections["Package"], None, None, "Cannonical package name")

    def getControlFile(self, name):
        """ Returns the contents of given file in debian/ or None if it does not exist """
        try:
            return apt_inst.DebFile(self.filename).control.extractdata(name)
        except LookupError:
            return None

    @property
    def items(self):
        """ Return the list of items in the package.
        Each file is represented by an instance of  FileInfo """
        items = []

        def extract_cb(member, data):
            if member.isfile():
                items.append(FileInfo(member.name, member.mode, member.uid, member.gid, member.size, member.mtime))
            elif member.isdir():
                items.append(DirectoryInfo(member.name, member.mode, member.uid, member.gid, member.size, member.mtime))
            elif member.issym():
                items.append(SymbolicLinkInfo(member.name, member.linkname, member.mode, member.uid, member.gid, member.size, member.mtime))
            elif member.islnk():
                items.append(HardLinkInfo(member.name, member.linkname, member.mode, member.uid, member.gid, member.size, member.mtime))
            elif member.isfifo():
                items.append(FifoInfo(member.name, member.mode, member.uid, member.gid, member.size, member.mtime))
            else:
                print("unsupported member type: %s" % member)
        apt_inst.DebFile(self.filename).data.go(extract_cb)
        return items
