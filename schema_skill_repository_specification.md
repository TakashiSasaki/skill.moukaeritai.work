# スキーマ・語彙・エージェントスキル統合リポジトリ仕様

## 1. 目的

このリポジトリは、ソフトウェア間のデータ互換性を維持するためのスキーマ、語彙、検証規則、変換規則、実装補助ツール、およびコーディングエージェント用スキルを一元管理するための正本リポジトリである。

対象とする「スキーマ」は狭義の JSON Schema に限らない。JSON Schema、RDF/Turtle、RDF/XML、JSON-LD context、SHACL shapes、SQL DDL、ORM mapping、CSVW metadata、バリデーションコード、変換コード、設計文書、コーディングエージェント向け作業手順を含む広義のデータ取り扱い仕様を対象とする。

このリポジトリの主目的は次の通りである。

1. データ構造と語彙の一次情報を明確に管理する。
2. 形式ごとの定義文書、検証コード、変換規則の相互整合性を維持する。
3. コーディングエージェントが、データ取り扱い上の取り決めを正しく参照できるようにする。
4. 下流開発者が必要なスキルだけを Git submodule として容易に取り込めるようにする。
5. 正本は単一リポジトリ・単一 `main` ブランチで管理しつつ、配布単位は細かく分割する。
6. 配布ブランチは CI により生成し、手編集による drift を防止する。

このリポジトリでは、スキルは一次情報ではない。一次情報は `specs/`、`catalog/`、`tools/`、`docs/` などに置かれるスキーマ、語彙、検証規則、設計文書である。スキルは、それらの一次情報をコーディングエージェントが適切に読解・編集・検証・生成するための操作知識である。

## 2. 設計原則

### 2.1 スキーマ・語彙ファースト

このリポジトリでは、スキーマ、語彙、検証規則、変換規則を一次情報として扱う。エージェントスキルは一次情報を代替しない。スキル内に仕様本文を重複して記述することは避ける。

スキルは、次のような役割を持つ。

- どの一次情報を読むべきかを案内する。
- どの検証ツールを実行すべきかを案内する。
- どのファイルが正本で、どのファイルが生成物かを明示する。
- コーディングエージェントが避けるべき操作を明示する。
- スキーマ編集時の作業順序、レビュー観点、検証観点を与える。

### 2.2 単一正本、複数配布物

編集正本は `main` ブランチのみとする。`main` には、すべてのスキーマ、語彙、検証ツール、カタログ、スキル、バンドル定義を置く。

一方、下流開発者が取り込むための配布物は `dist/` prefix を持つ配布ブランチとして生成する。配布ブランチは CI により生成され、人間は直接編集しない。

### 2.3 配布ブランチは orphan branch とする

各配布ブランチは、初回生成時に `main` と祖先を共有しない orphan branch として作成する。その後は同じ配布ブランチ上に通常 commit を積み、配布物としての履歴を保持する。

この方針により、配布ブランチ側で誤って `main` を merge する事故を抑制する。`main` の履歴と配布物の履歴は分離し、両者の対応関係は `bundle-lock.json` と commit message によって記録する。

### 2.4 self-contained bundle を標準とする

下流開発者は Git submodule や recursive submodule の詳細を知らない可能性がある。したがって、標準配布形態は self-contained bundle とする。

スキル配布ブランチは、スキル本体に加えて、そのスキルが必要とする最小限のスキーマ snapshot、catalog snapshot、参照文書、検証スクリプトを同梱する。nested submodule は標準配布では使わない。

### 2.5 コピーではなく生成 snapshot として扱う

配布ブランチに含まれるスキーマ、語彙、カタログ、検証ツールは、正本から CI が生成した snapshot である。人間が手でコピーしたものではない。

snapshot の出自は `references/bundle-lock.json` に記録する。これにより、bundle 内のファイルがどの `main` commit に由来するかを追跡できる。

### 2.6 deterministic generation

bundle 生成は可能な限り deterministic にする。入力 commit が同じなら生成物も同じになるべきである。

不要な差分を避けるため、生成時刻などの非決定的情報は原則として bundle に含めない。必要な場合は、release 時のみ固定値として入れるか、`SOURCE_DATE_EPOCH` 相当の仕組みを用いる。

### 2.7 symlink 非依存

