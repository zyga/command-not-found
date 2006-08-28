#!/usr/bin/env python
# (c) Zygmunt Krynicki 2005,
# Licensed under GPL, see COPYING for the whole text

import sys

"""
RELEASE should be set for end user:
    TODO is silently ignored
    FIXME triggers a CodeMaturityViolationError
    XXX is silently ignored

DEVEL should be set during debugging/development phase:
    TODO triggers error message
    FIXME triggers error message
    XXX triggers erorr message
"""
(RELEASE, DEVEL) = range(2)

class CodeMaturityViolationError(Exception):
    def __init__(self, message, code_stamp):
        self.message = message
        self.code_stamp = code_stamp
    def __str__(self):
        return "Code maturity violation in %s:%d: %s" % (self.code_stamp.filename, self.code_stamp.lineno, self.message)

class MessageTrigger:
    def __init__(self, kind, depth):
        self.kind = kind
        self.depth = depth
        self.seen = set()
    def trigger_once(self, message):
        if message not in self.seen:
            self.seen.add(message)
            self.trigger(message)
    def trigger(self, message):
        sys.stderr.write("%s in %s: %s\n" % (self.kind, CodeStamp(self.depth), message))

class CodeStamp:
    def __init__(self, depth=1):
        self.frame = sys._getframe(depth)
        self.filename = self.frame.f_code.co_filename
        self.lineno = self.frame.f_lineno
    def __str__(self):
        return "%s:%d" % (self.filename, self.lineno)
        
class CodeMaturity:
    def __init__(self, level = DEVEL):
        self.level = level
        depth = 4 # TODO|FIXME|XXX + MessageTrigger.trigger_once + MessageTrigger.trigger + 1
        self.fixme = MessageTrigger("FIXME", depth)
        self.todo = MessageTrigger("TODO", depth)
        self.xxx = MessageTrigger("XXX", depth)
    
    def TODO(self, message):
        if self.level == DEVEL:
            self.todo.trigger_once(message)
    
    def FIXME(self, message):
        if self.level == DEVEL:
            self.fixme.trigger_once(message)
        elif self.level == RELEASE:
            raise CodeMaturityViolationError(message, CodeStamp(3))
    
    def XXX(self, message):
        if self.level == DEVEL:
            self.xxx.trigger_once(message)
                
current_code_maturity = CodeMaturity()

TODO  = current_code_maturity.TODO
FIXME = current_code_maturity.FIXME
XXX   = current_code_maturity.XXX

__all__ = ["TODO", "FIXME", "XXX"]
