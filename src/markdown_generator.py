from .models import ChangelogEntry, VersionComparison

def generate_version_comparison(from_version: str, to_version: str, changelog_entries: list[ChangelogEntry]) -> str:
    """Generate markdown content for version comparison."""
    content = []
    content.append(f"# Changelog entries from {from_version} to {to_version}\n")
    content.append("=" * 40 + "\n")
    
    for entry in changelog_entries:
        content.append(f"[{entry.date}] {entry.title}\n")
        
        if entry.issue:
            content.append(f"  Issue: {entry.issue}\n")
            
        if entry.content.strip():
            content.append(f"\n{entry.content.strip()}\n")
            
        if entry.author:
            content.append(f"  Author: {entry.author}\n")
            if entry.author_email:
                content.append(f"  Email: {entry.author_email}\n")
            if entry.author_github:
                content.append(f"  GitHub: {entry.author_github}\n")
        content.append("\n")

    return "".join(content)