配布 bundle は通常ファイルと通常ディレクトリのみで構成する。symlink は配布 bundle の必須機構にしない。

理由は、Windows 環境、Git 設定、権限、CI 環境によって symlink の扱いが不安定になり得るためである。開発者ローカル環境で installer が symlink を作ることは許容できるが、標準配布物としては symlink に依存しない。

## 3. ブランチ構成

### 3.1 正本ブランチ

```text
main
```

`main` は唯一の編集正本である。人間が通常編集するのは `main` のみである。

`main` に含める内容は次の通りである。

```text
specs/
catalog/
tools/
skills/
docs/
examples/
tests/
bundles/
.github/workflows/
```

### 3.2 配布ブランチ

配布ブランチはすべて `dist/` prefix を持つ。

例:

```text
dist/skills/json-authoring
dist/skills/rdf-vocabulary-authoring
dist/skills/schema-consistency-review

dist/specs/json-schema-core
dist/specs/rdf-vocab-core
dist/specs/shacl-core

dist/catalog/core

dist/tools/validators
dist/tools/generators
```

標準的な下流利用では、`dist/skills/<name>` を Git submodule として取り込む。

### 3.3 配布ブランチの性質

配布ブランチは次の性質を持つ。

- 初回生成時は orphan branch とする。
- `main` と祖先を共有しない。
- 人間が直接編集しない。
- CI が生成・更新する。
- 履歴は保持する。
- force-push は原則として行わない。
- 各 commit は、どの `main` commit から生成されたかを commit message と `bundle-lock.json` に記録する。

## 4. リポジトリ構成

推奨する `main` の top-level 構成は次の通りである。

```text
schema-repo/
  README.md
  LICENSE
  catalog/
    catalog.jsonld
    README.md
  specs/
    README.md
    json-schema/
    vocab/
    shacl/
    sql/
    mappings/
    csvw/
  tools/
    README.md
    validators/
    generators/
    bundle/
  skills/
    README.md
    json-authoring/
    rdf-vocabulary-authoring/
    schema-consistency-review/
  docs/
    README.md
    naming-rules.md
    versioning.md
    release-policy.md
    authoring-guide.md
  examples/
    valid/
    invalid/
  tests/
    json-schema/
    rdf/
    shacl/
    sql/
    bundles/
  bundles/
    README.md
    skills/
      json-authoring.yaml
      rdf-vocabulary-authoring.yaml
      schema-consistency-review.yaml
    specs/
      json-schema-core.yaml
    catalog/
      core.yaml
    tools/
      validators.yaml
  .github/
    workflows/
      validate.yml
      publish-bundles.yml
      nightly.yml
      release.yml
```

## 5. 各ディレクトリの役割

### 5.1 `specs/`

`specs/` は一次情報の中心である。

ここには、次のような機械可読仕様を置く。

- JSON Schema
- Turtle/RDF 語彙
- RDF/XML 形式の生成物または互換配布物
- JSON-LD context
- SHACL shapes
- SQL DDL
- ORM mapping
- CSVW metadata
- R2RML またはそれに準じる mapping

`specs/` 内のファイルは、可能な限り安定した識別子を持つ。JSON Schema であれば `$id`、RDF 語彙であれば ontology IRI、SHACL shapes graph であれば graph IRI、JSON-LD context であれば context URL を明示する。

### 5.2 `catalog/`

`catalog/` は、リポジトリ内の成果物を機械可読に索引化する。

中心ファイルは次とする。

```text
catalog/catalog.jsonld
```

catalog には、少なくとも次を記録する。

- スキーマファイル
- 語彙ファイル
- SHACL shapes
- JSON-LD context
- SQL DDL
- mapping 定義
- validator/generator
- skill
- bundle 定義
- 配布 branch
- version
- deprecated 状態
- 依存関係
- 生成物と正本の関係

catalog は可能な限り生成物とする。手編集を最小限にし、CI で freshness を検証する。

### 5.3 `tools/`

`tools/` には、検証、生成、変換、bundle 生成、release 処理に使うスクリプトを置く。

例:

```text
tools/
  validators/
    check_json_schema.py
    check_rdf.py
    check_shacl.py
    check_sql_schema.py
    check_crossrefs.py
  generators/
    generate_catalog.py
    generate_dist.py
    generate_jsonld_context.py
  bundle/
    build_bundles.py
    validate_bundle_definitions.py
    validate_generated_bundles.py
    publish_bundle_branches.py
```

