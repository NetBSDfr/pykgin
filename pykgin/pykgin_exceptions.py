#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Exceptions used in Pykgin."""

class PykginError(Exception):
    """Pykgin custom exceptions."""
    def __init__(self, msg):
        """Constructor."""
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return(self.msg)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

