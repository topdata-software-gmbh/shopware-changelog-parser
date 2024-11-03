import click
import json
from typing import List

from .changelog import ChangelogManager
from .models import ChangelogEntry
from .printer import print_versions, print_version_comparison, print_changelog_file

@click.group()
def cli():
    """Changelog management tool"""
    pass

@cli.command()
def list_versions():
    """List all available versions"""
    manager = ChangelogManager()
    versions = manager.get_available_versions()
    print_versions(versions)

@cli.command()
@click.argument('from_version')
@click.argument('to_version')
@click.option('--format', '-f', type=click.Choice(['original', 'markdown', 'json']), 
              default='original', help='Output format')
def compare(from_version: str, to_version: str, format: str):
    """Compare changelog entries between two versions"""
    manager = ChangelogManager()
    to_entries = manager.get_entries_between_versions(from_version, to_version)
    
    if format == 'json':
        # Convert entries to dict and output as JSON
        entries_dict = [entry.dict() for entry in to_entries]
        print(json.dumps(entries_dict, indent=2))
    else:
        print_version_comparison(from_version, to_version, to_entries, format)

@cli.command()
@click.argument('file_path')
@click.option('--format', '-f', type=click.Choice(['original', 'markdown', 'json']), 
              default='original', help='Output format')
def show(file_path: str, format: str):
    """Show contents of a changelog file"""
    manager = ChangelogManager()
    entry = manager.parse_changelog_file(file_path)
    
    if format == 'json':
        print(json.dumps(entry.dict(), indent=2))
    else:
        print_changelog_file(entry, format)

if __name__ == '__main__':
    cli()
