import typer
import git
import os
from pathlib import Path
from typing import List, Optional
import re

app = typer.Typer(help="Shopware Changelog Parser", add_help_option=True, context_settings={"help_option_names": ["-h", "--help"]})

def get_available_versions(repo_path: str) -> List[str]:
    """Get all available changelog versions from the repository."""
    changelog_dir = Path(repo_path) / "changelog"
    if not changelog_dir.exists():
        return []
    
    versions = []
    for dir in changelog_dir.glob("release-*"):
        version = dir.name.replace("release-", "")
        versions.append(version)
    
    return sorted(versions)

@app.command()
def list_versions(
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
):
    """List all available changelog versions."""
    # Clone or update repository
    typer.echo("Fetching repository...")
    try:
        repo = clone_or_pull_repo("https://github.com/shopware/shopware.git", repo_path)
    except git.exc.GitCommandError as e:
        typer.echo(f"Error accessing repository: {e}")
        raise typer.Exit(1)

    versions = get_available_versions(repo_path)
    if not versions:
        typer.echo("No changelog versions found")
        raise typer.Exit(1)

    typer.echo("\nAvailable versions:")
    for version in versions:
        typer.echo(version)

def clone_or_pull_repo(repo_url: str, target_dir: str) -> git.Repo:
    """Clone the repository if it doesn't exist, or pull if it does."""
    if os.path.exists(target_dir):
        repo = git.Repo(target_dir)
        repo.remotes.origin.pull()
        return repo
    return git.Repo.clone_from(repo_url, target_dir)

def get_changelog_entries(repo_path: str, version: str) -> List[dict]:
    """Get changelog entries for a specific version."""
    # Replace dots with dashes in version number
    version = version.replace('.', '-')
    changelog_dir = Path(repo_path) / "changelog" / f"release-{version}"
    
    typer.echo(f"Looking for changelog entries in: {changelog_dir}")
    if not changelog_dir.exists():
        typer.echo(f"No changelog directory found for version {version}")
        raise typer.Exit(1)

    entries = []
    for file in changelog_dir.glob("*.md"):
        # Parse date and description from filename
        match = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md", file.name)
        if match:
            date, description = match.groups()
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            entries.append({
                'date': date,
                'description': description.replace('-', ' '),
                'content': content,
                'file': file.name
            })

    return sorted(entries, key=lambda x: x['date'])

@app.command()
def compare_versions(
    from_version: str = typer.Option(..., "--from", help="Starting version (e.g., 6-3-1-1)"),
    to_version: str = typer.Option(..., "--to", help="Ending version (e.g., 6-3-2-0)"),
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
):
    """Compare changelog entries between two Shopware versions."""

    # Clone or update repository
    typer.echo("Fetching repository...")
    try:
        repo = clone_or_pull_repo("https://github.com/shopware/shopware.git", repo_path)
    except git.exc.GitCommandError as e:
        typer.echo(f"Error accessing repository: {e}")
        raise typer.Exit(1)

    # Get changelog entries for both versions
    try:
        from_entries = get_changelog_entries(repo_path, from_version)
        to_entries = get_changelog_entries(repo_path, to_version)
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

if __name__ == "__main__":
    app()
