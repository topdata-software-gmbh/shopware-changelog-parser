import typer

def print_versions(versions: list):
    """Print available changelog versions."""
    if not versions:
        typer.echo("No changelog versions found")
        raise typer.Exit(1)

    typer.echo("\nAvailable versions:")
    for version in versions:
        typer.echo(version)

def print_version_comparison(from_version: str, to_version: str, from_entries: list, to_entries: list):
    """Print comparison between two versions."""
    typer.echo(f"\nChanges from version {from_version} to {to_version}:\n")

    typer.echo(f"Changes in {from_version}:")
    typer.echo("=" * 40)
    for entry in from_entries:
        typer.echo(f"[{entry['date']}] {entry['description']}")
        if entry['content']:
            typer.echo(f"  {entry['content']}\n")

    typer.echo(f"\nChanges in {to_version}:")
    typer.echo("=" * 40)
    for entry in to_entries:
        typer.echo(f"[{entry['date']}] {entry['description']}")
        if entry['content']:
            typer.echo(f"  {entry['content']}\n")

def print_changelog_file(parsed_content: dict):
    """Print parsed changelog file content."""
    typer.echo("\nParsed content:")
    typer.echo("=" * 40)
    typer.echo(f"Date: {parsed_content['date']}")
    typer.echo(f"Title: {parsed_content['title']}")
    typer.echo(f"Issue: {parsed_content['issue']}")
    if parsed_content['author']:
        typer.echo(f"Author: {parsed_content['author']}")
    if parsed_content['author_email']:
        typer.echo(f"Author Email: {parsed_content['author_email']}")
    if parsed_content['author_github']:
        typer.echo(f"Author Github: {parsed_content['author_github']}")
    typer.echo(f"Content:\n{parsed_content['content']}")
