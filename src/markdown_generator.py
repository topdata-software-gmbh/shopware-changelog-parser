def generate_version_comparison(from_version: str, to_version: str, changelog_entries: list) -> str:
    """Generate markdown content for version comparison."""
    content = []
    content.append(f"# Changelog entries from {from_version} to {to_version}\n")
    content.append("=" * 40 + "\n")
    
    for entry in changelog_entries:
        date = entry.get('date', 'No date')
        title = entry.get('title', 'No title')
        content.append(f"[{date}] {title}\n")
        
        if entry.get('issue'):
            content.append(f"  Issue: {entry['issue']}\n")
            
        entry_content = entry.get('content', '').strip()
        if entry_content:
            content.append(f"\n{entry_content}\n")
            
        author = entry.get('author')
        if author:
            content.append(f"  Author: {author}\n")
            if entry.get('author_email'):
                content.append(f"  Email: {entry['author_email']}\n")
            if entry.get('author_github'):
                content.append(f"  GitHub: {entry['author_github']}\n")
        content.append("\n")

    return "".join(content)
