# AGENTS.md

CLI tool (`sw-changelog`) that clones `shopware/shopware`, parses its `changelog/release-*/` markdown files, compares version ranges, and optionally sends Slack release notifications.

## Environment
- Use the checked-in `.venv` (Python 3.12, created with uv, editable install): `.venv/bin/sw-changelog ...` or `.venv/bin/python -m src.cli ...`.
- The venv has **no pip**; reinstall with `uv pip install -e .` (uv is on PATH). Refresh it after dependency changes — the editable install goes stale and imports fail with `ModuleNotFoundError`.
- No tests, linter, typecheck config, or CI exist. Verify changes by running the CLI against the local clone (plus `python -m py_compile`/`compileall` for syntax).
- `shopware_repo/` is a full clone of shopware/shopware (gitignored, large). Every command calls `clone_or_pull_repo()`, which pulls over the network — don't assume commands run offline, and don't delete the clone casually.

## Structure
- Entry point `src/cli.py` (Typer; `-h/--help`). Commands: `list-versions`, `compare-versions`, `parse-file`, `notify`.
- Flow: `ChangelogManager` (`src/changelog.py`) → pydantic `ChangelogEntry`/`VersionComparison` (`src/models.py`) → printers/formatters (`src/printer.py`, `src/formatters.py`, `src/markdown_generator.py`).
- `src/release_notifier.py` is the separate Slack path used by `notify`; it persists state in `.release-state` (gitignored JSON, `last_checked_version`). The committed `.release-state__BAK` is just a backup copy.
- The import package is literally named `src` (`sw-changelog = "src.cli:app"`); keep imports as `src.*` or relative. Don't rename it to the project name.

## Gotchas
- File paths passed to `parse_changelog_file`/`get_changelog_entries` (and returned by `get_all_changelog_files`) are relative to `repo_path`, e.g. `changelog/release-6-6-7-0/...` — do not prefix with `shopware_repo/`.
- Version args accept dashes or dots (`6-3-1-1` / `6.3.1.1`); comparisons range over `--from` **exclusive**, `--to` **inclusive**.
- Known breakage (verified): `format_original`/`format_markdown` in `src/formatters.py:12,30` call `entry.date.isoformat()`, but `ChangelogEntry.date` is deliberately `str` (invalid dates like `2020-25-10` occur, see `src/models.py:7`) → `AttributeError`. `parse-file` defaults to `original`, so it crashes as-is. `format_yaml` also prints debug output.
- `notify` requires `SLACK_TOKEN`/`SLACK_CHANNEL` env vars; `.env` is **not** auto-loaded (python-dotenv is a dependency but unused). Use exported vars or `--no-notification` for a dry run.
- `compare-versions` writes `./output/changelog.md` by default; the parent dir must already exist (`output/` is gitignored, kept via `.gitkeep`). `--stdout` skips the file.
- `src/frontmatter.py` is hand-rolled `---` splitting, not the PyPI `frontmatter` package.

## Docs
- `docs/index.md` is stale (lists nonexistent `compare`/`show` commands); trust `src/cli.py` and `README.md`.
- Follow `CONVENTIONS-PYTHON.md` (Python 3.10+, mandatory type hints) for new code, even though existing code doesn't fully comply.
- Upstream: `github.com:topdata-software-gmbh/shopware-changelog-parser`, branch `main`.
