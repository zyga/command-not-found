# (c) Zygmunt Krynicki 2005, 2006
# Licensed under GPL, see COPYING for the whole text

import sys, os, os.path, dbm, posix, grp
from gettext import gettext as _


def _guessUserLocale():
    msg = os.getenv("LC_MESSAGES") or os.getenv("LANG")
    if msg:
        return msg.split("_", 1)[0]
    else:
        return None

class BinaryDatabase:
    def __init__(self, filename):
        self.db = None
        if filename.endswith(".db"):
            try:
                self.db = dbm.open(filename[:-3], "r")
            except dbm.error, err:
                print >>sys.stderr, "Unable to open binary database %s: %s", filename, err
    def lookup(self, key):
        if self.db and self.db.has_key(key):
            return self.db[key]
        else:
            return None

class FlatDatabase:
    def __init__(self, filename):
        self.rows = []
        dbfile = file(filename)
        for line in (line.strip() for line in dbfile):
            self.rows.append(line.split("|"))
        dbfile.close()
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
            if cb(row[column],text):
                result.append(row)
        return result

class ProgramDatabase:
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

class Suggestion:
    def __init__(self, text, programs):
        self.text = text.replace("\\n", "\n")
        self.programs = programs

class SuggestionDatabase:
    (COMMAND, TEXT, PROGRAMS) = range(3)
    (COMMAND, LOCALIZED_TEXT) = range(2)
    def __init__(self, filename):
        self.db = FlatDatabase(filename)
        locale_database = "%s.%s" % (filename, _guessUserLocale())
        if os.path.exists(locale_database):
            self.db_locale = FlatDatabase(locale_database)
        else:
            self.db_locale = None
    def _localizedMsg(self,command):
        result = self.db_locale.lookup(self.COMMAND, command)
        if len(result) == 1:
            return result[0][self.LOCALIZED_TEXT]
        else:
            return None
    def lookup(self, command):
        def magicSplit(string, separator):
            if string=="":
                return []
            else:
                return string.split(separator)
        if self.db_locale:
            return [ Suggestion(self._localizedMsg(command) or row[self.TEXT], magicSplit(row[self.PROGRAMS], ",")) for row in self.db.lookup(self.COMMAND, command) ]
        else:
            return [ Suggestion(row[self.TEXT], magicSplit(row[self.PROGRAMS], ",")) for row in self.db.lookup(self.COMMAND, command) ]

class CommandNotFound:
    programs_dir = "programs.d"
    suggestions_dir = "suggestions.d"
    def __init__(self, data_dir=os.sep.join(('/','usr','share','command-not-found'))):
        self.programs = []
        self.suggestions = []
        for filename in os.listdir(os.path.sep.join([data_dir, self.programs_dir])):
            self.programs.append(ProgramDatabase(os.path.sep.join([data_dir, self.programs_dir, filename])))
        try:
            self.user_can_sudo = grp.getgrnam("admin")[2] in posix.getgroups()
        except KeyError:
            self.user_can_sudo = False
    def getSuggestions(self, command):
        result = []
        for db in self.suggestions:
            result.extend(db.lookup(command))
        return result
    def getPackages(self, command):
        result = set()
        for db in self.programs:
            result.update([(pkg,db.component) for pkg in db.lookup(command)])
        return list(result)
    def getBlacklist(self):
        try:
            blacklist = file(os.sep.join((os.getenv("HOME"), ".command-not-found.blacklist")))
            return [line.strip() for line in blacklist if line.strip() != ""]
        except IOError:
            return []
        else:
            blacklist.close()
    def advise(self, command):
        if command in self.getBlacklist():
            return False
        suggestions = self.getSuggestions(command)
        packages = self.getPackages(command)
        ok = len(packages) > 0 or len(suggestions) > 0
        for suggestion in suggestions:
            print suggestion.text
            if len(suggestion.programs):
                print _("Ubuntu has the following similar programs")
                for program in suggestion.programs:
                    print " * '%s'" % program
        if len(packages) == 1:
            print _("The program '%s' is currently not installed. ") % command,
            if posix.geteuid() == 0:
                print _("You can install it by typing:")
                print "apt-get install %s" %  packages[0][0]
            elif self.user_can_sudo:
                print _("You can install it by typing:")                
                print "sudo apt-get install %s" %  packages[0][0]
            else:
                print _("To run '%(command)s' please ask your administrator to install the package '%(package)s'") % {'command': command, 'package': packages[0][0]}
            if packages[0][1] != "main":
                print _("Make sure you have the '%s' component enabled") % packages[0][1]
        elif len(packages) > 1:
            print _("The program '%s' can be found in the following packages:") % command
            for package in packages:
                print " * %s" % package[0]
            if posix.geteuid() == 0:
                print _("Try: %s <selected package>") % "apt-get install"
            elif self.user_can_sudo:
                print _("Try: %s <selected package>") % "sudo apt-get install"
            else:
                print _("Ask your administrator to install one of them")
            if package[1] != "main":
                print _("Make sure you have the '%s' component enabled") % package[1]
        return ok
