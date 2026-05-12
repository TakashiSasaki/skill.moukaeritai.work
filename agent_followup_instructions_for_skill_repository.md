# Follow-up Instructions for Hardening the Schema Skill Repository Template

## 1. Task

Continue improving the current `main` branch of this repository so that it moves from a minimal bootstrap template toward an operational schema/skill distribution repository.

The current repository already contains a minimal `DocumentRecord` example, schema files, a skill, a bundle definition, validation scripts, and GitHub Actions workflows. Your task is to harden this implementation while preserving the design principles already documented in the repository.

Do not replace the repository with a new unrelated layout. Work incrementally from the existing structure.

## 2. Design principles to preserve

Preserve these principles throughout the work:

1. `main` is the only editable canonical branch.
2. Distribution branches use the `dist/` prefix.
3. Distribution branches are generated artifacts, not editable sources.
4. Distribution branches must be created as orphan branches on first publication.
5. Distribution branches must retain their own history after initial orphan creation.
6. Standard skill bundles must be self-contained.
7. Standard skill bundles must not require recursive submodules.
8. Canonical schema files belong under `specs/`, not under skill `assets/`.
9. Bundled schema snapshots belong under `references/specs/` in the generated bundle.
10. Symlinks must not be required for generated bundles.
11. Bundle generation should be deterministic where practical.
12. Do not add large frameworks or over-engineer this template.

## 3. Primary goals

Implement the next hardening step in this order:

1. Replace placeholder publishing logic with a safe, working implementation for generated `dist/*` orphan distribution branches.
2. Strengthen bundle generation so that output directories are cleanly regenerated and `bundle-lock.json` contains useful provenance.
3. Strengthen validation enough to catch obvious inconsistencies between JSON Schema, JSON-LD, SHACL, SQL, catalog, examples, and bundle definitions.
4. Fix obvious constraint mismatches in the `DocumentRecord` example.
5. Replace placeholder public metadata such as repository URLs and license holder where appropriate.
6. Keep the repository simple and maintainable.

## 4. Required changes

### 4.1 Implement `tools/bundle/publish_bundle_branches.py`

Replace the current placeholder with a safe implementation.

The script must support at least these arguments:

```bash
python tools/bundle/publish_bundle_branches.py --bundles-out .bundle-out
python tools/bundle/publish_bundle_branches.py --bundles-out .bundle-out --push
```

The script must remain a dry run unless `--push` is provided.

Expected behavior:

1. Read generated bundle metadata from each bundle output directory.
2. Determine the target output branch from `references/bundle-lock.json`.
3. Verify that the target branch starts with `dist/`.
4. Fetch the target branch from `origin` if it exists.
5. If the target branch does not exist, create it as an orphan branch.
6. If the target branch exists, check it out normally.
7. Replace the branch working tree with the generated bundle contents.
8. Commit only if there is a diff.
9. Push only when `--push` is explicitly provided.
10. Never force-push by default.
11. Print clear messages explaining what would happen in dry-run mode.

Implementation details:

- Use `git worktree` or a temporary clone/worktree.
- Never copy `.git` directories into the distribution branch.
- Do not allow target branch names that do not start with `dist/`.
- Do not allow absolute paths or path traversal.
- Use a deterministic commit message format.

Recommended commit message:

```text
Publish <bundle-name> bundle

Source branch: main
Source commit: <source-commit>
Bundle definition: <bundle-definition-path>
```

### 4.2 Strengthen `tools/bundle/build_bundles.py`

Improve bundle generation.

Requirements:

1. Clean the target bundle directory before regenerating it.
2. Reject absolute source paths.
3. Reject `..` path traversal in both source and target paths.
4. Reject output paths that escape the bundle root after normalization.
5. Copy directories and files deterministically.
6. Do not copy symlinks into bundles. Prefer failing if a symlink is encountered.
7. Generate a richer `references/bundle-lock.json`.
8. Do not include timestamps in the lock file.
9. Include checksums for copied files.
10. Preserve standard-library-only operation unless a dependency file is intentionally added.

The lock file should contain at least:

