---
name: ghex16-alphabetic-hex-encoding
description: A nibble-wise alphabetic encoding of hexadecimal digits
---

1. Overview

GHex16 is a nibble-wise alphabetic encoding of hexadecimal digits. It maps each hexadecimal digit, representing one 4-bit value, to one uppercase ASCII letter.

The defining alphabet of GHex16 is:

GHJKMNPQRSTVWXYZ

The mapping is value-preserving in the following sense: hexadecimal values 0 through F are assigned to the GHex16 alphabet from left to right. Therefore, for fixed-length strings, lexicographic order of GHex16 strings under binary ASCII / Unicode code point ordering is identical to the numeric order of the original hexadecimal values.

GHex16 is not standard hexadecimal notation. It is a distinct textual representation intended for cases where values normally written in hexadecimal need to be represented using identifier-friendly uppercase alphabetic characters.

2. Goals

GHex16 is designed to satisfy the following requirements.

First, every hexadecimal digit is encoded as exactly one character. Therefore, the encoded string has the same length as the source hexadecimal string.

Second, the encoded form uses uppercase ASCII letters only. This makes the representation suitable for many identifier syntaxes that disallow leading digits.

Third, the alphabet avoids visually or semantically undesirable characters. In particular, it excludes I, L, O, and U.

Fourth, the mapping preserves order for fixed-length values. If two source hexadecimal strings have the same length, then comparing their GHex16 encodings lexicographically gives the same result as comparing the original hexadecimal values numerically.

Fifth, the alphabet avoids A through F, so GHex16 strings are visually distinct from ordinary hexadecimal notation.

3. Non-goals

GHex16 is not intended to be a compression format. It does not reduce string length.

GHex16 is not a general base-N encoding for arbitrary byte streams in the same sense as Base32 or Base64. It is a direct digit-for-digit transformation of hexadecimal notation.

GHex16 is not intended to provide secrecy, authentication, checksumming, or error correction.

GHex16 is not intended to be parsed as ordinary hexadecimal. Characters such as A, B, C, D, E, and F are not valid GHex16 digits.

4. Alphabet

The GHex16 alphabet consists of the following 16 uppercase ASCII letters:

G H J K M N P Q R S T V W X Y Z

As a contiguous string:

GHJKMNPQRSTVWXYZ

The alphabet deliberately excludes:

A B C D E F I L O U

The letters A through F are excluded to avoid visual confusion with ordinary hexadecimal notation. The letters I, L, and O are excluded because of common visual confusion with 1, 1, and 0, respectively. The letter U is excluded to reduce the likelihood of accidental word formation and to align with human-readable alphabet design patterns that omit U.

5. Encoding table

The canonical mapping from hexadecimal digits to GHex16 characters is:

Hex digit	Numeric value	GHex16 digit

0	0	G
1	1	H
2	2	J
3	3	K
4	4	M
5	5	N
6	6	P
7	7	Q
8	8	R
9	9	S
A	10	T
B	11	V
C	12	W
D	13	X
E	14	Y
F	15	Z


In compact form:

0123456789ABCDEF
maps to:

GHJKMNPQRSTVWXYZ

6. Decoding table

The canonical inverse mapping is:

GHex16 digit	Numeric value	Hex digit

G	0	0
H	1	1
J	2	2
K	3	3
M	4	4
N	5	5
P	6	6
Q	7	7
R	8	8
S	9	9
T	10	A
V	11	B
W	12	C
X	13	D
Y	14	E
Z	15	F


7. Canonical form

A canonical GHex16 string MUST contain only characters from the alphabet:

GHJKMNPQRSTVWXYZ

A canonical GHex16 string MUST NOT contain lowercase letters.

A canonical GHex16 string MUST NOT contain whitespace, separators, prefixes, suffixes, hyphens, underscores, or grouping marks.

The empty string MAY be considered a valid GHex16 encoding of the empty hexadecimal string, depending on the embedding application.

Characters outside the GHex16 alphabet are invalid in strict decoding.

8. Encoding algorithm

Given a hexadecimal string H, the encoder processes each hexadecimal digit independently.

For each character:

0 is replaced with G;
1 is replaced with H;
2 is replaced with J;
3 is replaced with K;
4 is replaced with M;
5 is replaced with N;
6 is replaced with P;
7 is replaced with Q;
8 is replaced with R;
9 is replaced with S;
A is replaced with T;
B is replaced with V;
C is replaced with W;
D is replaced with X;
E is replaced with Y;
F is replaced with Z.

Input hexadecimal letters SHOULD be normalized to uppercase before encoding. A strict encoder MAY reject lowercase hexadecimal input instead.

The output length is exactly equal to the input length.

