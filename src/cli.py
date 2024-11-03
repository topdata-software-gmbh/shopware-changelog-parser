import typer
import git
from pathlib import Path
from InquirerPy import inquirer
from .changelog import ChangelogManager

app = typer.Typer(help="Shopware Changelog Parser", add_help_option=True, context_settings={"help_option_names": ["-h", "--help"]})

@app.command()
def list_versions(
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
):
    """List all available changelog versions."""
    manager = ChangelogManager(repo_path)
    
    # Clone or update repository
    typer.echo("Fetching repository...")
    try:
        manager.clone_or_pull_repo()
    except git.exc.GitCommandError as e:
        typer.echo(f"Error accessing repository: {e}")
        raise typer.Exit(1)

    versions = manager.get_available_versions()
    if not versions:
        typer.echo("No changelog versions found")
        raise typer.Exit(1)

    typer.echo("\nAvailable versions:")
    for version in versions:
        typer.echo(version)

@app.command()
def compare_versions(
    from_version: str = typer.Option(..., "--from", help="Starting version (e.g., 6-3-1-1)"),
    to_version: str = typer.Option(..., "--to", help="Ending version (e.g., 6-3-2-0)"),
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
):
    """Compare changelog entries between two Shopware versions."""
    manager = ChangelogManager(repo_path)

    # Clone or update repository
    typer.echo("Fetching repository...")
    try:
        manager.clone_or_pull_repo()
    except git.exc.GitCommandError as e:
        typer.echo(f"Error accessing repository: {e}")
        raise typer.Exit(1)

    # Get changelog entries for both versions
    try:
        typer.echo(f"Looking for changelog entries for version {from_version}")
        from_entries = manager.get_changelog_entries(from_version)
        
        typer.echo(f"Looking for changelog entries for version {to_version}")
        to_entries = manager.get_changelog_entries(to_version)
    except Exception as e:
        typer.echo(f"Error reading changelog entries: {e}")
        raise typer.Exit(1)

    # Display results
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

@app.command()
def parse_file(
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
):
    """Parse a single changelog file selected interactively."""
    manager = ChangelogManager(repo_path)
    
    # Clone or update repository
    typer.echo("Fetching repository...")
    try:
        manager.clone_or_pull_repo()
    except git.exc.GitCommandError as e:
        typer.echo(f"Error accessing repository: {e}")
        raise typer.Exit(1)

    # Get all changelog files
    changelog_files = manager.get_all_changelog_files()
    if not changelog_files:
        typer.echo("No changelog files found")
        raise typer.Exit(1)

    # Let user select a file
    selected_file = inquirer.select(
        message="Select a changelog file to parse:",
        choices=changelog_files,
        default=changelog_files[0] if changelog_files else None,
    ).execute()

    # Parse and display the selected file
    # try:
    parsed_content = manager.parse_changelog_file(selected_file)
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
    # except Exception as e:
    #     typer.echo(f"Error parsing changelog file: {e}")
    #     raise typer.Exit(1)

if __name__ == "__main__":
    app()
