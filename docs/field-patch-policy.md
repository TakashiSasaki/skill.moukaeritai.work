# Field Patch Policy

Direct commits to distribution branches are allowed in this repository as temporary field patches for small-team debugging and improvement. These commits are not canonical. The canonical source remains `main`. The bundle publisher detects field patches by finding commits after the last generated commit on a `dist/*` branch. If such commits exist, normal publication aborts to avoid silently overwriting them.

## 1. Canonical Source
`main` is canonical. All long-term accepted changes must eventually be represented on `main`.

## 2. Distribution Branches
`dist/*` branches are generated distribution branches.

## 3. Temporary Field Patches
Direct commits to `dist/*` are allowed only as temporary field patches.

## 4. Non-canonical Status
Field patches are not canonical until backported to `main`.

## 5. Detection Algorithm
The publisher detects manual commits after the last generated commit.

## 6. Publisher Abortion
The publisher must abort normal publication if pending field patches exist.

## 7. Commit Trailers
Commit trailers are optional and not required.

## 8. Git Hooks
Git hooks are optional and not required.

## 9. Developer Notification
Developers should contact the repository owner or open an issue/PR when they push a field patch.

## 10. Owner Review
The owner reviews field patches and backports accepted changes to `main`.

## Developer Instructions

If you need to debug or quickly improve a distributed skill, you may commit directly to the relevant `dist/*` branch. Keep the change small and focused. Then notify the repository owner so the change can be reviewed and backported to `main`.

Commit message trailers are optional. If you want to make the intent clear, add:

```
Backport-to-main: required
```

The publisher detects field patches even without this trailer.

Do not use `dist/*` branches for long-term feature development. If a change is more than a small field patch, make it on `main` through the normal workflow.
