# Schema and Skill Repository Template

This repository is the canonical source for schemas, vocabularies, validation tools, and coding-agent skills.

## Branching Policy

- `main` is the only editable canonical branch. All canonical schemas, vocabularies, tools, and bundle definitions reside here.
- Distribution branches use the `dist/` prefix (e.g., `dist/skills/document-record-authoring`).
- Distribution branches are generated from `main`. They are not canonical sources. In this small-team repository, direct commits to `dist/*` branches are allowed only as temporary field patches. Such commits must be backported to `main` or explicitly discarded. The publisher detects pending field patches and will not silently overwrite them.
- Distribution branches are intended to be orphan branches, decoupled from the history of `main` to provide clean history for consumers.

## Usage

Downstream users should import the generated `dist/skills/<name>` branches as Git submodules into their own projects. This provides a self-contained skill bundle that the agent can use.

### Example

```bash
git submodule add -b dist/skills/document-record-authoring \
  https://github.com/TakashiSasaki/skill.moukaeritai.work.git \
  .agents/skills/document-record-authoring
```

## Included Example

The repository includes a small `DocumentRecord` example. This toy domain is intentionally small and demonstrates the canonical pattern of managing schemas, shapes, JSON-LD contexts, validation, and skill bundling without introducing unnecessary domain complexity.
