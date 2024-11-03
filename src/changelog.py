import git
import os
from pathlib import Path
from typing import List
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

    def parse_changelog_file(self, file_path: str) -> dict:
        """Parse a single changelog file and return structured content."""
        full_path = Path(self.repo_path) / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Changelog file not found: {file_path}")
        
        # Parse frontmatter and content
        metadata, content = frontmatter.load(full_path)

        # Get filename components for fallback values
        filename = Path(file_path).name
        date_part = filename[:10] if len(filename) >= 10 else None

        return {
            'date': metadata.get('date', date_part),  # Use frontmatter date if available, fallback to filename
            'title': metadata.get('title', metadata.get('issue', '')),  # Use frontmatter title/issue if available
            'content': content,
            'file': file_path,
            'issue': metadata.get('issue', ''),
            'author': metadata.get('author', ''),
            'author_email': metadata.get('author_email', ''),
            'author_github': metadata.get('author_github', ''),
            'metadata': metadata  # Include all frontmatter metadata
        }

    def get_changelog_entries(self, version: str) -> List[dict]:
        """Get changelog entries for a specific version."""
        # Replace dots with dashes in version number
        version = version.replace('.', '-')
        changelog_dir = Path(self.repo_path) / "changelog" / f"release-{version}"
        
        if not changelog_dir.exists():
            raise FileNotFoundError(f"No changelog directory found for version {version} at {changelog_dir}")

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
