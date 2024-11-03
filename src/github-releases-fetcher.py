import requests
import json
from datetime import datetime

def fetch_shopware_releases():
    # GitHub API endpoint for Shopware releases
    url = "https://api.github.com/repos/shopware/shopware/releases"
    
    # Headers to get JSON response
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse JSON response
        releases = response.json()
        
        # Print each release's information
        for release in releases:
            published_at = datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ')
            formatted_date = published_at.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\nRelease: {release['name']}")
            print(f"Tag: {release['tag_name']}")
            print(f"Published: {formatted_date}")
            print(f"URL: {release['html_url']}")
            print("-" * 50)
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching releases: {e}")

if __name__ == "__main__":
    fetch_shopware_releases()
