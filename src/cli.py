import typer
import git
import json
import os
from pathlib import Path
from InquirerPy import inquirer
from .changelog import ChangelogManager
from .printer import print_versions, print_version_comparison, print_changelog_file
from .release_notifier import ReleaseNotifier

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
    to_version: str = typer.Option(None, "--to", help="Ending version (e.g., 6-3-2-0). Defaults to newest version."),
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

    # If no to_version specified, use the newest available version
    if to_version is None:
        versions = manager.get_available_versions()
        to_version = versions[-1]  # Get the last (newest) version
        typer.echo(f"No target version specified. Using newest version: {to_version}")

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

@app.command()
def notify(
    repo_path: str = typer.Option("./shopware_repo", help="Path to clone/store the repository"),
    no_notification: bool = typer.Option(False, "--no-notification", help="Check for updates without sending notifications"),
):
    """Check for new versions and send Slack notifications"""
    if not no_notification:
        slack_token = os.getenv('SLACK_TOKEN')
        slack_channel = os.getenv('SLACK_CHANNEL')
        
        missing_vars = []
        if not slack_token:
            missing_vars.append("SLACK_TOKEN")
        if not slack_channel:
            missing_vars.append("SLACK_CHANNEL")
            
        if missing_vars:
            typer.echo("Error: The following environment variables are required but not set:")
            for var in missing_vars:
                typer.echo(f"  - {var}")
            typer.echo("\nPlease set them using:")
            typer.echo("  export SLACK_TOKEN='your-slack-token'")
            typer.echo("  export SLACK_CHANNEL='your-channel-name'")
            raise typer.Exit(1)
    else:
        # Use dummy values for dry-run
        slack_token = "dry-run-token"
        slack_channel = "dry-run-channel"
    
    notifier = ReleaseNotifier(slack_token, slack_channel)
    notifier.check_and_notify(no_notification=no_notification)
    if no_notification:
        typer.echo("Check complete - no notifications were sent")
    else:
        typer.echo("Notification check complete")

if __name__ == "__main__":
    app()
