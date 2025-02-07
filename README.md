# Discord Selfbot with GPT Integration

A powerful Discord selfbot that integrates GPT capabilities for intelligent interactions, message handling, and automated responses. Built with Python for educational purposes.

## ⚡ Features

- 🤖 Advanced Discord selfbot functionality
  - Message handling and event tracking
  - Reaction monitoring and management
  - Typing event detection
  - Channel and guild monitoring
- 🧠 GPT Integration
  - Smart conversation handling
  - Context-aware responses
  - Customizable AI personality
- 📊 Message Analytics
  - Message counting and tracking
  - User interaction statistics
  - Channel activity monitoring
- 🔄 Automated Tasks
  - Scheduled message sending
  - Periodic status updates
  - Custom automation workflows
- 📝 Comprehensive Logging
  - Detailed event logging
  - Error tracking
  - Activity monitoring

## 🚀 Prerequisites

- Python 3.12 or higher
- Discord Account Token
- OpenAI API Key
- SQLite (for database)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/py-discord-selfbot.git
cd py-discord-selfbot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_token
OPENAI_API_KEY=your_openai_api_key
MONITORED_CHANNELS=channel_id1,channel_id2
MONITORED_GUILDS=guild_id1,guild_id2
LOG_LEVEL=INFO
DB_PATH=db/discord.db
```

## 📁 Project Structure

```
py-discord-selfbot/
├── discord_gpt/           # GPT integration module
│   ├── client.py         # GPT client implementation
│   └── db/              # GPT-related database
├── discord_selfbot/       # Core selfbot functionality
│   ├── client.py        # Discord client implementation
│   ├── models.py        # Data models
│   └── logger.py        # Logging configuration
├── db/                   # SQLite database
├── requirements.txt      # Project dependencies
└── .env                 # Environment configuration
```

## 🎮 Usage

1. Basic bot startup:
```bash
python example.py
```

2. With custom configuration:
```bash
LOG_LEVEL=DEBUG python example.py
```

## 💡 Example Usage

Check `example.py` in the root directory for a complete implementation example.

### Basic Features

1. Message Handling:
```python
from discord_selfbot import DiscordSelfBot
from discord_selfbot.models import Message, EventType

# Initialize the bot
bot = DiscordSelfBot(
    token="your_discord_token",
    monitored_channels=[channel_id1, channel_id2],
    monitored_guilds=[guild_id1, guild_id2],
    debug=False
)

@bot.on_event(EventType.MESSAGE_CREATE)
async def handle_message(message: Message):
    if message.author.id == bot.user.id:
        return
    # Your message handling logic here
    print(f"Received message: {message.content}")
```

2. GPT Integration:
```python
from discord_gpt import GPTClient

# Initialize the bot with GPT integration
bot = DiscordSelfBot(
    token="your_discord_token",
    monitored_channels=[channel_id1, channel_id2],
    debug=False
)
gpt_client = GPTClient(api_key="your_openai_api_key")

@bot.on_event(EventType.MESSAGE_CREATE)
async def handle_gpt_message(message: Message):
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            response = await gpt_client.get_response(message.content)
            await bot.send_message(message.channel_id, response)
```

3. Reaction Handling:
```python
from discord_selfbot.models import Reaction

@bot.on_event(EventType.MESSAGE_REACTION_ADD)
async def handle_reaction(reaction: Reaction):
    if reaction.user_id == bot.user.id:
        return
    # Your reaction handling logic here
    print(f"Reaction added: {reaction.emoji}")
```

4. Typing Event Detection:
```python
from discord_selfbot.models import TypingEvent

@bot.on_event(EventType.TYPING_START)
async def handle_typing(typing: TypingEvent):
    if typing.user_id == bot.user.id:
        return
    print(f"User {typing.user_id} is typing in channel {typing.channel_id}")
```

To start the bot:
```python
if __name__ == "__main__":
    bot.run()
```

## ⚠️ Security Notice

- Never share your Discord token or OpenAI API key
- Keep your `.env` file secure and never commit it to version control
- Use this selfbot responsibly and in accordance with Discord's terms of service
- Regularly rotate your API keys and tokens

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DISCORD_TOKEN | Your Discord account token | Yes |
| OPENAI_API_KEY | OpenAI API key for GPT integration | Yes |
| MONITORED_CHANNELS | Comma-separated channel IDs | No |
| MONITORED_GUILDS | Comma-separated guild IDs | No |
| LOG_LEVEL | Logging level (DEBUG, INFO, etc.) | No |
| DB_PATH | Path to SQLite database | No |

## 🛠️ Development

1. Set up development environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🌟 Support

If you find this project helpful, please consider giving it a star ⭐ 