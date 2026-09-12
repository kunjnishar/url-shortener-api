"""
Base62 encoding/decoding utilities.

Converts integer primary keys into compact, URL-safe short codes using
the alphabet 0-9a-zA-Z (62 characters total).
"""

BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(BASE62_ALPHABET)
MIN_LENGTH = 6


def base62_encode(number: int) -> str:
    """
    Encode a non-negative integer into a Base62 string.

    The result is left-padded with the alphabet's zero character ('0')
    so that short codes have a consistent minimum length of 6 characters,
    which keeps generated URLs compact and uniform in appearance.
    """
    if number < 0:
        raise ValueError("base62_encode() only supports non-negative integers")

    if number == 0:
        encoded = BASE62_ALPHABET[0]
    else:
        digits = []
        n = number
        while n > 0:
            n, remainder = divmod(n, BASE)
            digits.append(BASE62_ALPHABET[remainder])
        encoded = "".join(reversed(digits))

    if len(encoded) < MIN_LENGTH:
        encoded = encoded.rjust(MIN_LENGTH, BASE62_ALPHABET[0])

    return encoded


def base62_decode(code: str) -> int:
    """
    Decode a Base62 string back into its original integer value.

    Leading padding characters (the alphabet's zero character) are
    naturally handled since they decode to a positional value of 0.
    """
    if not code:
        raise ValueError("base62_decode() received an empty string")

    number = 0
    for char in code:
        if char not in BASE62_ALPHABET:
            raise ValueError(f"Invalid Base62 character encountered: {char!r}")
        number = number * BASE + BASE62_ALPHABET.index(char)

    return number