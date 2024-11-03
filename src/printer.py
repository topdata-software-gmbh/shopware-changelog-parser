from pathlib import Path
from typing import List

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

def print_version_comparison(from_version: str, to_version: str, to_entries: List[ChangelogEntry], parsed_files: list, output_file: Path = None, stdout: bool = False):
    """Print comparison between two versions."""
    # Always show parsed files to stdout
    typer.echo("\nParsed changelog files:")
    for file in parsed_files:
        typer.secho(f"  {file}", fg="bright_blue")

    # Generate the changelog content
    final_content = generate_version_comparison(from_version, to_version, to_entries)

    # Output based on mode
    if stdout:
        typer.echo(final_content)
    else:
        output_file.write_text(final_content)
        typer.echo(f"\nChangelog written to: {output_file}")

def print_changelog_file(entry: ChangelogEntry):
    """Print parsed changelog file content."""
    typer.echo("\nParsed content:")
    typer.echo("=" * 40)
    typer.echo(f"Date: {entry.date}")
    typer.echo(f"Title: {entry.title}")
    typer.echo(f"Version: {entry.version}")
    if entry.issue:
        typer.echo(f"Issue: {entry.issue}")
    if entry.author:
        typer.echo(f"Author: {entry.author}")
    if entry.author_email:
        typer.echo(f"Author Email: {entry.author_email}")
    if entry.author_github:
        typer.echo(f"Author Github: {entry.author_github}")
    typer.echo(f"Content:\n{entry.content}")
