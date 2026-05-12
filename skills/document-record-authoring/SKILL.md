---
name: document-record-authoring
description: Use this skill when authoring or editing DocumentRecord data, schemas, or tools.
---

# DocumentRecord Authoring Skill

## Purpose
This skill provides operational guidance for authoring, editing, and validating `DocumentRecord` definitions and data.

## Important Note
Schemas in `specs/` are canonical. This skill provides operational guidance and is NOT the primary definition of the domain.
Do NOT edit generated distribution branch files directly. Only edit the canonical files on `main`.

## Instructions
1. **Read References First:** Before making any changes, read `references/schema-sources.md` to understand where canonical files are located.
2. **Validation Rules:** Understand the validation expectations by reading `references/validation-rules.md`.
3. **Run Validation:** After making changes in the canonical repository (`main` branch), run the validation script:
   ```bash
   python tools/validate_all.py
   ```
4. **Distribution Bundles:** If you are working within a distribution bundle (`dist/*` branch), use the bundled `references/specs/` and `scripts/` paths if they are present.
