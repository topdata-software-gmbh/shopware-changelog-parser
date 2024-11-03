# Slack Notifier

The Slack notifier is a component that automatically checks for new Shopware releases and posts notifications to a specified Slack channel.

## Configuration

### Environment Variables

The following environment variables must be set:

- `SLACK_TOKEN`: Your Slack API token
- `SLACK_CHANNEL`: The channel where notifications should be posted

### Example Configuration

```bash
export SLACK_TOKEN="xoxb-your-token"
export SLACK_CHANNEL="#releases"
```

## Usage

### Manual Testing

You can manually test the Slack notification system using the CLI:

```bash
python -m changelog notify
```

### Automated Notifications

Set up a cron job to run the notifier automatically. Example crontab entry to run daily at 9 AM:

```bash
0 9 * * * cd /path/to/project && python -m changelog notify
```

## How It Works

1. The notifier checks for new Shopware releases
2. If a new version is found, it:
   - Generates a markdown summary of changes
   - Posts the summary to the configured Slack channel
   - Updates the last checked version

## Error Handling

- The system logs all activities and errors
- If Slack notification fails, the last checked version is not updated
- This ensures no releases are missed due to temporary failures

## Troubleshooting

Common issues:

1. Environment variables not set
   - Ensure both `SLACK_TOKEN` and `SLACK_CHANNEL` are set
   - Verify the token has required permissions

2. Slack API errors
   - Check the logs for detailed error messages
   - Verify the channel exists and the bot has access

3. Version tracking issues
   - Check the `releases.json` file for current state
   - Delete `releases.json` to reset version tracking
