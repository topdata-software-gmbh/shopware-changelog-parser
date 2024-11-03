from pathlib import Path
from typing import List
import json
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer
from .formatters import CHANGELOG_ENTRY_FORMATTERS, VERSION_COMPARISON_FORMATTERS



import typer
from .models import ChangelogEntry

def print_versions(versions: list):
    """Print available changelog versions."""
    if not versions:
        typer.echo("No changelog versions found")
        raise typer.Exit(1)

    typer.echo("\nAvailable versions:")
    for version in versions:
        typer.echo(version)

from .markdown_generator import generate_version_comparison

def print_version_comparison(from_version: str, to_version: str, to_entries: List[ChangelogEntry], parsed_files: list, output_file: Path = None, stdout: bool = False, format: str = "markdown"):
    """Print comparison between two versions."""
    # Always show parsed files to stdout
    typer.echo("\nParsed changelog files:")
    for file in parsed_files:
        typer.secho(f"  {file}", fg="bright_blue")

    # Generate the changelog content
    if format not in VERSION_COMPARISON_FORMATTERS:
        typer.echo(f"Unknown format: {format}. Using 'markdown'.")
        format = 'markdown'
    
    formatter = VERSION_COMPARISON_FORMATTERS[format]
    final_content = formatter(from_version, to_version, to_entries, parsed_files)

    # Output based on mode
    if stdout:
        typer.echo(final_content)
    else:
        output_file.write_text(final_content)
        typer.echo(f"\nChangelog written to: {output_file}")

def print_changelog_file(entry: ChangelogEntry, format: str = "original"):
    """Print a single changelog entry in the specified format."""
    if format not in CHANGELOG_ENTRY_FORMATTERS:
        typer.echo(f"Unknown format: {format}. Using 'original'.")
        format = "original"
    
    formatter = CHANGELOG_ENTRY_FORMATTERS[format]
    typer.echo(formatter(entry))
