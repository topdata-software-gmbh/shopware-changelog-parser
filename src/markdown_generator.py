from .models import ChangelogEntry, VersionComparison

def generate_version_comparison(from_version: str, to_version: str, changelog_entries: list) -> str:
    """Generate markdown content for version comparison."""
    content = []
    content.append(f"# Changelog entries from {from_version} to {to_version}\n")
    content.append("=" * 40 + "\n")
    
    # Sort entries by date if available
    sorted_entries = sorted(changelog_entries, key=lambda x: x.date if x.date else '')
    
    for entry in sorted_entries:
        if hasattr(entry, 'date') and hasattr(entry, 'title'):
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
