# Discord with GPT Integration

A powerful Discord that integrates GPT capabilities and includes features like message counting, reaction handling, and automated responses for educational purposes.

## Features

- Discord functionality with event handling
- GPT integration for intelligent responses
- Message counting system
- Reaction monitoring and handling
- Typing event tracking
- Automated scheduled tasks
- Channel and guild monitoring
- Comprehensive logging system

## Prerequisites

- Python 3.12+
- Discord Account Token
- OpenAI API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd py-discord-selfbot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```env
DISCORD_TOKEN=your_discord_token
OPENAI_API_KEY=your_openai_api_key
MONITORED_CHANNELS=channel_id1,channel_id2
MONITORED_GUILDS=guild_id1,guild_id2
```

## Project Structure

- `discord_gpt/` - GPT integration module
- `discord_selfbot/` - Core selfbot functionality
- `common/` - Shared utilities and helpers

## Usage

Run the bot using:
```bash
python count.py
```

## Features Description

### Message Counting
- Automatically tracks and responds to number sequences
- Supports continuation of counting games

### GPT Integration
- Responds to mentions using GPT
- Maintains conversation history
- Intelligent response generation

### Event Handling
- Message creation, updates, and deletion
- Reaction addition and removal
- Typing events
- Scheduled tasks

## Security Notice

⚠️ **Important**: 
- Keep your Discord token and OpenAI API key secure
- Never share your `.env` file
- Use selfbots responsibly and in accordance with Discord's terms of service

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Deployment

### VPS Setup
1. Ensure Python 3.12+ is installed on your VPS
2. Add your VPS SSH key to GitHub repository secrets:
   - VPS_HOST: Your VPS IP/hostname
   - VPS_USERNAME: SSH username
   - VPS_SSH_KEY: SSH private key

3. Run the setup script:
```bash
chmod +x setup_vps.sh
./setup_vps.sh
```

### Service Management
```bash
# Start the service
sudo systemctl start discord-bot

# Stop the service
sudo systemctl stop discord-bot

# Check status
sudo systemctl status discord-bot

# View logs
sudo journalctl -u discord-bot -f
``` 