#!/usr/bin/env python

"""
Copyright (c) 2006-2021 sqlmap developers (http://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import os
from lib.core.common import singleTimeWarnMessage
from lib.core.enums import DBMS
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHER


def dependencies():
    singleTimeWarnMessage(
        "tamper script '%s' is only meant to be run against %s"
        % (os.path.basename(__file__).split(".")[0], DBMS.MYSQL)
    )


def tamper(payload, **kwargs):
    """
    Wraps every word in payload with MySQL versioned comments /*!50000WORD*/
    Preserves SQL comments (--, #, /* */)
    """
    if not payload:
        return payload

    retVal = payload
    postfix = ""

    # Extract trailing SQL comment if present
    for comment in ("--", "#", "/*"):
        if comment in payload:
            postfix = payload[payload.find(comment):]
            payload = payload[:payload.find(comment)]
            break

    # Wrap every word
    parts = payload.split(" ")
    parts = [f"/*!50000{word}*/" if word else "" for word in parts]
    retVal = " ".join(parts) + postfix

    return retVal