import git
import os
from pathlib import Path
from typing import List, Tuple
from .models import ChangelogEntry, VersionComparison
import re
from . import frontmatter

class ChangelogManager:
    def __init__(self, repo_path: str = "./shopware_repo"):
        self.repo_path = repo_path
        self.repo_url = "https://github.com/shopware/shopware.git"

    def get_available_versions(self) -> List[str]:
        """Get all available changelog versions from the repository."""
        changelog_dir = Path(self.repo_path) / "changelog"
        if not changelog_dir.exists():
            return []
        
        versions = []
        for dir in changelog_dir.glob("release-*"):
            version = dir.name.replace("release-", "")
            versions.append(version)
        
        return sorted(versions)

    def clone_or_pull_repo(self) -> git.Repo:
        """Clone the repository if it doesn't exist, or pull if it does."""
        if os.path.exists(self.repo_path):
            repo = git.Repo(self.repo_path)
            repo.remotes.origin.pull()
            return repo
        return git.Repo.clone_from(self.repo_url, self.repo_path)

    def get_all_changelog_files(self) -> List[str]:
        """Get all changelog files from all versions."""
        changelog_base = Path(self.repo_path) / "changelog"
        if not changelog_base.exists():
            return []
        
        files = []
        for version_dir in changelog_base.glob("release-*"):
            for file in version_dir.glob("*.md"):
                # Store relative path from repo root
                rel_path = file.relative_to(self.repo_path)
                files.append(str(rel_path))
        
        return sorted(files, reverse=True)

    def parse_changelog_file(self, file_path: str) -> ChangelogEntry:
        """Parse a single changelog file and return a ChangelogEntry model."""
        full_path = Path(self.repo_path) / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Changelog file not found: {file_path}")
        
        # Parse frontmatter and content
        metadata, content = frontmatter.load(full_path)

        # Get filename components for fallback values
        filename = Path(file_path).name
        date_part = filename[:10] if len(filename) >= 10 else None

        # Extract version from file path (release-6-4-20-0/file.md -> 6.4.20.0)
        version = file_path.split('/')[1].replace('release-', '').replace('-', '.')
        
        return ChangelogEntry(
            date=metadata.get('date', date_part),
            title=metadata.get('title', metadata.get('issue', '')),
            version=version,
            content=content,
            issue=metadata.get('issue'),
            author=metadata.get('author'),
            author_email=metadata.get('author_email'),
            author_github=metadata.get('author_github')
        )

    def get_changelog_entries(self, version: str) -> List[ChangelogEntry]:
        """Get changelog entries for a specific version."""
        # Replace dots with dashes in version number
        version = version.replace('.', '-')
        changelog_dir = Path(self.repo_path) / "changelog" / f"release-{version}"
        
        if not changelog_dir.exists():
            raise FileNotFoundError(f"No changelog directory found for version {version} at {changelog_dir}")

        entries = []
        for file in changelog_dir.glob("*.md"):
            rel_path = file.relative_to(self.repo_path)
            changelog_entry = self.parse_changelog_file(str(rel_path))
            entries.append(changelog_entry)

        return sorted(entries, key=lambda x: x.date if x.date else '')

    def _version_to_tuple(self, version: str) -> tuple:
        """Convert version string to comparable tuple."""
        parts = version.replace('-', '.').split('.')
        return tuple(map(int, parts))

    def get_versions_between(self, from_version: str, to_version: str) -> List[str]:
        """Get all version folders after from_version up to and including to_version."""
        all_versions = self.get_available_versions()
        from_parts = self._version_to_tuple(from_version)
        to_parts = self._version_to_tuple(to_version)
        
        included_versions = []
        for version in all_versions:
            version_parts = self._version_to_tuple(version)
            if from_parts < version_parts <= to_parts:  # Changed <= to < for from_version comparison
                included_versions.append(version)
        
        return included_versions

    def get_markdown_files_for_versions(self, versions: List[str]) -> List[str]:
        """Get all markdown files for given versions."""
        markdown_files = []
        for version in versions:
            version_dir = Path(self.repo_path) / "changelog" / f"release-{version}"
            if version_dir.exists():
                files = [str(f.relative_to(self.repo_path)) for f in version_dir.glob("*.md")]
                markdown_files.extend(files)
        return markdown_files

    def parse_markdown_files(self, files: List[str]) -> List[ChangelogEntry]:
        """Parse markdown files and return structured data as ChangelogEntry objects."""
        parsed_entries = []
        for file_path in files:
            try:
                changelog_entry = self.parse_changelog_file(file_path)
                parsed_entries.append(changelog_entry)
            except FileNotFoundError:
                continue
        
        return sorted(parsed_entries, key=lambda x: x.date if x.date else '')

    def get_version_comparison(self, from_version: str, to_version: str) -> VersionComparison:
        """Get a VersionComparison object for the specified versions."""
        entries, _ = self.get_entries_between_versions(from_version, to_version)
        return VersionComparison(
            from_version=from_version,
            to_version=to_version,
            entries=entries
        )

    def get_entries_between_versions(self, from_version: str, to_version: str) -> Tuple[List[ChangelogEntry], List[str]]:
        """Get all changelog entries between two versions, inclusive.
        Returns tuple of (entries, parsed_files)"""
        versions = self.get_versions_between(from_version, to_version)
        markdown_files = self.get_markdown_files_for_versions(versions)
        changelog_entries = self.parse_markdown_files(markdown_files)
        return changelog_entries, markdown_files