GitHub Actions の YAML に複雑な検証ロジックを書かず、`tools/` に実装する。CI はこれらを呼び出すだけにする。

### 5.4 `skills/`

`skills/` には、コーディングエージェント用スキルを置く。

各 skill は原則として次の構成を持つ。

```text
skills/<skill-name>/
  SKILL.md
  references/
  scripts/
  assets/
```

`SKILL.md` はスキルの入口である。`references/` はスキルが参照する詳細文書、設計規則、読み方の説明を置く。`scripts/` はそのスキルに固有の軽量 wrapper や補助コマンドを置く。`assets/` はテンプレートや固定素材を置く。

正本スキーマ、正本語彙、共通 validator の実体は `skills/` 内に重複配置しない。それらは `specs/`、`catalog/`、`tools/` に置く。

### 5.5 `docs/`

`docs/` には人間向け説明を置く。

ここに置かれる文書は、一次情報の理解を助ける説明であり、機械可読仕様の代替ではない。ただし、命名規則、versioning policy、deprecation policy、review policy のような運用規約は `docs/` に置いてよい。

### 5.6 `examples/`

`examples/` には、正例と反例を置く。

```text
examples/
  valid/
  invalid/
```

正例はすべての該当 validator を通るべきである。反例は期待した理由で失敗するべきである。

### 5.7 `tests/`

`tests/` には、自動検証用テストを置く。

検証対象には次を含める。

- JSON Schema の metaschema 検証
- JSON example の検証
- RDF/Turtle parse 検証
- SHACL validation
- SQL DDL 実行可能性
- catalog freshness
- cross-reference consistency
- bundle definition validation
- generated bundle validation

### 5.8 `bundles/`

`bundles/` は配布 bundle 定義の正本である。

各 YAML ファイルは、どの正本ファイルをどの配布 branch にどのようなパスで含めるかを定義する。

`bundles/` 内の定義ファイルは人間が編集する。配布 branch はこれに基づいて CI が生成する。

## 6. スキルディレクトリの方針

### 6.1 `SKILL.md`

`SKILL.md` には、次を簡潔に記述する。

- スキルの目的
- いつ使うべきか
- 最初に読むべき参照文書
- 正本ファイルの場所
- 編集してよいファイルと編集してはいけないファイル
- 実行すべき検証コマンド
- よくある誤り

`SKILL.md` にスキーマ定義や語彙定義を直接大量に書かない。

### 6.2 `references/`

`references/` は、スキルが読む詳細文書の置き場である。

例:

```text
skills/json-authoring/references/
  schema-sources.md
  authoring-rules.md
  validation-rules.md
  examples.md
```

`references/` に置く文書は、スキルの作業手順を補助する。正本スキーマそのものを置く場所ではない。

### 6.3 `scripts/`

`scripts/` はスキル固有の補助スクリプトを置く。

共通 validator は原則として `tools/` に置く。スキル内 `scripts/` は、その共通 validator を呼ぶ wrapper として使う。

### 6.4 `assets/`

`assets/` はテンプレート、雛形、固定素材、コピーして使う初期ファイルなどを置く。

`assets/` には、正本スキーマ、正本語彙、正本 DDL、共通 validator を置かない。

### 6.5 独自 manifest の扱い

`references/manifest.json` のようなファイルは、Agent Skills の標準ファイルではない。必要な場合は、独自 convention であることが分かる名前を使う。

推奨名は次のいずれかである。

```text
references/schema-sources.md
references/schema-dependencies.json
references/validation-profile.json
```

これらの独自ファイルを使う場合は、`specs/json-schema/internal/` などにその JSON Schema を定義し、CI で検証する。

## 7. 配布 bundle の基本構成

`dist/skills/<name>` の配布 branch root は、原則として次の構成を持つ。

```text
SKILL.md
README.md
references/
  bundle-lock.json
  catalog.snapshot.jsonld
  specs/
  docs/
scripts/
assets/
```

### 7.1 `SKILL.md`

配布 bundle 内の `SKILL.md` は、bundle 内の相対パスだけを参照するべきである。

悪い例:

```text
../../vendor/schema-repo/specs/json-schema/core/ を参照する。
```

良い例:

