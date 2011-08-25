# (c) Zygmunt Krynicki 2008
# Licensed under GPL, see COPYING for the whole text

import gettext
import locale
import sys
import gettext

_ = gettext.translation("command-not-found", fallback=True).ugettext


def crash_guard(callback, bug_report_url, version):
    """ Calls callback and catches all exceptions.
    When something bad happens prints a long error message
    with bug report information and exits the program"""
    try:
        try:
            callback()
        except Exception, ex:
            print >> sys.stderr, _("Sorry, command-not-found has crashed! Please file a bug report at:")
            print >> sys.stderr, bug_report_url
            print >> sys.stderr, _("Please include the following information with the report:")
            print >> sys.stderr
            print >> sys.stderr, _("command-not-found version: %s") % version
            print >> sys.stderr, _("Python version: %d.%d.%d %s %d") % sys.version_info
            try:
                import subprocess
                subprocess.call(["lsb_release", "-i", "-d", "-r", "-c"], stdout=sys.stderr)
            except (ImportError, OSError):
                pass
            print >> sys.stderr, _("Exception information:")
            print >> sys.stderr
            print >> sys.stderr, ex
            try:
                import traceback
                traceback.print_exc()
            except ImportError:
                pass
    finally:
        sys.exit(127)


__all__ = ["gettext_wrapper", "crash_guard"]