```json
{
  "schemaVersion": 1,
  "bundle": {
    "name": "document-record-authoring",
    "kind": "skill",
    "outputBranch": "dist/skills/document-record-authoring"
  },
  "source": {
    "repository": "https://github.com/TakashiSasaki/skill.moukaeritai.work.git",
    "branch": "main",
    "commit": "<git-commit>",
    "bundleDefinition": "bundles/skills/document-record-authoring.yaml"
  },
  "generated": {
    "mode": "orphan-distribution-branch",
    "historyPolicy": "append-only"
  },
  "included": [
    {
      "from": "specs/json-schema/document-record.schema.json",
      "to": "references/specs/json-schema/document-record.schema.json",
      "sha256": "..."
    }
  ]
}
```

If the repository URL cannot be detected reliably, use:

```text
https://github.com/TakashiSasaki/skill.moukaeritai.work.git
```

### 4.3 Generate or copy bundle README files

The bundle definition currently contains:

```yaml
generate:
  readme: README.md
```

Make this meaningful.

Generated bundle `README.md` must state:

1. This is a generated distribution branch.
2. Do not edit it directly.
3. Canonical sources are maintained on `main`.
4. The source bundle definition path.
5. The source commit.
6. How to add the bundle as a submodule.
7. How to update the submodule.

Use the real repository URL:

```bash
git submodule add -b dist/skills/document-record-authoring \
  https://github.com/TakashiSasaki/skill.moukaeritai.work.git \
  .agents/skills/document-record-authoring
```

### 4.4 Improve `tools/bundle/validate_bundle_definitions.py`

The current validator is string-based. Improve it while keeping the implementation simple.

Requirements:

1. Validate required fields: `schemaVersion`, `bundle.name`, `bundle.kind`, `bundle.source`, `bundle.outputBranch`, and `include`.
2. Verify `bundle.outputBranch` starts with `dist/`.
3. Verify every `include[].from` exists.
4. Verify every `include[].to` is relative and does not escape the bundle root.
5. Verify every `include[].mode` is currently `copy`.
6. Verify `generate.lockFile` exists and ends with `bundle-lock.json`.
7. Verify no source or target path contains unsafe traversal.

If adding PyYAML would significantly simplify the implementation, add a minimal `pyproject.toml`. Otherwise keep a limited parser, but document its limitations clearly.

### 4.5 Strengthen `tools/validate_all.py`

Keep the script simple, but make it more useful.

At minimum, add checks for:

1. Required files exist.
2. JSON files parse.
3. JSON Schema contains the expected required fields: `id`, `title`, `createdAt`.
4. JSON Schema has `additionalProperties: false`.
5. Valid example has required fields and no unexpected properties.
6. Invalid example is invalid because `title` is missing.
7. Catalog contains paths to all key files.
8. Bundle definition output branch starts with `dist/`.
9. `skills/document-record-authoring/SKILL.md` has YAML front matter with the expected name.
10. No generated `.bundle-out/` contents are committed to `main`.
11. No `dist/` directory is committed to `main` as if it were canonical source.
12. SQL DDL can be executed in an in-memory SQLite database.
13. SQL table constraints reject an empty title.
14. SQL tag table rejects an empty tag.

Optional if practical:

- Check that Turtle files contain expected prefixes and terms.
- Check that SHACL contains `sh:minCount` and `sh:maxCount` for required properties.
- Check that SHACL contains `sh:minLength 1` for required string properties if such constraints are added.

### 4.6 Align constraints across JSON Schema, SHACL, and SQL

Fix the `DocumentRecord` example so constraints are more consistent.

JSON Schema already requires non-empty `id`, `title`, and non-empty tag strings.

Update SHACL to include:

- `sh:minLength 1` for `core:id`.
- `sh:minLength 1` for `core:title`.
- `sh:minLength 1` for `core:tag`.

Update SQL DDL to make the intended constraints explicit:

```sql
CREATE TABLE document_record (
    id TEXT NOT NULL PRIMARY KEY CHECK (length(id) > 0),
    title TEXT NOT NULL CHECK (length(title) > 0),
    created_at TEXT NOT NULL
);

CREATE TABLE document_record_tag (
    document_id TEXT NOT NULL,
    tag TEXT NOT NULL CHECK (length(tag) > 0),
    PRIMARY KEY (document_id, tag),
    FOREIGN KEY(document_id) REFERENCES document_record(id)
);
```

