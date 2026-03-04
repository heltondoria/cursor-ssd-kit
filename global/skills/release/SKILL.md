---
name: release
description: Create a semver release with version bump, changelog, and git tag (commitizen + git-cliff)
argument-hint: "[--dry-run] [--major | --minor | --patch] [--pre <label>]"
---

# Release

Create a semver release with version bump, changelog (Keep a Changelog), git tag, and push.
Uses commitizen for bump and git-cliff for changelog.

**Pipeline position**: `... -> /quality-gates -> /impl-review -> **`/release`**`

## Input

Parse `$ARGUMENTS`:
- `--dry-run`: simulate everything without modifying files (uses `cz bump --dry-run`)
- `--major`, `--minor`, `--patch`: force increment type (overrides automatic detection)
- `--pre <label>`: pre-release (e.g., `--pre alpha` produces `v1.2.0-alpha.1`)
- No arguments: automatic increment detection via conventional commits

---

## Phase 1: Pre-flight Checks

Run these checks in order. Abort on first failure unless noted.

### 1.1 Git repository

Verify we are inside a git repository (`git rev-parse --is-inside-work-tree`).
If not, abort: "Not a git repository. Run this skill from a project root."

### 1.2 Clean working directory

Run `git status --porcelain`. If output is non-empty, abort:
"Commit or stash your changes before releasing."

### 1.3 Branch check

Get current branch (`git branch --show-current`).
- If `main` or `master`: proceed silently.
- Otherwise: print warning "You are on branch `<name>`, not main/master. Proceeding anyway."

### 1.4 Tools installed

Check that both tools are available:

1. `cz version` — if fails: "commitizen not found. Install: `pipx install commitizen`"
2. `git cliff --version` — if fails: "git-cliff not found. Install: `pipx install git-cliff` or `cargo install git-cliff`"

If `cz` is missing, abort. If only `git-cliff` is missing, print warning:
"git-cliff not found. Will use commitizen built-in changelog as fallback."

### 1.5 Existing tags

Run `git tag --list 'v*'`.
- If no tags found: inform "No previous tags found. This will be the first release."

### 1.6 Commits since last tag

```bash
git log $(git describe --tags --abbrev=0 2>/dev/null)..HEAD --oneline
```
(If no tags exist, use `git log --oneline`.)

If zero commits, abort: "No new commits since last release."

### 1.7 Commitizen configuration

Check if commitizen is configured:
- `[tool.commitizen]` section in `pyproject.toml`, OR
- `.cz.toml` exists, OR
- `package.json` has a `"commitizen"` key

If no config found, run **Phase 1b** to auto-configure.

### Phase 1b: Auto-configure commitizen

Detect stack and create minimal configuration:

**Python** (`pyproject.toml` exists):

Add section to `pyproject.toml`:
```toml
[tool.commitizen]
name = "cz_conventional_commits"
version_provider = "pep621"
version_scheme = "semver"
tag_format = "v$version"
update_changelog_on_bump = false
bump_message = "chore(release): bump version $current_version → $new_version"
```

If `[project].version` does not exist in pyproject.toml, add `version = "0.0.0"` under `[project]`.

Note: `update_changelog_on_bump = false` because we use git-cliff for changelog.

**TypeScript** (`package.json` exists, no `pyproject.toml`):

Ensure `package.json` has a `"version"` field. If missing, add `"version": "0.0.0"`.

Create `.cz.json`:
```json
{
  "commitizen": {
    "name": "cz_conventional_commits",
    "version_provider": "npm",
    "version_scheme": "semver",
    "tag_format": "v$version",
    "bump_message": "chore(release): bump version $current_version → $new_version"
  }
}
```

**Both exist** (monorepo):

Use `pyproject.toml` as primary. Add `version_files = ["package.json:version"]` to the
`[tool.commitizen]` section to keep both in sync.

After auto-configuring, show the user what was created and ask for confirmation before proceeding.

---

## Phase 2: Version Bump

### 2.1 Preview (always)

Run `cz bump --dry-run` and display:

```
Version Bump Preview
====================
Current version:  1.2.3
Increment:        MINOR (detected from commits)
New version:      1.3.0
Tag:              v1.3.0

Commits included:
  feat(F6): implement task export service
  fix(F6): correct export encoding
  test(F6): add task export tests
  docs(F6): update API documentation
```

