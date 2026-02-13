#!/usr/bin/env python

import random

__priority__ = 1

def dependencies():
pass

def tamper(payload):
"""
Randomly URL encodes characters in the payload
"""
if payload:
encoded_payload = ""
for char in payload:
if random.randint(0, 1):
encoded_payload += "%%%02x" % ord(char)
else:
encoded_payload += char
return encoded_payload
return payload