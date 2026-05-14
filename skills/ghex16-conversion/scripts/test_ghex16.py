import unittest
from ghex16 import encode_hex_to_ghex16, decode_ghex16_to_hex, encode_int_to_ghex16, decode_ghex16_to_int

class TestGHex16(unittest.TestCase):

    def test_encode_hex_to_ghex16(self):
        # Default lowercase
        self.assertEqual(encode_hex_to_ghex16(""), "")
        self.assertEqual(encode_hex_to_ghex16("0"), "g")
        self.assertEqual(encode_hex_to_ghex16("1"), "h")
        self.assertEqual(encode_hex_to_ghex16("9"), "s")
        self.assertEqual(encode_hex_to_ghex16("a"), "t")
        self.assertEqual(encode_hex_to_ghex16("A"), "t")
        self.assertEqual(encode_hex_to_ghex16("f"), "z")
        self.assertEqual(encode_hex_to_ghex16("F"), "z")
        self.assertEqual(encode_hex_to_ghex16("00"), "gg")
        self.assertEqual(encode_hex_to_ghex16("0F"), "gz")
        self.assertEqual(encode_hex_to_ghex16("10"), "hg")
        self.assertEqual(encode_hex_to_ghex16("FF"), "zz")
        self.assertEqual(encode_hex_to_ghex16("0123456789abcdef"), "ghjkmnpqrstvwxyz")
        self.assertEqual(encode_hex_to_ghex16("0123456789ABCDEF"), "ghjkmnpqrstvwxyz")
        self.assertEqual(encode_hex_to_ghex16("0F1A9C"), "gzhtsw")
        self.assertEqual(encode_hex_to_ghex16("DEADBEEF"), "xytxvyyz")

        # Uppercase
        self.assertEqual(encode_hex_to_ghex16("0F1A9C", uppercase=True), "GZHTSW")
        self.assertEqual(encode_hex_to_ghex16("deadbeef", uppercase=True), "XYTXVYYZ")

    def test_encode_hex_to_ghex16_invalid(self):
        with self.assertRaises(ValueError):
            encode_hex_to_ghex16("g")
        with self.assertRaises(ValueError):
            encode_hex_to_ghex16("0x1A")

    def test_decode_ghex16_to_hex(self):
        # Default strict case
        self.assertEqual(decode_ghex16_to_hex(""), "")
        self.assertEqual(decode_ghex16_to_hex("g"), "0")
        self.assertEqual(decode_ghex16_to_hex("h"), "1")
        self.assertEqual(decode_ghex16_to_hex("s"), "9")
        self.assertEqual(decode_ghex16_to_hex("t"), "a")
        self.assertEqual(decode_ghex16_to_hex("z"), "f")
        self.assertEqual(decode_ghex16_to_hex("gg"), "00")
        self.assertEqual(decode_ghex16_to_hex("gz"), "0f")
        self.assertEqual(decode_ghex16_to_hex("hg"), "10")
        self.assertEqual(decode_ghex16_to_hex("zz"), "ff")
        self.assertEqual(decode_ghex16_to_hex("ghjkmnpqrstvwxyz"), "0123456789abcdef")
        self.assertEqual(decode_ghex16_to_hex("GHJKMNPQRSTVWXYZ"), "0123456789abcdef")
        self.assertEqual(decode_ghex16_to_hex("gzhtsw"), "0f1a9c")
        self.assertEqual(decode_ghex16_to_hex("xytxvyyz"), "deadbeef")

    def test_decode_ghex16_to_hex_invalid_characters(self):
        with self.assertRaises(ValueError):
            decode_ghex16_to_hex("a") # Not in ghex16 alphabet
        with self.assertRaises(ValueError):
            decode_ghex16_to_hex("0") # Not in ghex16 alphabet
        with self.assertRaises(ValueError):
            decode_ghex16_to_hex("i") # excluded
        with self.assertRaises(ValueError):
            decode_ghex16_to_hex("l") # excluded
        with self.assertRaises(ValueError):
            decode_ghex16_to_hex("o") # excluded
        with self.assertRaises(ValueError):
            decode_ghex16_to_hex("u") # excluded

    def test_decode_ghex16_to_hex_mixed_case(self):
        # Strict mode (default) should reject mixed case
        with self.assertRaisesRegex(ValueError, "GHex16 string must not mix uppercase and lowercase"):
            decode_ghex16_to_hex("gZhT")
        with self.assertRaisesRegex(ValueError, "GHex16 string must not mix uppercase and lowercase"):
            decode_ghex16_to_hex("Gz")

        # Mixed case allowed
        self.assertEqual(decode_ghex16_to_hex("gZhT", allow_mixed_case=True), "0f1a")
        self.assertEqual(decode_ghex16_to_hex("Gz", allow_mixed_case=True), "0f")

    def test_encode_int_to_ghex16(self):
        self.assertEqual(encode_int_to_ghex16(0), "g")
        self.assertEqual(encode_int_to_ghex16(1), "h")
        self.assertEqual(encode_int_to_ghex16(15), "z")
        self.assertEqual(encode_int_to_ghex16(16), "hg")
        self.assertEqual(encode_int_to_ghex16(255), "zz")
        self.assertEqual(encode_int_to_ghex16(255, uppercase=True), "ZZ")

    def test_encode_int_to_ghex16_invalid(self):
        with self.assertRaises(ValueError):
            encode_int_to_ghex16(-1)

    def test_decode_ghex16_to_int(self):
        self.assertEqual(decode_ghex16_to_int("g"), 0)
        self.assertEqual(decode_ghex16_to_int("h"), 1)
        self.assertEqual(decode_ghex16_to_int("z"), 15)
        self.assertEqual(decode_ghex16_to_int("hg"), 16)
        self.assertEqual(decode_ghex16_to_int("zz"), 255)
        self.assertEqual(decode_ghex16_to_int("ZZ"), 255)

        # Mixed case
        with self.assertRaisesRegex(ValueError, "GHex16 string must not mix uppercase and lowercase"):
            decode_ghex16_to_int("gZ")

        self.assertEqual(decode_ghex16_to_int("gZ", allow_mixed_case=True), 15)

    def test_decode_ghex16_to_int_invalid(self):
        with self.assertRaises(ValueError):
            decode_ghex16_to_int("") # Empty string cannot be decoded to int

if __name__ == "__main__":
    unittest.main()