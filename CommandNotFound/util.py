# (c) Zygmunt Krynicki 2008
# Licensed under GPL, see COPYING for the whole text

import sys

def no_gettext_for_you(message):
    """This function is used instead of gettext when there are some locale problems"""
    return message

def setup_locale():
    import locale
    try:
        import gettext
        locale.getpreferredencoding()
        gettext.bindtextdomain("command-not-found", "/usr/share/locale")
        gettext.textdomain("command-not-found")
        gettext.install("command-not-found", unicode=True)
        return gettext.lgettext
    except locale.Error:
        #print "Warning: python was unable to setup locale!"
        #print "Internationalizatio features will not be enabled."
        return no_gettext_for_you

_ = gettext_wrapper = setup_locale()

def crash_guard(callback, bug_report_url, version):
    """ Calls callback and catches all exceptions.
    When something bad happens prints a long error message
    with bug report information and exits the program"""
    try:
        try:
            callback()
        except Exception, ex:
            print >>sys.stderr, _("Sorry, command-not-found has crashed! Please file a bug report at:")
            print >>sys.stderr, bug_report_url
            print >>sys.stderr, _("Please include the following information with the report:")
            print >>sys.stderr
            print >>sys.stderr, _("command-not-found version: %s") % version
            print >>sys.stderr, _("Python version: %d.%d.%d %s %d") % sys.version_info
            try:
                import subprocess
                subprocess.call(["lsb_release", "-i", "-d", "-r", "-c"], stdout=sys.stderr)
            except (ImportError, OSError):
                pass
            print >>sys.stderr, _("Exception information:")
            print >>sys.stderr
            print >>sys.stderr, ex
            try:
                import traceback
                traceback.print_exc()
            except ImportError:
                pass
    finally:
        sys.exit(127)

__all__ = ["gettext_wrapper", "crash_guard"]