```text
references/specs/json-schema/core/ を参照する。
references/bundle-lock.json で source commit を確認する。
scripts/check_json_schema.py で検証する。
```

### 7.2 `README.md`

配布 branch の `README.md` には、最低限次を記載する。

- この branch が生成物であること
- 直接編集禁止であること
- 正本は `main` にあること
- 生成元 bundle 定義ファイル
- 生成元 commit
- submodule としての取り込み方法
- 更新方法

例:

```text
This is a generated distribution branch.
Do not edit this branch directly.
Canonical sources are maintained on the main branch.
This branch is generated from bundles/skills/json-authoring.yaml.
```

### 7.3 `references/bundle-lock.json`

`bundle-lock.json` は bundle の provenance と再現性を記録する。

最低限、次を含める。

- bundle name
- bundle kind
- output branch
- source repository
- source branch
- source commit
- bundle definition path
- included files
- checksum
- generation mode
- history policy

### 7.4 `references/specs/`

`references/specs/` には、bundle が必要とする schema snapshot を置く。

これは正本ではない。正本は `main` の `specs/` にある。`references/specs/` は特定 commit から生成された配布 snapshot である。

### 7.5 `references/catalog.snapshot.jsonld`

`catalog.snapshot.jsonld` は、bundle が参照する catalog snapshot である。

初期実装では `catalog/catalog.jsonld` 全体を snapshot として含めてよい。将来的には、bundle に関係する entry だけを抽出した subset catalog にしてもよい。

### 7.6 `scripts/`

`scripts/` には、bundle 内で使える検証 wrapper を置く。

下流開発者が正本リポジトリ全体を持っていなくても、必要最小限の検証ができるようにする。

## 8. bundle 定義ファイル

### 8.1 配置

bundle 定義ファイルは `bundles/` 以下に置く。

例:

```text
bundles/skills/json-authoring.yaml
bundles/skills/rdf-vocabulary-authoring.yaml
bundles/specs/json-schema-core.yaml
bundles/tools/validators.yaml
```

### 8.2 基本形式

bundle 定義ファイルは YAML とする。

理由は次の通りである。

- 人間が読みやすい。
- コメントを書ける。
- path mapping を記述しやすい。
- YAML を JSON data model として読み込み、JSON Schema で検証できる。

### 8.3 例

```yaml
schemaVersion: 1

bundle:
  name: json-authoring
  kind: skill
  source: skills/json-authoring
  outputBranch: dist/skills/json-authoring
  description: >
    Skill bundle for authoring and validating JSON-oriented schemas
    defined by this schema repository.

version:
  deriveFrom: repository
  compatibleSchemaVersions:
    - "1.x"

include:
  - from: skills/json-authoring/
    to: ./
    mode: copy

  - from: specs/json-schema/core/
    to: references/specs/json-schema/core/
    mode: copy

  - from: specs/mappings/jsonld/core.context.jsonld
    to: references/specs/jsonld/core.context.jsonld
    mode: copy

  - from: catalog/catalog.jsonld
    to: references/catalog.snapshot.jsonld
    mode: copy

  - from: docs/naming-rules.md
    to: references/docs/naming-rules.md
    mode: copy

  - from: tools/validators/check_json_schema.py
    to: scripts/check_json_schema.py
    mode: copy

exclude:
  - "**/__pycache__/**"
  - "**/.pytest_cache/**"
  - "**/*.tmp"

generate:
  lockFile: references/bundle-lock.json
  readme: README.md

validation:
  requireFiles:
    - SKILL.md
    - references/bundle-lock.json
  run:
    - python scripts/check_json_schema.py --self-test
  checkNoBrokenRelativeLinks: true
  checkNoSymlinks: true
```

### 8.4 `schemaVersion`

bundle 定義自体のスキーマバージョンである。

初期値は `1` とする。

### 8.5 `bundle`

bundle の基本情報を記述する。

必須フィールド:

```text
bundle.name
bundle.kind
bundle.source
bundle.outputBranch
```

`bundle.kind` は初期段階では次を想定する。

```text
skill
specs
catalog
tools
```

`bundle.outputBranch` は必ず `dist/` で始まる。

### 8.6 `include`

`include` は、正本リポジトリ内のどのファイルまたはディレクトリを、bundle 内のどのパスに含めるかを定義する。