### 4.7 Replace placeholder repository metadata

Replace placeholder repository URLs in documentation with:

```text
https://github.com/TakashiSasaki/skill.moukaeritai.work.git
```

The root README should no longer use:

```text
https://github.com/YOUR-ORG/YOUR-REPO.git
```

For the MIT license, replace placeholder holder text with:

```text
Copyright (c) 2026 Takashi Sasaki
```

Do not change the license type.

### 4.8 Move bootstrap-only instruction documents if appropriate

The repository currently contains bootstrap/instruction documents at the root. If they are still useful, move them under `docs/` with clearer names, for example:

```text
docs/schema-skill-repository-specification.md
docs/repository-template-agent-instructions.md
docs/agent-followup-instructions.md
```

If moving files, update any links that refer to them.

Do not delete them unless explicitly instructed.

## 5. GitHub Actions updates

### 5.1 `validate.yml`

Keep this workflow as the required validation gate.

It should run:

```bash
python tools/validate_all.py
python tools/bundle/validate_bundle_definitions.py bundles/
python tools/bundle/build_bundles.py --all --out .bundle-out
```

After improving bundle generation, add a check that generated bundle directories contain:

```text
SKILL.md
README.md
references/bundle-lock.json
references/specs/json-schema/document-record.schema.json
references/catalog.snapshot.jsonld
scripts/validate_all.py
```

### 5.2 `publish-bundles.yml`

Keep publishing disabled by default unless repository permissions and branch protections are intentionally configured.

It is acceptable for the workflow to run publish in dry-run mode:

```bash
python tools/bundle/publish_bundle_branches.py --bundles-out .bundle-out
```

If enabling real publishing, use:

```bash
python tools/bundle/publish_bundle_branches.py --bundles-out .bundle-out --push
```

Do not enable real publishing unless branch protection and token permissions are appropriate.

## 6. Acceptance criteria

The work is complete when these commands pass from repository root:

```bash
python tools/validate_all.py
python tools/bundle/validate_bundle_definitions.py bundles/
python tools/bundle/build_bundles.py --all --out .bundle-out
python tools/bundle/publish_bundle_branches.py --bundles-out .bundle-out
```

The last command must be a dry run unless `--push` is explicitly supplied.

After bundle generation, verify that `.bundle-out/document-record-authoring/` contains at least:

```text
SKILL.md
README.md
references/bundle-lock.json
references/catalog.snapshot.jsonld
references/specs/json-schema/document-record.schema.json
references/specs/vocab/core.ttl
references/specs/shacl/document-record.shacl.ttl
references/specs/mappings/jsonld/document-record.context.jsonld
scripts/validate_all.py
```

Also verify:

1. No symlink exists in the generated bundle.
2. `references/bundle-lock.json` contains `outputBranch`, `source.commit`, `source.bundleDefinition`, and an `included` list with SHA-256 checksums.
3. README examples use the real repository URL.
4. SQL constraints and SHACL constraints are aligned with JSON Schema for non-empty strings.
5. No `.bundle-out/` directory is committed to `main`.
6. No `dist/` directory is committed to `main`.
7. `publish_bundle_branches.py` does not push unless `--push` is provided.

## 7. What not to do

Do not:

1. Convert the repository into a multi-repository design.
2. Make `dist/*` branches canonical sources.
3. Require recursive submodules for the standard skill bundle.
4. Put canonical schemas under skill `assets/`.
5. Introduce a large ontology framework.
6. Add generated timestamps that make bundles non-deterministic.
7. Force-push distribution branches by default.
8. Delete the existing example domain unless replacing it with an equally complete example.
9. Claim that distribution branches have been published unless the publish script actually pushed them successfully.

## 8. Expected final report

After completing the work, report:

1. Files changed.
2. Validation commands run and their results.
3. Whether publishing remains dry-run only or was enabled.
4. Whether any `dist/*` branch was actually created.
5. Any remaining limitations.
6. Any decisions that should be reviewed by the repository owner.

