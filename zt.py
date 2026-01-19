#!/usr/bin/env python 

import re 

from lib.core.enums import PRIORITY 

__priority__ = PRIORITY.NORMAL 

def tamper(payload, **kwargs):
    retVal = payload 

    if payload:
        for word in ("union", "select"):
            retVal = retVal.replace(word, "%/**_**//*!s*/%/**_**//*!s*/%"  (word[:len(word) / 2], word[len(word) / 2:])) 

    return retVal
