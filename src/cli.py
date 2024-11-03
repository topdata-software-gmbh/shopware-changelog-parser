import typer
import git
from pathlib import Path
from InquirerPy import inquirer
from .changelog import ChangelogManager
from .printer import print_versions, print_version_comparison, print_changelog_file

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
    print_versions(versions)

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

    print_version_comparison(from_version, to_version, from_entries, to_entries)

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

    parsed_content = manager.parse_changelog_file(selected_file)
    print_changelog_file(parsed_content)
    # except Exception as e:
    #     typer.echo(f"Error parsing changelog file: {e}")
    #     raise typer.Exit(1)

if __name__ == "__main__":
    app()