各 item は次を持つ。

```text
from
to
mode
```

初期実装では `mode: copy` のみを必須対応とする。

将来的には次を検討できる。

```text
template
generated
external-ref
```

ただし、初期段階では複雑化を避ける。

### 8.7 `exclude`

`exclude` は、include 対象から除外する glob pattern を記述する。

典型例:

```text
**/__pycache__/**
**/.pytest_cache/**
**/*.tmp
```

### 8.8 `generate`

`generate` は、bundle builder が生成する補助ファイルを指定する。

必須:

```text
generate.lockFile
```

推奨:

```text
generate.readme
```

### 8.9 `validation`

`validation` は生成後 bundle に対する検証規則である。

例:

- 必須ファイルの存在確認
- self-test 実行
- 相対リンク切れ確認
- symlink 禁止確認
- bundle-lock と branch 名の一致確認

## 9. `bundle-lock.json`

### 9.1 目的

`bundle-lock.json` は、配布 bundle の由来と内容を記録する lock file である。

これにより、下流開発者とメンテナは、bundle 内の各ファイルがどの `main` commit に由来するかを確認できる。

### 9.2 例

```json
{
  "schemaVersion": 1,
  "bundle": {
    "name": "json-authoring",
    "kind": "skill",
    "outputBranch": "dist/skills/json-authoring"
  },
  "source": {
    "repository": "https://github.com/YOUR-ORG/schema-repo",
    "branch": "main",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "bundleDefinition": "bundles/skills/json-authoring.yaml"
  },
  "generated": {
    "mode": "orphan-distribution-branch",
    "historyPolicy": "append-only"
  },
  "included": [
    {
      "from": "skills/json-authoring/",
      "to": "./",
      "sha256": "..."
    },
    {
      "from": "specs/json-schema/core/",
      "to": "references/specs/json-schema/core/",
      "sha256": "..."
    },
    {
      "from": "catalog/catalog.jsonld",
      "to": "references/catalog.snapshot.jsonld",
      "sha256": "..."
    }
  ]
}
```

### 9.3 非決定的フィールドの扱い

`generatedAt` のような生成時刻は、原則として含めない。

どうしても必要な場合は、release 時のみ固定可能な値として含める。通常の `main` push による bundle 更新では、入力が同じなら出力も同じになることを優先する。

## 10. CI 設計

### 10.1 Workflow 構成

推奨 workflow は次の通りである。

```text
validate.yml
publish-bundles.yml
nightly.yml
release.yml
```

### 10.2 `validate.yml`

`validate.yml` は、pull request と `main` push で実行する。

役割:

- JSON Schema 検証
- RDF/Turtle parse 検証
- SHACL 検証
- SQL DDL 検証
- catalog freshness 検証
- cross-reference consistency 検証
- examples 検証
- bundle definition 検証

この workflow は branch protection の required check とする。

### 10.3 `publish-bundles.yml`

`publish-bundles.yml` は、`main` push 後に bundle を生成し、`dist/*` branch を更新する。

処理順序:

```text
1. main を checkout
2. 全体検証を実行
3. bundles/**/*.yaml を検証
4. 全 bundle を一時ディレクトリに生成
5. 生成 bundle を検証
6. 対象 dist/* branch を取得
7. branch が存在しなければ orphan branch として初期化
8. branch が存在すれば通常 checkout
9. 作業ツリーを bundle 内容で完全置換
10. 差分があれば commit
11. dist/* branch に push
```

### 10.4 `nightly.yml`

`nightly.yml` は定期実行する。

役割:

- 公開 URL の生存確認
- PURL / redirect の確認
- 公開済み JSON Schema `$id` URL の確認
- 公開済み JSON-LD context URL の確認
- 外部 ontology import の確認
- GitHub Pages 生成結果の確認
- 配布 branch と `main` の祖先非共有検査

外部ネットワークに依存するため、PR の必須 check にはしない。

### 10.5 `release.yml`

`release.yml` は tag または manual dispatch で実行する。

役割:

- 完全検証
- bundle 生成
- 配布 branch 更新
- release artifact 生成
- 必要に応じた release tag 作成

## 11. 配布 branch publish algorithm

### 11.1 基本方針

配布 branch の初回作成時は orphan branch とする。以後は同じ branch に通常 commit を積む。

