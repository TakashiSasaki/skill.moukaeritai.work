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
        with open("examples/valid/document-record.json") as f:
            valid_data = json.load(f)
            if "id" not in valid_data or "title" not in valid_data or "createdAt" not in valid_data:
                print("FAIL: valid/document-record.json is missing required fields")
                errors += 1
            else:
                print("PASS: valid/document-record.json has basic required fields")
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

    if errors > 0:
        print(f"Validation failed with {errors} errors.")
        sys.exit(1)
    else:
        print("All validations passed.")

if __name__ == "__main__":
    main()
