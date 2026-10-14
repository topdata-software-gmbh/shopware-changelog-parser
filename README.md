# Shopware Changelog Parser

A command-line tool to fetch and compare changelog information between different Shopware versions. It clones (or updates) [`shopware/shopware`](https://github.com/shopware/shopware) into a local directory, parses the `changelog/release-*/` markdown files, compares version ranges, and can post Slack notifications for new releases.

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
