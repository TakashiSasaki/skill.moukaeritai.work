#!/usr/bin/env python3
import json
import sys
import os

def main():
    errors = 0

    required_files = [
        "catalog/catalog.jsonld",
        "specs/json-schema/document-record.schema.json",
        "specs/vocab/core.ttl",
        "specs/shacl/document-record.shacl.ttl",
        "specs/sql/document-record.sqlite.sql",
        "specs/mappings/jsonld/document-record.context.jsonld",
        "examples/valid/document-record.json",
        "examples/invalid/document-record-missing-title.json",
        "bundles/skills/document-record-authoring.yaml",
        "skills/document-record-authoring/SKILL.md",
    ]

    for rf in required_files:
        if not os.path.exists(rf):
            print(f"FAIL: Missing required file {rf}")
            errors += 1
        else:
            print(f"PASS: Required file {rf} exists")

    try:
        with open("specs/json-schema/document-record.schema.json") as f:
            schema_data = json.load(f)
            if "$id" not in schema_data or "title" not in schema_data:
                print("FAIL: JSON Schema missing $id or title")
                errors += 1
            if schema_data.get("additionalProperties") is not False:
                print("FAIL: JSON Schema missing additionalProperties: false")
                errors += 1
            print("PASS: JSON Schema looks well-formed")
    except Exception as e:
        print(f"FAIL: Could not load JSON Schema: {e}")
        errors += 1

    try:
        with open("examples/valid/document-record.json") as f:
            valid_data = json.load(f)
            if "id" not in valid_data or "title" not in valid_data or "createdAt" not in valid_data:
                print("FAIL: valid/document-record.json is missing required fields")
                errors += 1
            elif any(k not in ["id", "title", "createdAt", "tags"] for k in valid_data):
                print("FAIL: valid/document-record.json has unexpected properties")
                errors += 1
            else:
                print("PASS: valid/document-record.json has basic required fields and no unexpected properties")
    except Exception as e:
        print(f"FAIL: Could not load valid example: {e}")
        errors += 1

    try:
        with open("examples/invalid/document-record-missing-title.json") as f:
            invalid_data = json.load(f)
            if "title" in invalid_data:
                print("FAIL: invalid/document-record-missing-title.json has a title")
                errors += 1
            else:
                print("PASS: invalid/document-record-missing-title.json correctly misses title")
    except Exception as e:
        print(f"FAIL: Could not load invalid example: {e}")
        errors += 1

    # Check that SQL scripts are valid
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        with open("specs/sql/document-record.sqlite.sql") as f:
            conn.executescript(f.read())

        try:
            conn.execute("INSERT INTO document_record (id, title, created_at) VALUES ('1', '', '2024-01-01')")
            print("FAIL: SQL did not reject empty title")
            errors += 1
        except sqlite3.IntegrityError:
            print("PASS: SQL rejected empty title")

        try:
            conn.execute("INSERT INTO document_record (id, title, created_at) VALUES ('2', 'Doc 2', '2024-01-01')")
            conn.execute("INSERT INTO document_record_tag (document_id, tag) VALUES ('2', '')")
            print("FAIL: SQL did not reject empty tag")
            errors += 1
        except sqlite3.IntegrityError:
            print("PASS: SQL rejected empty tag")

        conn.close()
    except Exception as e:
        print(f"FAIL: SQL evaluation failed: {e}")
        errors += 1

    # Check for committed generated files
    try:
        import subprocess
        output = subprocess.check_output(["git", "ls-files", ".bundle-out"]).decode("utf-8")
        if output.strip():
            print("FAIL: .bundle-out contents are committed to git")
            errors += 1
        else:
            print("PASS: No .bundle-out contents committed")

        output = subprocess.check_output(["git", "ls-files", "dist"]).decode("utf-8")
        if output.strip():
            print("FAIL: dist/ directory contents are committed to git")
            errors += 1
        else:
            print("PASS: No dist/ contents committed")
    except Exception:
        # Ignore git errors if not in git repo
        pass

    if errors > 0:
        print(f"Validation failed with {errors} errors.")
        sys.exit(1)
    else:
        print("All validations passed.")

if __name__ == "__main__":
    main()