9. Decoding algorithm

Given a GHex16 string G, the decoder processes each character independently.

For each character:

G is replaced with 0;
H is replaced with 1;
J is replaced with 2;
K is replaced with 3;
M is replaced with 4;
N is replaced with 5;
P is replaced with 6;
Q is replaced with 7;
R is replaced with 8;
S is replaced with 9;
T is replaced with A;
V is replaced with B;
W is replaced with C;
X is replaced with D;
Y is replaced with E;
Z is replaced with F.

A strict decoder MUST reject every character outside the GHex16 alphabet.

A permissive decoder MAY accept lowercase ghjkmnpqrstvwxyz by first converting the input to uppercase. However, such lowercase input is not canonical.

10. Byte encoding

GHex16 itself is defined as a transformation of hexadecimal digits. To encode bytes, first represent the byte sequence as hexadecimal using two hexadecimal digits per byte, with the high nibble first and the low nibble second. Then encode each hexadecimal digit using the GHex16 mapping.

For example, the byte 0xAF is first written as hexadecimal AF, then encoded as TZ.

The byte 0x00 is encoded as GG.

The byte 0xFF is encoded as ZZ.

11. Ordering property

For fixed-length hexadecimal strings, GHex16 preserves numeric order under lexicographic comparison.

For example, ordinary fixed-width hexadecimal order:

00 < 01 < 09 < 0A < 0F < 10

is transformed into:

GG < GH < GS < GT < GZ < HG

This works because the GHex16 alphabet is monotonically ordered by ASCII / Unicode code point value:

G < H < J < K < M < N < P < Q < R < S < T < V < W < X < Y < Z

and because each source digit is mapped to the corresponding target character in numeric order.

This property is guaranteed only when the compared values have the same length. For variable-length numeric values, lexicographic order and numeric order do not generally coincide. Applications requiring numeric order SHOULD use fixed-width encodings, length-prefixing, or compare by length before lexicographic comparison.

For example, the hexadecimal values F and 10 satisfy:

F < 10 numerically is false; actually 0xF < 0x10.

Their GHex16 encodings are:

Z and HG.

Lexicographically, HG < Z, which is consistent only if the values are represented at fixed width, for example:

0F -> GZ
10 -> HG

and then:

GZ < HG

Therefore, fixed-width representation is REQUIRED when GHex16 strings are sorted lexicographically as numeric identifiers.

12. Identifier suitability

A GHex16 string consists only of uppercase ASCII letters. It can therefore be embedded directly in many identifier-like syntaxes that require the first character to be alphabetic.

Because the first encoded digit is always one of G H J K M N P Q R S T V W X Y Z, a GHex16-encoded value never begins with a digit.

This is useful when encoding hexadecimal-like identifiers for environments such as programming-language identifiers, conservative XML local names, RDF local names, database symbolic keys, filesystem-safe names, or URL path components.

The embedding specification remains responsible for determining whether additional restrictions apply. For example, some systems may impose maximum length limits, case-folding behavior, reserved words, or namespace-specific naming rules.

13. Collation requirements

Applications relying on the ordering property MUST compare GHex16 strings using binary code point ordering, ASCII ordering, or another collation that preserves the order:

G < H < J < K < M < N < P < Q < R < S < T < V < W < X < Y < Z

Applications MUST NOT assume that locale-sensitive, case-insensitive, natural-sort, or dictionary-style collation preserves the numeric ordering property.

When storing GHex16 identifiers in databases, a binary collation is preferred if lexicographic order is intended to reflect numeric order.

14. Error handling

A strict GHex16 decoder MUST reject the following:

ordinary hexadecimal letters A B C D E F;
digits 0 1 2 3 4 5 6 7 8 9;
excluded letters I L O U;
lowercase letters, unless a permissive profile is explicitly used;
whitespace;
punctuation;
fullwidth Unicode variants;
look-alike Unicode characters;
prefixes such as 0x;
grouping separators such as _, -, or space.

Applications MAY define an external presentation format with grouping separators, but such separators are not part of canonical GHex16.

15. Test vectors

Source hex	GHex16

empty string	empty string
0	G
1	H
9	S
A	T
F	Z
00	GG
0F	GZ
10	HG
FF	ZZ
0123456789ABCDEF	GHJKMNPQRSTVWXYZ
0F1A9C	GZHTSW
DEADBEEF	XYTXVYYZ


16. Rationale

16.1 Why a hexadecimal-derived encoding?

Hexadecimal notation is widely used because each digit corresponds exactly to one 4-bit nibble. This makes it convenient for binary data, hashes, UUIDs, bit fields, machine identifiers, database keys, and low-level diagnostic values.

