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

class ReleaseChecker:
    def __init__(self, state_file: str = '.release-state'):
        self.changelog_manager = ChangelogManager()
        self.state_file = state_file
        
    def get_last_checked_version(self) -> Optional[str]:
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return data.get('last_checked_version')
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {self.state_file}")
            return None
            
    def save_last_checked_version(self, version: str):
        with open(self.state_file, 'w') as f:
            json.dump({'last_checked_version': version}, f)
            
    def check_for_updates(self) -> Tuple[Optional[str], Optional[str], Optional[List[ChangelogEntry]], Optional[str]]:
        """Returns (latest_version, last_checked_version, changelog_entries, formatted_message)"""
        try:
            versions = self.changelog_manager.get_available_versions()
            if not versions:
                logger.warning("No versions found")
                return None, None, None, None
                
            latest_version = versions[-1]  # Get the newest version (last in the list)
            last_checked = self.get_last_checked_version()
            
            logger.info(f"Latest version: {latest_version}, Last checked: {last_checked}")
            
            if not last_checked or latest_version != last_checked:
                entries, parsed_files = self.changelog_manager.get_entries_between_versions(
                    last_checked if last_checked else versions[0],  # If no last_checked, start from oldest
                    latest_version
                )
                
                message = generate_version_comparison(
                    last_checked if last_checked else versions[0],
                    latest_version, 
                    entries
                )
                
                return latest_version, last_checked, entries, message
                
            return latest_version, last_checked, None, None
            
        except Exception as e:
            logger.error(f"Error checking for updates: {str(e)}")
            raise

class NotificationService:
    def __init__(self, slack_token: str, channel: str):
        self.slack_client = WebClient(token=slack_token)
        self.channel = channel
        
    def notify(self, version: str, message: str, no_notification: bool = False) -> bool:
        notification_text = f"New Shopware release: {version}\n{message}"
        
        # Print notification to console
        print(notification_text)
        logger.info("Notification printed to console")
        
        if not self.channel:
            return True
            
        if no_notification:
            logger.info("NO NOTIFICATION: Would send to Slack:")
            logger.info(f"Channel: {self.channel}")
            logger.info("Message:")
            logger.info(notification_text)
            return True
            
        try:
            self.slack_client.chat_postMessage(
                channel=self.channel,
                text=notification_text
            )
            logger.info("Successfully posted to Slack")
            return True
        except SlackApiError as e:
            logger.error(f"Failed to post to Slack: {str(e)}")
            return False

class ReleaseNotifier:
    def __init__(self, slack_token: str, channel: str):
        self.checker = ReleaseChecker()
        self.notifier = NotificationService(slack_token, channel)
        
    def check_and_notify(self, no_notification: bool = False):
        try:
            latest_version, last_checked, entries, message = self.checker.check_for_updates()
            
            if message and latest_version:
                if self.notifier.notify(latest_version, message, no_notification):
                    self.checker.save_last_checked_version(latest_version)
                        
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
