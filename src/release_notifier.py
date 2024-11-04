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
                if isinstance(data, dict):
                    return data.get('last_checked_version')
                elif isinstance(data, list):
                    # Handle case where file contains a list
                    return data[0] if data else None
                else:
                    logger.warning(f"Unexpected data format in releases.json: {type(data)}")
                    return None
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            logger.error("Invalid JSON in releases.json")
            return None
            
    def save_last_checked_version(self, version: str):
        with open('releases.json', 'w') as f:
            json.dump({'last_checked_version': version}, f)
            
    def check_and_notify(self, dry_run: bool = False):
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
                entries, parsed_files = self.changelog_manager.get_entries_between_versions(
                    last_checked, latest_version
                )
                
                # Generate markdown summary
                message = generate_version_comparison(
                    last_checked, 
                    latest_version, 
                    entries
                )
                
                try:
                    # Print notification to console
                    print(f"New Shopware release: {latest_version}\n{message}")
                    logger.info("Notification printed to console")
                
                    # Try to post to Slack if credentials are set and not in dry-run mode
                    if self.channel:
                        notification_text = f"New Shopware release: {latest_version}\n{message}"
                        if dry_run:
                            logger.info("DRY RUN: Would send to Slack:")
                            logger.info(f"Channel: {self.channel}")
                            logger.info("Message:")
                            logger.info(notification_text)
                        else:
                            try:
                                self.slack_client.chat_postMessage(
                                    channel=self.channel,
                                    text=notification_text
                                )
                                logger.info("Successfully posted to Slack")
                                # Only update last checked version if Slack notification succeeded
                                self.save_last_checked_version(latest_version)
                            except SlackApiError as e:
                                logger.error(f"Failed to post to Slack: {str(e)}")
                    
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
        
    if slack_token and slack_channel:
        try:
            notifier = ReleaseNotifier(slack_token, slack_channel)
            notifier.check_and_notify()
        except Exception as e:
            logger.error(f"Failed to run notifier: {str(e)}")
    logger.info("No Slack credentials set, skipping notification")
    return 0

if __name__ == "__main__":
    main()