However, ordinary hexadecimal notation uses digits 0 through 9. This is inconvenient in syntactic contexts where identifiers cannot begin with digits. A hexadecimal value such as 0F1A9C may be semantically suitable as an identifier but syntactically invalid or awkward in systems requiring an alphabetic initial character.

GHex16 preserves the nibble-wise structure of hexadecimal while replacing all digits with uppercase letters.

16.2 Why not simply prefix ordinary hex?

Prefixing ordinary hexadecimal, such as x0F1A9C, is often the simplest solution. However, prefixing changes the structure of the identifier and does not eliminate digit characters from the body. In contexts where an all-letter identifier is preferred, or where the encoded value should occupy exactly one character per nibble without a special prefix, a digit-free alphabetic encoding is useful.

GHex16 is designed for those cases.

16.3 Why not keep A through F unchanged?

Keeping A through F unchanged initially seems attractive because it preserves partial familiarity with ordinary hexadecimal. However, doing so breaks the natural ordering property.

In ordinary hexadecimal, the digit order is:

0 < 1 < 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9 < A < B < C < D < E < F

If A through F are retained as values 10 through 15, then those letters appear before many replacement letters in ASCII lexicographic order. As a result, encoded string order no longer corresponds to numeric order.

GHex16 instead maps values 0 through 15 to a target alphabet that is itself lexicographically ordered. This gives the desired fixed-width sorting behavior.

16.4 Why start at G?

Starting at G has a specific purpose: it avoids using A through F, which are already meaningful as ordinary hexadecimal digits.

If GHex16 used A as the encoding of zero, then the encoded alphabet might look like an alternative Base16 alphabet but would visually overlap with conventional hexadecimal notation. By starting at G, GHex16 makes encoded strings visibly distinct from ordinary hex.

For example:

ordinary hex: 0F1A9C
GHex16: GZHTSW

The GHex16 form is not easily mistaken for standard hexadecimal.

16.5 Why skip I, L, and O?

The letters I, L, and O are commonly confused with digits or with each other in many fonts and handwriting styles.

I may be confused with 1.
L may be confused with 1 or lowercase l.
O may be confused with 0.

Because GHex16 is intended for identifier-like and possibly human-visible strings, avoiding these letters reduces transcription and reading errors.

16.6 Why skip U?

The letter U is not excluded primarily because of visual ambiguity. The main rationale is to reduce accidental word formation, especially undesirable or distracting word fragments, in generated identifiers.

By excluding U, while also excluding A, E, I, and O, the alphabet avoids ordinary English vowel letters except Y. This makes it less likely that arbitrary encoded strings will accidentally resemble natural-language words.

The resulting alphabet is still large enough to encode all 16 nibble values while preserving lexicographic order.

16.7 Why uppercase only?

Uppercase ASCII letters are widely accepted in identifiers and are visually stable across many systems. Restricting the canonical form to uppercase also avoids ambiguity between uppercase and lowercase variants.

Allowing lowercase as a permissive input form is possible, but lowercase output is not canonical.

16.8 Why one character per nibble?

A one-character-per-nibble mapping gives GHex16 a simple relationship to hexadecimal. It allows direct conversion without bit packing, padding rules, or byte-boundary complications.

This makes the format easy to implement, inspect, and debug. The length of the encoded string is exactly the same as the length of the source hexadecimal string.

16.9 Why fixed-width ordering only?

No positional numeral system with ordinary lexicographic comparison preserves numeric order across arbitrary variable-length strings without additional rules. For example, in decimal notation, 100 sorts before 20 lexicographically even though 100 is numerically larger.

The same issue applies to hexadecimal and GHex16. Therefore, GHex16’s ordering guarantee is explicitly limited to fixed-length strings, or to systems that externally normalize length.

17. Suggested API names

Suggested function names:

encode_ghex16
decode_ghex16

Alternative method-style names:

to_ghex16
from_ghex16

Suggested regular expression for canonical GHex16:

^[GHJKMNPQRSTVWXYZ]*$

Suggested regular expression for non-empty canonical GHex16:

^[GHJKMNPQRSTVWXYZ]+$

18. Summary definition

GHex16 is a digit-free, uppercase, nibble-wise encoding of hexadecimal values using the alphabet:

GHJKMNPQRSTVWXYZ

Its canonical digit mapping is:

0123456789ABCDEF
→
GHJKMNPQRSTVWXYZ

Its primary properties are:

it uses only uppercase ASCII letters;
it never begins with a digit;
it excludes I, L, O, and U;
it avoids A through F to distinguish itself from ordinary hexadecimal;
it preserves numeric order under lexicographic comparison for fixed-length strings.
