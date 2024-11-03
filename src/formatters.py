from typing import Dict, Any
from .models import ChangelogEntry
import yaml

def format_original(entry: ChangelogEntry) -> str:
    """Format entry as original markdown with frontmatter"""
    frontmatter = {
        'date': entry.date.isoformat(),
        'title': entry.title,
    }
    if entry.issue:
        frontmatter['issue'] = entry.issue
    if entry.author:
        frontmatter['author'] = entry.author
    if entry.author_email:
        frontmatter['author_email'] = entry.author_email
    if entry.author_github:
        frontmatter['author_github'] = entry.author_github
    
    yaml_front = yaml.dump(frontmatter, default_flow_style=False)
    return f"---\n{yaml_front}---\n\n{entry.content}"

def format_markdown(entry: ChangelogEntry) -> str:
    """Format entry as clean markdown"""
    parts = [f"# {entry.title}"]
    parts.append(f"\nDate: {entry.date.isoformat()}")
    if entry.issue:
        parts.append(f"\nIssue: {entry.issue}")
    if entry.author:
        parts.append(f"\nAuthor: {entry.author}")
    parts.append(f"\n{entry.content}")
    return "\n".join(parts)

def format_yaml(entry: ChangelogEntry) -> str:
     """Format entry as YAML"""
     data = entry.model_dump()
     return yaml.dump(data, default_flow_style=False)
     
FORMATTERS = {
    'original': format_original,
    'markdown': format_markdown,
    'yaml': format_yaml
}
