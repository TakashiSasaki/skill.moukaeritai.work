# Validation Rules

All changes to the schemas or examples must pass validation.

Validation is performed by `tools/validate_all.py` in the canonical repository, or an equivalent script in the skill bundle.

The validation script checks:
1. All required canonical files exist.
2. The valid example (`examples/valid/document-record.json`) has the basic required fields (`id`, `title`, `createdAt`).
3. The invalid example (`examples/invalid/document-record-missing-title.json`) is correctly flagged as invalid (missing `title`).
