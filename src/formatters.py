from typing import Dict, Any
from .models import ChangelogEntry
import yaml
import json
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, YamlLexer

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
     yaml_str = yaml.dump(data, default_flow_style=False)
     return highlight(yaml_str, YamlLexer(), TerminalFormatter())

def format_json(entry: ChangelogEntry) -> str:
     """Format entry as JSON"""
     data = entry.model_dump()
     json_str = json.dumps(data, indent=4, default=str)
     return highlight(json_str, JsonLexer(), TerminalFormatter())
     
FORMATTERS = {
    'original': format_original,
    'markdown': format_markdown,
    'yaml': format_yaml,
    'json': format_json
}
