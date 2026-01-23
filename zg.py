#!/usr/bin/env python

"""
Copyright (c) 2006-2021 sqlmap developers (http://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import os
import re
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
    Leaves initial URL/parameter intact (e.g. site.com?id=1)
    Wraps every token AFTER first space with /*!50000TOKEN*/
    Preserves SQL comments
    """
    if not payload or " " not in payload:
        return payload

    postfix = ""

    # Preserve trailing SQL comments
    for comment in ("--", "#", "/*"):
        if comment in payload:
            postfix = payload[payload.find(comment):]
            payload = payload[:payload.find(comment)]
            break

    # Split once: keep first part untouched
    first, rest = payload.split(" ", 1)

    # Wrap every non-space token in the SQL part
    rest = re.sub(r"[^\s]+", lambda m: f"/*!50000{m.group(0)}*/", rest)

    return first + " " + rest + postfix