force-push は原則として使わない。履歴を保持する。

### 11.2 概念的な publish 処理

```bash
branch="dist/skills/json-authoring"
bundle_dir=".bundle-out/skills/json-authoring"
worktree=".worktrees/dist-skills-json-authoring"

git fetch origin "$branch" || true

if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
  git worktree add "$worktree" "origin/$branch"
else
  git worktree add --detach "$worktree"
  (
    cd "$worktree"
    git switch --orphan "$branch"
    git rm -rf . >/dev/null 2>&1 || true
  )
fi

rsync -a --delete \
  --exclude ".git" \
  "$bundle_dir"/ "$worktree"/

(
  cd "$worktree"
  git add -A

  if git diff --cached --quiet; then
    echo "No changes for $branch"
    exit 0
  fi

  git commit -m "Publish json-authoring bundle from ${GITHUB_SHA}"
  git push origin HEAD:"refs/heads/$branch"
)
```

実際の実装は Python で行う方が望ましい。複数 bundle、path validation、checksum、lock file 生成を扱いやすいためである。

### 11.3 祖先非共有検査

配布 branch は `main` と祖先を共有しないことを CI で確認する。

概念的には次を検査する。

```bash
git fetch origin main dist/skills/json-authoring

if git merge-base origin/main origin/dist/skills/json-authoring >/dev/null; then
  echo "ERROR: dist branch shares ancestry with main"
  exit 1
fi
```

この検査は nightly または publish 後に実行する。

## 12. 下流開発者向け利用方法

### 12.1 skill bundle の取り込み

下流開発者は、必要な skill bundle だけを submodule として取り込む。

例:

```bash
git submodule add -b dist/skills/json-authoring \
  https://github.com/YOUR-ORG/schema-repo.git \
  .agents/skills/json-authoring
```

### 12.2 skill bundle の更新

```bash
git submodule update --remote .agents/skills/json-authoring
git add .agents/skills/json-authoring
git commit -m "Update json-authoring skill bundle"
```

submodule は親プロジェクト内で特定 commit に pin される。`--remote` は更新時に明示的に使う。

### 12.3 recursive submodule を要求しない

標準 bundle は self-contained であり、nested submodule を使わない。

したがって、下流開発者は `git submodule update --init --recursive` を知らなくてもよい。

### 12.4 再現性

下流プロジェクトは submodule の commit を親リポジトリに記録する。これにより、どの skill bundle version を使っているかが再現可能になる。

bundle 内の `references/bundle-lock.json` から、さらにその bundle がどの `main` commit に由来するかを追跡できる。

## 13. 検証方針

### 13.1 検証の階層

検証は次の階層に分ける。

1. 構文検証
2. 識別子検証
3. 参照整合性検証
4. 生成物 freshness 検証
5. 意味的整合性検証
6. 例ベース回帰テスト
7. bundle 定義検証
8. bundle 生成物検証
9. 配布 branch 検証

### 13.2 構文検証

- JSON Schema が metaschema に合っていること
- Turtle/RDF/XML/JSON-LD が parse できること
- SHACL shapes graph が妥当であること
- SQL DDL が対象 DB で実行可能であること

### 13.3 識別子検証

- JSON Schema `$id` が規則に従うこと
- RDF term IRI が規則に従うこと
- JSON-LD context URL が安定していること
- SHACL shapes graph IRI が規則に従うこと
- SQL migration ID が一意であること
- bundle branch 名と bundle 定義が一致すること

### 13.4 参照整合性検証

- JSON Schema `$ref` の解決
- JSON-LD context term mapping の妥当性
- RDF `owl:imports` の解決
- SHACL `sh:targetClass` の対象存在確認
- SQL foreign key の対象存在確認
- ORM mapping の table/column 対応確認
- skill が参照する `references/`、`scripts/`、`specs/` の存在確認

### 13.5 生成物 freshness 検証

- catalog を再生成して差分がないこと
- JSON-LD context を再生成して差分がないこと
- RDF/XML 配布物を再生成して差分がないこと
- bundle を再生成して差分がないこと

### 13.6 意味的整合性検証

例:

- JSON Schema では required なのに SQL では nullable になっていないか
- SHACL では `xsd:integer` なのに JSON Schema では `string` になっていないか
- deprecated term が JSON-LD context で通常 term として露出していないか
- SQL constraint と SHACL constraint が明らかに矛盾していないか
- ORM mapping が語彙定義と矛盾していないか

