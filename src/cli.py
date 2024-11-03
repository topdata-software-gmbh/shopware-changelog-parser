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
    output_file: Path = typer.Option("./output/changelog.md", help="Output file path for changelog"),
    stdout: bool = typer.Option(False, "--stdout", help="Print changelog to stdout instead of file"),
    format: str = typer.Option("markdown", help="Output format (markdown, json)"),
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

    # Get changelog entries between versions
    typer.echo(f"Looking for changelog entries between versions {from_version} and {to_version}")
    entries, parsed_files = manager.get_entries_between_versions(from_version, to_version)


    print_version_comparison(from_version, to_version, entries, parsed_files, output_file, stdout, format)

@app.command()
def parse_file(
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
    format: str = typer.Option("original", help="Output format (original, markdown, yaml, json)"),
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
    print_changelog_file(parsed_content, format)
    # except Exception as e:
    #     typer.echo(f"Error parsing changelog file: {e}")
    #     raise typer.Exit(1)

if __name__ == "__main__":
    app()
