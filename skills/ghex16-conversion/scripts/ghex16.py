#!/usr/bin/env python3
"""
GHex16 Conversion Tool
Implements the GHex16 alphabetic encoding of hexadecimal digits.

Provides functions to encode and decode between:
- Hexadecimal strings
- Integers
- GHex16 strings
"""

import sys
import argparse

GHEX16_LOWER = "ghjkmnpqrstvwxyz"
GHEX16_UPPER = "GHJKMNPQRSTVWXYZ"

HEX_DIGITS = "0123456789abcdef"

# Pre-compute encoding and decoding maps
ENCODE_MAP_LOWER = {
    hex_char: ghex_char
    for hex_char, ghex_char in zip(HEX_DIGITS, GHEX16_LOWER)
}
ENCODE_MAP_LOWER.update({
    hex_char.upper(): ghex_char
    for hex_char, ghex_char in zip(HEX_DIGITS, GHEX16_LOWER)
})

ENCODE_MAP_UPPER = {
    hex_char: ghex_char
    for hex_char, ghex_char in zip(HEX_DIGITS, GHEX16_UPPER)
}
ENCODE_MAP_UPPER.update({
    hex_char.upper(): ghex_char
    for hex_char, ghex_char in zip(HEX_DIGITS, GHEX16_UPPER)
})


DECODE_MAP = {
    ghex_char: hex_char
    for ghex_char, hex_char in zip(GHEX16_LOWER, HEX_DIGITS)
}
DECODE_MAP.update({
    ghex_char: hex_char
    for ghex_char, hex_char in zip(GHEX16_UPPER, HEX_DIGITS)
})


def encode_hex_to_ghex16(hex_str: str, uppercase: bool = False) -> str:
    """Encode a hexadecimal string to a GHex16 string."""
    map_to_use = ENCODE_MAP_UPPER if uppercase else ENCODE_MAP_LOWER
    try:
        return "".join(map_to_use[c] for c in hex_str)
    except KeyError as e:
        raise ValueError(f"Invalid hexadecimal character: {e.args[0]}")


def decode_ghex16_to_hex(ghex16_str: str) -> str:
    """Decode a GHex16 string to a hexadecimal string (lowercase)."""
    try:
        return "".join(DECODE_MAP[c] for c in ghex16_str)
    except KeyError as e:
        raise ValueError(f"Invalid GHex16 character: {e.args[0]}")


def encode_int_to_ghex16(value: int, uppercase: bool = False) -> str:
    """Encode an integer to a GHex16 string."""
    if value < 0:
        raise ValueError("Negative integers cannot be encoded to GHex16 without explicit byte sizing.")
    # hex() returns '0x...', we strip the '0x'
    hex_str = hex(value)[2:]
    return encode_hex_to_ghex16(hex_str, uppercase=uppercase)


def decode_ghex16_to_int(ghex16_str: str) -> int:
    """Decode a GHex16 string to an integer."""
    if not ghex16_str:
        raise ValueError("Cannot decode empty string to an integer")
    hex_str = decode_ghex16_to_hex(ghex16_str)
    return int(hex_str, 16)


def main():
    parser = argparse.ArgumentParser(
        description="Convert to and from GHex16 representation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encode hex command
    parser_encode_hex = subparsers.add_parser("encode-hex", help="Encode hexadecimal string to GHex16")
    parser_encode_hex.add_argument("value", help="The hexadecimal string to encode")
    parser_encode_hex.add_argument("--upper", action="store_true", help="Output uppercase GHex16")

    # Encode int command
    parser_encode_int = subparsers.add_parser("encode-int", help="Encode integer to GHex16")
    parser_encode_int.add_argument("value", type=int, help="The integer value to encode")
    parser_encode_int.add_argument("--upper", action="store_true", help="Output uppercase GHex16")

    # Decode to hex command
    parser_decode_hex = subparsers.add_parser("decode-hex", help="Decode GHex16 to hexadecimal string")
    parser_decode_hex.add_argument("value", help="The GHex16 string to decode")

    # Decode to int command
    parser_decode_int = subparsers.add_parser("decode-int", help="Decode GHex16 to integer")
    parser_decode_int.add_argument("value", help="The GHex16 string to decode")

    args = parser.parse_args()

    try:
        if args.command == "encode-hex":
            result = encode_hex_to_ghex16(args.value, uppercase=args.upper)
        elif args.command == "encode-int":
            result = encode_int_to_ghex16(args.value, uppercase=args.upper)
        elif args.command == "decode-hex":
            result = decode_ghex16_to_hex(args.value)
        elif args.command == "decode-int":
            result = decode_ghex16_to_int(args.value)
        else:
            parser.print_help()
            sys.exit(1)

        print(result)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
