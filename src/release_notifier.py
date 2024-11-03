import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import logging
from typing import Optional, List, Tuple
from pathlib import Path

from .changelog import ChangelogManager
from .markdown_generator import generate_version_comparison
from .models import ChangelogEntry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReleaseNotifier:
    def __init__(self, slack_token: str, channel: str):
        self.changelog_manager = ChangelogManager()
        self.slack_client = WebClient(token=slack_token)
        self.channel = channel
        
    def get_last_checked_version(self) -> Optional[str]:
        try:
            with open('releases.json', 'r') as f:
                data = json.load(f)
                return data.get('last_checked_version')
        except FileNotFoundError:
            return None
            
    def save_last_checked_version(self, version: str):
        with open('releases.json', 'w') as f:
            json.dump({'last_checked_version': version}, f)
            
    def check_and_notify(self):
        try:
            # Get latest available version
            versions = self.changelog_manager.get_available_versions()
            if not versions:
                logger.warning("No versions found")
                return
                
            latest_version = versions[0]  # Assuming versions are sorted
            last_checked = self.get_last_checked_version()
            
            logger.info(f"Latest version: {latest_version}, Last checked: {last_checked}")
            
            if not last_checked or latest_version != last_checked:
                # New version found
                logger.info(f"New version detected: {latest_version}")
                entries = self.changelog_manager.get_entries_between_versions(
                    last_checked, latest_version
                )
                
                # Generate markdown summary
                message = generate_version_comparison(
                    last_checked, 
                    latest_version, 
                    entries
                )
                
                try:
                    # Post to Slack
                    self.slack_client.chat_postMessage(
                        channel=self.channel,
                        text=f"New Shopware release: {latest_version}\n{message}"
                    )
                    logger.info("Successfully posted to Slack")
                    
                    # Only update last checked version if Slack notification succeeded
                    self.save_last_checked_version(latest_version)
                    
                except SlackApiError as e:
                    logger.error(f"Failed to post to Slack: {str(e)}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error in check_and_notify: {str(e)}")
            raise

def main():
    slack_token = os.getenv('SLACK_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL')
    
    if not slack_token or not slack_channel:
        logger.error("SLACK_TOKEN and SLACK_CHANNEL environment variables must be set")
        return 1
        
    try:
        notifier = ReleaseNotifier(slack_token, slack_channel)
        notifier.check_and_notify()
        return 0
    except Exception as e:
        logger.error(f"Failed to run notifier: {str(e)}")
        return 1

if __name__ == "__main__":
    main()