#!/usr/bin/env python

import random

__priority__ = 1

def dependencies():
    pass

def tamper(payload):
    """
    Wraps every word in payload with /*!50000 and */
    """
    if payload:
        parts = payload.split(" ")
        parts = [f"/*!50000{word}*/" for word in parts if word != ""]
        payload = " ".join(parts)
    return payload