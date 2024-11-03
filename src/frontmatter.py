from typing import Tuple, Dict, Any
import re

def load(file_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse a markdown file with YAML frontmatter.
    Returns a tuple of (metadata_dict, content_string)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split on first and second '---' markers
    parts = content.split('---', 2)
    
    if len(parts) < 3:
        # No valid frontmatter found
        return {}, content.strip()

    # Middle part is frontmatter, last part is content
    frontmatter_raw = parts[1].strip()
    content = parts[2].strip()

    # Parse frontmatter
    metadata = {}
    for line in frontmatter_raw.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Split on first ':' only
        key_value = line.split(':', 1)
        if len(key_value) != 2:
            continue
            
        key, value = key_value
        key = key.strip()
        value = value.strip()
        
        # Handle quoted values
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
            
        # Clean up @ symbols and other special characters
        value = re.sub(r'^@', '', value)  # Remove leading @
        
        metadata[key] = value

    return metadata, content

class Post:
    """
    A class representing a markdown post with frontmatter
    """
    def __init__(self, metadata: Dict[str, Any], content: str):
        self.metadata = metadata
        self.content = content
