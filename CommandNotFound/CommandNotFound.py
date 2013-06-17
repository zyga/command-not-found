# (c) Zygmunt Krynicki 2005, 2006, 2007, 2008
# Licensed under GPL, see COPYING for the whole text

from __future__ import print_function

try:
    import dbm.gnu as gdbm
except ImportError:
    import gdbm
import gettext
import grp
import os
import os.path
import posix
import sys
import subprocess

from functools import cmp_to_key

if sys.version >= "3":
    _gettext_method = "gettext"
else:
    _gettext_method = "ugettext"
_ = getattr(gettext.translation("command-not-found", fallback=True), _gettext_method)


class BinaryDatabase(object):

    def __init__(self, filename):
        self.db = None
        if filename.endswith(".db"):
            try:
                self.db = gdbm.open(filename, "r")
            except gdbm.error as err:
                print("Unable to open binary database %s: %s" % (filename, err), file=sys.stderr)

    def lookup(self, key):
        if not isinstance(key, bytes):
            # gdbm does not entirely handle Unicode strings; "self.db[key]"
            # works, but "key in self.db" does not.
            key = key.encode('utf-8')
        if self.db and key in self.db:
            return self.db[key].decode('utf-8')
        else:
            return None


class FlatDatabase(object):

    def __init__(self, filename):
        self.rows = []
        with open(filename) as dbfile:
            for line in (line.strip() for line in dbfile):
                self.rows.append(line.split("|"))

    def lookup(self, column, text):
        result = []
        for row in self.rows:
            if row[column] == text:
                result.append(row)
        return result

    def createColumnByCallback(self, cb, column):
        for row in self.rows:
            row.append(cb(row[column]))

    def lookupWithCallback(self, column, cb, text):
        result = []
        for row in self.rows:
            if cb(row[column], text):
                result.append(row)
        return result


class ProgramDatabase(object):

    (PACKAGE, BASENAME_PATH) = range(2)

    def __init__(self, filename):
        basename = os.path.basename(filename)
        (self.arch, self.component) = basename.split(".")[0].split("-")
        self.db = BinaryDatabase(filename)

    def lookup(self, command):
        result = self.db.lookup(command)
        if result:
            return result.split("|")
        else:
            return []


