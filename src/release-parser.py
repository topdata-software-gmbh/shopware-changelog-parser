import json
from markdown_it import MarkdownIt
from markdown_it.token import Token


def parse_release_changes(body):
    # Initialize markdown parser
    md = MarkdownIt()
    tokens = md.parse(body)

    changes = []
    current_item = None
    
    for token in tokens:
        if token.type == 'bullet_list_open':
            continue
            
        # Look for list items
        if token.type == 'list_item_open':
            current_item = {'title': '', 'markdown_link': '', 'author': 'No author specified'}
            continue

        if token.type == 'inline' and current_item is not None:
            content = token.content
            
            # Look for markdown links
            if '[' in content and '](' in content and ')' in content:
                # Extract the link
                link_start = content.find('](') + 2
                link_end = content.find(')', link_start)
                link = content[link_start:link_end]
                
                if link.endswith('.md'):
                    current_item['markdown_link'] = link
                    
                    # Extract title - everything before the link
                    title_start = content.find('[') + 1
                    title_end = content.find(']')
                    if title_start > 0 and title_end > title_start:
                        current_item['title'] = content[title_start:title_end].strip()
            
            # Look for author information
            if '(' in content and ')' in content:
                # Find the last set of parentheses
                start = content.rfind('(') + 1
                end = content.rfind(')')
                if start > 0 and end > start:
                    author = content[start:end].strip()
                    if author and not author.startswith('http'):  # Avoid URLs
                        current_item['author'] = author

        if token.type == 'list_item_close' and current_item is not None:
            if current_item['markdown_link']:  # Only add items with markdown links
                changes.append(current_item)
            current_item = None

    return changes


def process_github_release(release_data):
    body = release_data.get('body', '')
    version = release_data.get('tag_name', '')
    changes = parse_release_changes(body)

    print(f"\nChanges in version {version}:")
    print("-" * 50)

    for change in changes:
        print(f"Title: {change['title']}")
        print(f"Markdown: {change['markdown_link']}")
        print(f"Author: {change['author']}")
        print("-" * 30)

    return changes


if __name__ == "__main__":
    # First install required package:
    # pip install markdown-it-py

    # Example usage with releases data
    with open('../releases.json', 'r') as f:
        releases = json.load(f)

    all_changes = []
    for release in releases:
        changes = process_github_release(release)
        all_changes.extend(changes)

    # Optionally save to file
    with open('../parsed_changes.json', 'w') as f:
        json.dump(all_changes, f, indent=2)
