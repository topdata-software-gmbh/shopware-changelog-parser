# Shopware Changelog Parser

A command-line tool to fetch and compare changelog information between different Shopware versions. It clones (or updates) [`shopware/shopware`](https://github.com/shopware/shopware) into a local directory, parses the `changelog/release-*/` markdown files, compares version ranges, and can post Slack notifications for new releases.

> **Status: retired (October 2026).** Upstream replaced the changelog workflow in November 2025: the `changelog/release-*` tree is frozen at 6.7.4.2 on `trunk`, and current release notes live in GitHub Releases and `RELEASE_INFO-6.<minor>.md`. This tool no longer sees current releases — see [Better alternatives for the release feed](#better-alternatives-for-the-release-feed). The frozen archive (6.3 → 6.7.4.2) remains queryable with the commands below.

## Better alternatives for the release feed

Current sources (verified October 2026):

- **GitHub Releases** — Shopware publishes curated release notes for every version (critical fixes, core/storefront changes, PR links, UPGRADE link):
  - Feed, no auth: <https://github.com/shopware/shopware/releases.atom>
  - Page: <https://github.com/shopware/shopware/releases>
  - CLI: `gh release list -R shopware/shopware`
- **Slack, zero code** — with the GitHub for Slack app installed in the workspace, run in the target channel:

  ```text
  /github subscribe shopware/shopware releases
  ```

- **Slack, custom filtering** — a GitHub repo webhook (`release` event) or a small poller over `releases.atom` with a seen-set; no clone or changelog parsing needed.
- **Upgrade context for plugins** — the `sw6-upgrade-check` skill (in `ai-coding-prompts`) reads `UPGRADE-6.<minor>.md`, `RELEASE_INFO-6.<minor>.md`, and git tags/diffs directly.
- **6.6 line only** — per-release `changelog/release-6-6-*` files still ship at the release **tags** (not on `trunk`); read them with `git ls-tree -r <tag> changelog/` and `git show <tag>:changelog/...`.

Not usable as a feed: `releases.json` (EOL dates only) and the Packagist releases feed for `shopware/core` (does not exist).

## Installation

```bash
pip install .
```

For development, an editable install (this is how the checked-in `.venv` was created):

```bash
uv venv .venv
uv pip install -e .
```

After installation, use `sw-changelog ...`; in this repo use `.venv/bin/sw-changelog ...` or `.venv/bin/python -m src.cli ...`.

## Usage

These commands operate on the frozen archive (see the status note above) and remain useful for comparisons within 6.3 → 6.7.4.2.

Every command clones the repository into `--repo-path` (default `./shopware_repo`) if it is missing, or pulls it if it exists. Commands therefore require network access and may take a while on first run. Versions are accepted with dashes or dots (`6-3-1-1` or `6.3.1.1`).

All commands support `-h/--help`.

### List Available Versions

```bash
sw-changelog list-versions [--repo-path ./shopware_repo]
```

### Compare Versions

```bash
sw-changelog compare-versions --from 6-3-1-1 --to 6-3-2-0 [OPTIONS]
```

- `--from` is required; the range starts **after** it.
- `--to` is optional and **inclusive**; if omitted, the newest available version is used.
- `--output-file` (default `./output/changelog.md`) writes the comparison to a file; the parent directory must already exist.
- `--stdout` prints to stdout instead of writing a file.
- `--format` selects `markdown` (default), `json`, or `yaml`.

```bash
# Compare up to the newest available version, print to stdout
sw-changelog compare-versions --from 6-3-1-1 --stdout
```

### Parse a Single Changelog File

Interactively selects one changelog file and prints it:

```bash
sw-changelog parse-file [--repo-path ./shopware_repo] [--format original|markdown|yaml|json]
```

### Slack Notifications

> **Retired:** since `trunk` is frozen at 6.7.4.2 and the state file now sits at that boundary, this command would report "nothing new" indefinitely. Use the [alternatives above](#better-alternatives-for-the-release-feed) instead.

Checks for releases newer than the last notified version and posts a summary to Slack. Requires the `SLACK_TOKEN` and `SLACK_CHANNEL` environment variables (a `.env` file is not loaded automatically):

```bash
export SLACK_TOKEN="xoxb-your-token"
export SLACK_CHANNEL="#releases"
sw-changelog notify [--repo-path ./shopware_repo]
```

`--no-notification` performs a dry run: it checks for updates and prints the message without contacting Slack. Notification state is stored in `.release-state` (JSON, `last_checked_version`).

See [docs/slack_notifier.md](docs/slack_notifier.md) for details.

## Known Issues

- `parse-file` with the default `original` (or `markdown`) format crashes: the formatters in `src/formatters.py` call `entry.date.isoformat()`, but dates are stored as plain strings. Use `--format json` or `--format yaml` meanwhile.
- `format_yaml` prints debug output to stdout in addition to the formatted entry.

## Requirements

- Python 3.9+ (declared as `>=3.8` in `pyproject.toml`; `list[...]` annotations in `src/models.py` require 3.9)
- Git (for cloning/updating the repository)

Dependencies are declared in `pyproject.toml` and installed automatically.

Coding conventions for contributions: see [CONVENTIONS-PYTHON.md](CONVENTIONS-PYTHON.md).