def similar_words(word):
    """
    return a set with spelling1 distance alternative spellings

    based on http://norvig.com/spell-correct.html
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz-_0123456789'
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts = [a + c + b     for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


class CommandNotFound(object):

    programs_dir = "programs.d"

    prefixes = (
        "/bin",
        "/usr/bin",
        "/usr/local/bin",
        "/sbin",
        "/usr/sbin",
        "/usr/local/sbin",
        "/usr/games")

    def __init__(self, data_dir="/usr/share/command-not-found"):
        self.programs = []
        self.priority_overrides = []
        p = os.path.join(data_dir, "priority.txt")
        if os.path.exists(p):
            with open(p) as priority_file:
                self.priority_overrides = [line.strip() for line in priority_file]
        self.components = ['main', 'universe', 'contrib', 'restricted',
                           'non-free', 'multiverse']
        self.components.reverse()
        self.sources_list = self._getSourcesList()
        for filename in os.listdir(os.path.sep.join([data_dir, self.programs_dir])):
            self.programs.append(ProgramDatabase(os.path.sep.join([data_dir, self.programs_dir, filename])))
        try:
            self.user_can_sudo = grp.getgrnam("admin")[2] in posix.getgroups() or grp.getgrnam("sudo")[2] in posix.getgroups()
        except KeyError:
            self.user_can_sudo = False

    def print_spelling_suggestion(self, word, min_len=3, max_len=15):
        " try to correct the spelling "
        if len(word) < min_len:
            return
        possible_alternatives = []
        for w in similar_words(word):
            packages = self.getPackages(w)
            for (package, comp) in packages:
                possible_alternatives.append((w, package, comp))
        if len(possible_alternatives) > max_len:
            print(_("No command '%s' found, but there are %s similar ones") % (word, len(possible_alternatives)), file=sys.stderr)
        elif len(possible_alternatives) > 0:
            print(_("No command '%s' found, did you mean:") % word, file=sys.stderr)
            for (w, p, c) in possible_alternatives:
                print(_(" Command '%s' from package '%s' (%s)") % (w, p, c), file=sys.stderr)

    def getPackages(self, command):
        result = set()
        for db in self.programs:
            result.update([(pkg, db.component) for pkg in db.lookup(command)])
        return list(result)

    def getBlacklist(self):
        try:
            with open(os.sep.join((os.getenv("HOME", "/root"), ".command-not-found.blacklist"))) as blacklist:
                return [line.strip() for line in blacklist if line.strip() != ""]
        except IOError:
            return []

    def _getSourcesList(self):
        try:
            import apt_pkg
            from aptsources.sourceslist import SourcesList
            apt_pkg.init()
        except (SystemError, ImportError):
            return []
        sources_list = set([])
        # The matcher parses info files from
        # /usr/share/python-apt/templates/
        # But we don't use the calculated data, skip it
        for source in SourcesList(withMatcher=False):
            if not source.disabled and not source.invalid:
                for component in source.comps:
                    sources_list.add(component)
        return sources_list

    def sortByComponent(self, x, y):
        # check overrides
        if (x[0] in self.priority_overrides and
            y[0] in self.priority_overrides):
            # both have priority, do normal sorting
            pass
        elif x[0] in self.priority_overrides:
            return -1
        elif y[0] in self.priority_overrides:
            return 1
        # component sorting
        try:
            xidx = self.components.index(x[1])
        except:
            xidx = -1
        try:
            yidx = self.components.index(y[1])
        except:
            xidx = -1
        # http://python3porting.com/differences.html#comparisons
        return (yidx - xidx) or ((x > y) - (x < y))

    def install_prompt(self, package_name):
        if not "COMMAND_NOT_FOUND_INSTALL_PROMPT" in os.environ:
            return
        if package_name:
            prompt = _("Do you want to install it? (N/y)")
            if sys.version >= '3':
                answer = input(prompt)
            else:
                answer = raw_input(prompt)
                if sys.stdin.encoding and isinstance(answer, str):
                    # Decode the answer so that we get an unicode value
                    answer = answer.decode(sys.stdin.encoding)
            if answer.lower() == _("y"):
                if posix.geteuid() == 0:
                    command_prefix = ""
                else:
                    command_prefix = "sudo "
                install_command = "%sapt-get install %s" % (command_prefix, package_name)
                print("%s" % install_command, file=sys.stdout)
                subprocess.call(install_command.split(), shell=False)

    def advise(self, command, ignore_installed=False):
        " give advice where to find the given command to stderr "
        def _in_prefix(prefix, command):
            " helper that returns if a command is found in the given prefix "
            return (os.path.exists(os.path.join(prefix, command))
                    and not os.path.isdir(os.path.join(prefix, command)))

        if command.startswith("/"):
            if os.path.exists(command):
                prefixes = [os.path.dirname(command)]
            else:
                prefixes = []
        else:
            prefixes = [prefix for prefix in self.prefixes if _in_prefix(prefix, command)]

        # check if we have it in a common prefix that may not be in the PATH
        if prefixes and not ignore_installed:
            if len(prefixes) == 1:
                print(_("Command '%(command)s' is available in '%(place)s'") % {"command": command, "place": os.path.join(prefixes[0], command)}, file=sys.stderr)
            else:
                print(_("Command '%(command)s' is available in the following places") % {"command": command}, file=sys.stderr)
                for prefix in prefixes:
                    print(" * %s" % os.path.join(prefix, command), file=sys.stderr)
            missing = list(set(prefixes) - set(os.getenv("PATH", "").split(":")))
            if len(missing) > 0:
                print(_("The command could not be located because '%s' is not included in the PATH environment variable.") % ":".join(missing), file=sys.stderr)
                if "sbin" in ":".join(missing):
                    print(_("This is most likely caused by the lack of administrative privileges associated with your user account."), file=sys.stderr)
            return False

        # do not give advice if we are in a situation where apt-get
        # or aptitude are not available (LP: #394843)
        if not (os.path.exists("/usr/bin/apt-get") or
                os.path.exists("/usr/bin/aptitude")):
            return False

        if command in self.getBlacklist():
            return False
        packages = self.getPackages(command)
        if len(packages) == 0:
            self.print_spelling_suggestion(command)
        elif len(packages) == 1:
            print(_("The program '%s' is currently not installed. ") % command, end="", file=sys.stderr)
            if posix.geteuid() == 0:
                print(_("You can install it by typing:"), file=sys.stderr)
                print("apt-get install %s" % packages[0][0], file=sys.stderr)
                self.install_prompt(packages[0][0])
            elif self.user_can_sudo:
                print(_("You can install it by typing:"), file=sys.stderr)
                print("sudo apt-get install %s" % packages[0][0], file=sys.stderr)
                self.install_prompt(packages[0][0])
            else:
                print(_("To run '%(command)s' please ask your administrator to install the package '%(package)s'") % {'command': command, 'package': packages[0][0]}, file=sys.stderr)
            if not packages[0][1] in self.sources_list:
                print(_("You will have to enable the component called '%s'") % packages[0][1], file=sys.stderr)
        elif len(packages) > 1:
            packages.sort(key=cmp_to_key(self.sortByComponent))
            print(_("The program '%s' can be found in the following packages:") % command, file=sys.stderr)
            for package in packages:
                if package[1] in self.sources_list:
                    print(" * %s" % package[0], file=sys.stderr)
                else:
                    print(" * %s" % package[0] + " (" + _("You will have to enable component called '%s'") % package[1] + ")", file=sys.stderr)
            if posix.geteuid() == 0:
                print(_("Try: %s <selected package>") % "apt-get install", file=sys.stderr)
            elif self.user_can_sudo:
                print(_("Try: %s <selected package>") % "sudo apt-get install", file=sys.stderr)
            else:
                print(_("Ask your administrator to install one of them"), file=sys.stderr)
        return len(packages) > 0