### 2.2 Dry-run exit

If `--dry-run` was passed: stop here. Show preview and exit with the dry-run output
(see **Output Final** section).

### 2.3 Confirmation

Ask the user: "Proceed with release v1.3.0? (y/n)"

### 2.4 Execute bump

Build the `cz bump` command with appropriate flags:

```bash
cz bump --yes --no-verify [FLAGS]
```

Additional flags based on arguments:
- `--major` -> `cz bump --increment MAJOR`
- `--minor` -> `cz bump --increment MINOR`
- `--patch` -> `cz bump --increment PATCH`
- `--pre <label>` -> `cz bump --prerelease <label>`

The `--no-verify` flag is used **only** on the bump commit to prevent lint hooks from
blocking the version-bump commit. All other commits in the pipeline go through hooks normally.

Commitizen will:
1. Update version in `pyproject.toml` / `package.json`
2. Create a commit: `chore(release): bump version 1.2.3 → 1.3.0`
3. Create a git tag: `v1.3.0`

If bump fails with "No bumpable commits found", inform:
"No bumpable commits found. Only fix/feat/BREAKING commits trigger a version bump."

---

## Phase 3: Changelog

### 3.1 Generate changelog

If git-cliff is available:
```bash
git cliff --output CHANGELOG.md
```

This generates a complete CHANGELOG.md (all releases from tag history), not incremental.

If git-cliff is **not** available (fallback):
```bash
cz changelog
```

### 3.2 Detect manual changelog

If `CHANGELOG.md` already existed before this release, check if it was generated by git-cliff
(look for `<!-- generated by git-cliff -->` or similar marker). If it appears to be manually
written (no marker found), warn the user and ask for confirmation before overwriting.

### 3.3 Amend bump commit

Include the updated CHANGELOG.md in the bump commit:

```bash
git add CHANGELOG.md
git commit --amend --no-edit --no-verify
```

### 3.4 Recreate tag

Since the commit changed, the tag must be recreated:

```bash
git tag -d v<version>
git tag -a v<version> -m "release: v<version>"
```

The annotated tag includes a meaningful message with the `release:` prefix.

---

## Phase 4: Push

### 4.1 Release summary

Display:

```
Release Summary
===============
Version:    v1.3.0
Tag:        v1.3.0 (annotated)
Changelog:  CHANGELOG.md updated
Commits:    4 commits included in this release

Files modified:
  pyproject.toml   (version: 1.2.3 → 1.3.0)
  CHANGELOG.md     (new release section added)
```

### 4.2 Push confirmation

Ask: "Push tag and commit to remote? (y/n)"

- **Yes**: `git push && git push --tags`
- **No**: "Release created locally. Push when ready: `git push && git push --tags`"

**Never** force push. If the tag already exists on the remote, abort with:
"Tag v1.3.0 already exists on remote. Delete it manually if you want to re-release."

---

## Output

### Successful release

```
Release Complete
================
Version:     v1.3.0
Tag:         v1.3.0
Changelog:   CHANGELOG.md
Pushed:      yes / no

Next steps:
  - Create GitHub/GitLab release from tag (if desired)
  - Publish package: `uv publish` (Python) or `npm publish` (TypeScript)
```

### Dry-run

```
Release Preview (dry-run)
=========================
Version:     v1.3.0 (not created)
Increment:   MINOR
Commits:     4 since v1.2.3

No files were modified.
```

---

## Reminders

- Always run `cz bump --dry-run` before the real bump
- Never force push (`--force`) — if the tag already exists on remote, abort
- If bump fails (no bumpable commits), inform the user clearly
- If git-cliff is not installed, fall back to commitizen's built-in changelog (`cz changelog`)
- If an existing CHANGELOG.md appears manually written, warn before overwriting

## Commit

This skill does **not** create a separate commit — commitizen creates the bump commit.
The only modification is the amend to include CHANGELOG.md.

Commit format (customized via `bump_message`):
- `chore(release): bump version 1.2.3 → 1.3.0`

Tag format (annotated):
- Tag name: `v1.3.0`
- Tag message: `release: v1.3.0`