これらは完全自動推論だけに依存せず、明示的な invariant test として書く。

### 13.7 例ベース回帰テスト

`examples/valid/` は検証に通るべきである。

`examples/invalid/` は期待した理由で失敗するべきである。

反例が意図せず通る場合、スキーマが緩すぎる可能性がある。正例が失敗する場合、スキーマまたは例のどちらかに不整合がある。

## 14. 命名規則

### 14.1 基本方針

各技術領域で許される名前の範囲は異なる。RDF/XML QName localName、Turtle PN_LOCAL、JSON property、SQL identifier、Python identifier、skill name、file path はそれぞれ制約が異なる。

したがって、すべてを単一規則に押し込めるのではなく、用途ごとに安全な subset を定義する。

### 14.2 RDF term local name

推奨する安全 subset:

```text
^[A-Za-z_][A-Za-z0-9._-]*$
```

これは RDF/XML、Turtle、JSON-LD、ファイル名、コード生成の相互運用を意識した保守的な規則である。

### 14.3 SQL column / code identifier

SQL column や Python/TypeScript への写像を強く意識する場合は、より厳しくする。

例:

```text
^[a-z][a-z0-9_]*$
```

### 14.4 skill name

skill name は lowercase letters、numbers、hyphens を基本とする。

例:

```text
json-authoring
rdf-vocabulary-authoring
schema-consistency-review
```

### 14.5 branch name

配布 branch は必ず `dist/` で始める。

例:

```text
dist/skills/json-authoring
dist/specs/json-schema-core
dist/catalog/core
dist/tools/validators
```

## 15. Versioning と release

### 15.1 正本 version

リポジトリ全体として semantic versioning 相当の release tag を持つ。

例:

```text
v1.4.0
```

### 15.2 bundle version

bundle は `main` の release version と source commit によって追跡する。

必要であれば、bundle ごとに tag を付ける。

例:

```text
skill-json-authoring-v1.4.0
specs-json-schema-core-v1.4.0
```

### 15.3 下流利用者の pinning

下流利用者は submodule commit によって bundle version を pin する。

`-b dist/skills/<name>` は更新先 branch を指定するためのものであり、親リポジトリに記録されるのは具体的な commit である。

### 15.4 破壊的変更

破壊的変更は major version を上げる。

語彙 term の意味を変更することは原則避ける。既存 term の意味を変更するより、新 term を追加し、旧 term を deprecated にする方を優先する。

## 16. Security と運用上の注意

### 16.1 配布 branch の直接編集禁止

`dist/*` branch は人間が直接編集しない。

branch protection または repository rule により、可能な限り CI 以外の push を禁止する。

### 16.2 bundle 生成時の path traversal 防止

bundle 定義の `include[].from` と `include[].to` には、次の制約を課す。

- 絶対パス禁止
- `..` による repository root 外参照禁止
- bundle root 外への出力禁止
- `.git` ディレクトリのコピー禁止
- symlink の同梱禁止または明示許可制

### 16.3 実行スクリプトの扱い

配布 bundle に `scripts/` を含める場合、下流環境で実行される可能性がある。

したがって、次を守る。

- 外部ネットワークアクセスを必要最小限にする
- destructive operation を避ける
- 実行前提を README に明記する
- self-test を用意する
- 依存ライブラリを明示する

### 16.4 署名と provenance

将来的には、release artifact、bundle lock、配布 branch commit に対して署名を検討する。

初期段階では、`bundle-lock.json`、commit message、CI log により provenance を確保する。

## 17. GitHub Actions の運用

### 17.1 required checks

`main` への merge 条件として、少なくとも次を required check にする。

```text
validate-spec-repository
catalog-current
generated-files-current
cross-reference-consistency
examples-valid
bundle-definitions-valid
```

### 17.2 publish workflow permissions

`publish-bundles.yml` は `dist/*` branch へ push するため、`contents: write` が必要である。

ただし、通常の `validate.yml` には write 権限を与えない。

### 17.3 CI bot identity

配布 branch の commit author は CI bot とする。

commit message には source commit を含める。

例:

```text
Publish json-authoring bundle

Source branch: main
Source commit: 0123456789abcdef0123456789abcdef01234567
Bundle definition: bundles/skills/json-authoring.yaml
```

