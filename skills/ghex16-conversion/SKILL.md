# GHex16 Conversion Skill

## Purpose

This skill allows coding agents to correctly encode and decode `GHex16` values. GHex16 is an alphabetic encoding of hexadecimal values (using `ghjkmnpqrstvwxyz`), useful for identifier-safe representations that preserve numeric sorting for fixed-width inputs.

## When to use

Use this skill when you need to convert ordinary hexadecimal strings or integers into GHex16 encoded strings, or when you need to decode GHex16 back into hexadecimal strings or integers.

## References

* `references/specs/encodings/ghex16-alphabetic-hex-encoding.md`: The canonical specification for GHex16.

## Scripts

* `scripts/ghex16.py`: A Python 3 utility to perform GHex16 encoding and decoding. It can be used as a command-line tool or imported as a Python module.

### Command-line usage:
```bash
# Encode a hex string (defaults to lowercase)
python scripts/ghex16.py encode-hex 0F1A9C
# Result: gzhtsw

# Encode a hex string with uppercase output
python scripts/ghex16.py encode-hex 0F1A9C --upper
# Result: GZHTSW

# Decode a GHex16 string to hex
python scripts/ghex16.py decode-hex gzhtsw
# Result: 0f1a9c

# Encode an integer
python scripts/ghex16.py encode-int 255
# Result: zz

# Decode to integer
python scripts/ghex16.py decode-int zz
# Result: 255
```

### Module usage:
```python
import ghex16

# Encode/Decode
ghex16.encode_hex_to_ghex16("0F1A9C")      # returns "gzhtsw"
ghex16.encode_hex_to_ghex16("0F", uppercase=True) # returns "GZ"
ghex16.decode_ghex16_to_hex("gzhtsw")      # returns "0f1a9c"

ghex16.encode_int_to_ghex16(255)           # returns "zz"
ghex16.decode_ghex16_to_int("zz")          # returns 255
```

## Common Mistakes

* Mixing uppercase and lowercase characters in the same GHex16 string. A canonical string must be exclusively uppercase or exclusively lowercase.
* Expecting variable-length GHex16 strings to preserve numeric sorting. Numeric sorting is only preserved for fixed-width inputs.
* Treating ordinary letters `a-f` or `A-F` as valid GHex16 inputs when decoding. GHex16 uses `g-z` only.
