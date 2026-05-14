# Distribution Branches

Distribution branches are published to `dist/*` by the CI system. They are self-contained and intended to be used as git submodules by consumers.

## Field Patches

Distribution branches are generated from `main` and are not canonical. However, in this small-team repository, direct commits to `dist/*` branches are allowed as temporary field patches.

Field patches are allowed to enable quick debugging and minor improvements by developers. They are temporary and must be backported to `main` or explicitly discarded by the repository owner.

The bundle publisher detects field patches by finding commits after the last generated commit on a `dist/*` branch. If such commits exist, normal publication aborts to avoid silently overwriting them.

Backporting should be performed by the repository owner, reviewing the field patches and applying the accepted changes to the canonical files on `main`.
