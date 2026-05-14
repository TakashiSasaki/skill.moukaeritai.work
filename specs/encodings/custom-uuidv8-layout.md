---
name: custom-uuidv8-layout
description:
  - "@language": en
    "@value": Specification defining the fixed portion of the custom UUIDv8 format used in this application, specifically detailing the UUIDv8 version field and the 12-bit project-local layout discriminator.
  - "@language": ja
    "@value": このアプリケーションで使用されるカスタムUUIDv8フォーマットの固定部分、特にUUIDv8バージョンフィールドと12ビットのプロジェクトローカルなレイアウト識別子について詳細を定めた仕様書。
---

# Custom UUIDv8 Layout Identifier Specification

## 1. Scope

This document defines the fixed portion of the custom UUIDv8 format used in this application.

The purpose of this document is limited to specifying the UUIDv8 version field and the 12-bit project-local layout discriminator immediately following it. The concrete meanings of individual layout_id values, and the bit layouts selected by those values, are intentionally left for future documents or later sections of this specification.

This UUID format is a custom UUIDv8 layout. It is not intended to define a new UUID version, a new UUID variant, or a globally standardized UUID subtype.

## 2. Terminology

The following terms are used in this document.

**UUIDv8** : A UUID whose version field is set to binary 1000. The remaining non-version and non-variant bits are available for application-defined use, subject to the UUID variant requirements.

**layout_id** : A 12-bit project-local layout identifier placed immediately after the UUIDv8 version field. It identifies how the remaining application-defined bits of the UUID are to be interpreted.

**layout_family** : The upper 4 bits of layout_id. It selects a broad family of custom UUIDv8 layouts.

**layout_selector** : The lower 8 bits of layout_id. It selects a concrete layout within the selected layout_family.

**project-local** : Defined only within this application or specification family. A project-local value must not be assumed to have the same meaning in other systems.

## 3. Bit Numbering Convention

This document numbers UUID bits from 0 to 127, starting from the most significant bit of the canonical 128-bit UUID value.

The canonical UUID text representation is the usual 8-4-4-4-12 hexadecimal form:

`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

In this document, bit positions refer to the canonical UUID bit order, not to any platform-specific in-memory representation. In particular, implementations must not infer this bit layout from Microsoft GUID little-endian memory layout conventions.

## 4. Fixed Field Layout

The following portion of the UUIDv8 layout is fixed by this application-level specification.

| Bit range | Length | Field | Required value or meaning |
|---|---|---|---|
| 48–51 | 4 bit | version | UUID version field. Must be binary 1000. |
| 52–63 | 12 bit | layout_id | Project-local custom UUIDv8 layout identifier. |
| 52–55 | 4 bit | layout_family | Upper 4 bits of layout_id. |
| 56–63 | 8 bit | layout_selector | Lower 8 bits of layout_id. |

The layout_id field is defined as:

`layout_id = (layout_family << 8) | layout_selector`

The valid numeric ranges are:

| Field | Width | Range |
|---|---|---|
| layout_family | 4 bit | 0x0–0xf |
| layout_selector | 8 bit | 0x00–0xff |
| layout_id | 12 bit | 0x000–0xfff |

This gives a total of 4096 project-local layout identifiers.

## 5. Canonical Text Representation

In canonical UUID text form, the third hexadecimal group contains the UUID version nibble followed by the 12-bit layout_id.

The third group has the form:

`8FSS`

where:

| Hex digit(s) | Meaning |
|---|---|
| 8 | UUIDv8 version field, binary 1000. |
| F | layout_family, represented as one hexadecimal digit. |
| SS | layout_selector, represented as two hexadecimal digits. |

Thus, the application-level UUIDv8 pattern can be written as:

`aaaaaaaa-aaaa-8FSS-vxxx-xxxxxxxxxxxx`

where:

| Symbol | Meaning |
|---|---|
| a | Application-defined bits before the version field. |
| 8 | UUID version 8. |
| F | layout_family. |
| SS | layout_selector. |
| v | UUID variant-containing hexadecimal digit. For RFC-compatible UUIDs, this digit is normally one of 8, 9, a, or b. |
| x | Application-defined bits after the variant field. |

Examples of the third group only:

| Third group | layout_family | layout_selector | layout_id |
|---|---|---|---|
| 8000 | 0x0 | 0x00 | 0x000 |
| 8100 | 0x1 | 0x00 | 0x100 |
| 8123 | 0x1 | 0x23 | 0x123 |
| 8aff | 0xa | 0xff | 0xaff |
| 8fff | 0xf | 0xff | 0xfff |

## 6. Interpretation Rule

The layout_id identifies the custom UUIDv8 bit layout used by the UUID. It is a layout discriminator, not an object type, MIME type, database table identifier, authorization scope, or semantic class of the referenced object.

A parser may use layout_id to select the decoding rule for the remaining application-defined bits. However, until a specific layout_id is defined by a later specification section, the value is reserved or undefined and must not be interpreted by inference.

Implementations must not assume that numerically adjacent layout_id values have related semantics unless such a relationship is explicitly defined.

## 7. Relationship to UUID Version and Variant

The version field remains the standard UUID version field. For all UUIDs covered by this document, it must be set to UUID version 8.

The layout_id field does not replace, extend, or reinterpret the UUID variant field. The UUID variant field remains separate and must be handled according to the UUID specification.

The variant-containing hexadecimal digit appears in the fourth UUID group, not in the layout_id field. For UUIDs using the RFC-compatible variant, the variant bits are binary 10, and the corresponding hexadecimal digit is normally one of 8, 9, a, or b.

## 8. Reserved and Undefined Values

This document reserves the 12-bit layout_id field as a namespace for project-local UUIDv8 layouts.

The meanings of individual values from 0x000 to 0xfff are not assigned in this document. Future specification sections should define allocation policy, including whether particular layout_family values or layout_selector ranges are reserved, experimental, deprecated, or assigned.

Recommended future policy decisions include:

* whether layout_family = 0x0 is reserved for null, baseline, or legacy layouts;
* whether layout_family = 0xf is reserved for experimental or private layouts;
* whether layout_selector = 0x00 has a default meaning within each family;
* whether layout_selector = 0xff is reserved within each family;
* whether allocation is dense, sparse, or registry-based.

Until those policies are explicitly defined, no special meaning is assigned to any layout_id value beyond its role as a 12-bit discriminator.

## 9. Implementation Notes

Implementations should expose layout_id, layout_family, and layout_selector as derived fields when parsing this application’s UUIDv8 values.

The extraction rules are:

`layout_family = (layout_id >> 8) & 0x0f`

`layout_selector = layout_id & 0xff`

When extracting from the canonical third UUID group 8FSS, implementations should verify that the first hexadecimal digit is 8 before interpreting the following three hexadecimal digits as layout_id.

A parser should reject or treat as unsupported any UUID whose version field is not 8 when this custom UUIDv8 format is expected.

A parser should also validate the UUID variant independently of layout_id.

## 10. Current Decision Summary

The following decisions are fixed by this document:

1. This application will use UUIDv8 for custom UUID layouts.
2. The UUID version field is the standard 4-bit UUID version field and must be binary 1000.
3. The 12 bits immediately following the version field are reserved as layout_id.
4. layout_id is divided into a 4-bit layout_family and an 8-bit layout_selector.
5. `layout_id = (layout_family << 8) | layout_selector`.
6. The concrete meanings of the 4096 possible layout_id values are not yet assigned.
7. layout_id identifies UUID bit layouts, not object semantics.