## 18. 推奨される初期実装順序

### Phase 1: 正本構成の作成

- `specs/`、`catalog/`、`tools/`、`skills/`、`bundles/` を作成する。
- 最初の skill を 1 つ作る。
- 最初の bundle 定義を 1 つ作る。

### Phase 2: 検証基盤

- `tools/validate_all.py` を作る。
- JSON Schema、RDF、SHACL、catalog の最小検証を入れる。
- `validate.yml` を作る。

### Phase 3: bundle builder

- `tools/bundle/build_bundles.py` を作る。
- `bundles/skills/<name>.yaml` から一時ディレクトリへ bundle を生成する。
- `bundle-lock.json` を生成する。
- deterministic generation を確認する。

### Phase 4: orphan 配布 branch publish

- `publish_bundle_branches.py` を作る。
- 初回は orphan branch を作る。
- 以後は通常 commit を積む。
- `dist/skills/<name>` を生成する。

### Phase 5: 下流利用テスト

- 別のテストリポジトリで `git submodule add -b dist/skills/<name>` を実行する。
- コーディングエージェントが skill を discovery できるか確認する。
- bundle 内参照がすべて相対パスで解決できるか確認する。

### Phase 6: 拡張

- skill bundle を追加する。
- specs/catalog/tools bundle を必要に応じて追加する。
- catalog subset 生成を検討する。
- release workflow を追加する。

## 19. 採用しない方針

### 19.1 配布 branch を人間が直接編集する

採用しない。

理由は、`main` の正本と配布 branch の内容が drift するためである。

### 19.2 unrelated component branch を正本にする

採用しない。

各機能単位を最初から unrelated branch とし、`main` がそれらを submodule として取り込む方式は、submodule モデルとしては一貫している。しかし、関連変更を一つの PR で扱いにくくなり、複数 branch 間の更新順序、pointer 更新、CI、release 管理が複雑になる。

### 19.3 nested submodule を標準配布にする

採用しない。

下流開発者が recursive submodule を理解しているとは限らない。標準配布では self-contained bundle を提供する。

### 19.4 正本スキーマを skill `assets/` に置く

採用しない。

`assets/` はテンプレートや固定素材の置き場であり、正本スキーマや語彙の置き場ではない。

### 19.5 symlink 必須配布

採用しない。

Windows、Git 設定、権限、CI 環境で問題が起きやすいためである。

## 20. 未確定事項

次の事項は、今後の実装過程で確定する。

1. `catalog/catalog.jsonld` の詳細語彙設計。
2. bundle 定義 YAML の JSON Schema。
3. `bundle-lock.json` の JSON Schema。
4. catalog subset 生成を初期実装に含めるかどうか。
5. 配布 branch への tag 命名規則。
6. release artifact と branch 配布の関係。
7. validator scripts の依存管理方式。
8. skill bundle 内の `SKILL.md` を canonical と同一にするか、bundle 用に生成するか。
9. GitHub branch protection / repository rules の具体設定。
10. 署名や provenance attestation をいつ導入するか。

## 21. 現時点の結論

このリポジトリは、`main` を唯一の編集正本とし、`dist/*` を CI 生成の配布 branch として扱う。

スキーマ、語彙、検証規則、変換規則は `specs/`、`catalog/`、`tools/` に置く。エージェントスキルは `skills/` に置くが、仕様の重複記述は避ける。

下流開発者向けには、`dist/skills/<name>` branch を self-contained skill bundle として提供する。各 bundle は、必要最小限の schema snapshot、catalog snapshot、参照文書、検証 wrapper を含む。下流開発者は recursive submodule を使わず、単一の `git submodule add -b dist/skills/<name>` で必要な skill を取り込める。

配布 branch は orphan branch として作成し、`main` と祖先を共有しない。初回のみ orphan とし、以後は履歴を保持して通常 commit を積む。bundle の由来は `bundle-lock.json` と commit message に記録する。

この設計により、次を同時に満たす。

- 正本の一元管理
- スキーマとスキルの明確な責務分離
- 下流開発者にとっての導入容易性
- 配布単位の細分化
- recursive submodule 非依存
- CI による freshness と整合性保証
- 配布 branch の履歴追跡
- `main` 誤 merge リスクの低減

