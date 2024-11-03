# Shopware Changelog Parser

A command-line tool to fetch and compare changelog information between different Shopware versions.

## Installation

You can install this package directly from the source:

```bash
pip install .
```

## Usage

The tool provides two main commands:

### List Available Versions

To list all available changelog versions:

```bash
sw-changelog list-versions [--repo-path ./shopware_repo]
```

### Compare Versions

To compare changelog entries between two Shopware versions:

```bash
sw-changelog compare-versions --from 6-3-1-1 --to 6-3-2-0 [--repo-path ./shopware_repo]
```

### Options

- `--repo-path`: Path where the Shopware repository will be cloned (default: ./shopware_repo)
- `--from`: Starting version for comparison (required for compare-versions)
- `--to`: Ending version for comparison (required for compare-versions)

## Requirements

- Python >= 3.8
- Git (for repository operations)

## Dependencies

- rich
- typer
- gitpython

## Example

```bash
# List all available versions
sw-changelog list-versions

# Compare changes between two versions
sw-changelog compare-versions --from 6-3-1-1 --to 6-3-2-0
```

The tool will automatically clone the Shopware repository if it doesn't exist, or update it if it does.
