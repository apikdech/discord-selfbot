#!/usr/bin/env python3

import os
import asyncio
from dotenv import load_dotenv
from discord_selfbot import DiscordSelfBot
from discord_selfbot.models import Message, Reaction, TypingEvent, EventType
from discord_gpt.client import DiscordGPTClient
from discord_selfbot.logger import Logger

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = Logger()


async def main():
    # Initialize the Discord client with GPT integration
    bot = DiscordSelfBot(
        token=os.getenv("DISCORD_TOKEN"),
        monitored_channels=[
            int(ch) for ch in os.getenv("MONITORED_CHANNELS", "").split(",") if ch
        ],
        monitored_guilds=[
            int(guild)
            for guild in os.getenv("MONITORED_GUILDS", "").split(",")
            if guild
        ],
        debug=False,
    )

    # Initialize GPT client if API key is available
    gpt_client = None
    if os.getenv("OPENAI_API_KEY"):
        gpt_client = DiscordGPTClient(openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Message handling
    @bot.on_event(EventType.MESSAGE_CREATE)
    async def handle_message(message: Message):
        """Handle new messages"""
        if message.author.id == bot.user.id:
            return

        logger.info(f"Message from {message.author.username}: {message.content}")

        # Example: Auto-reply to mentions if GPT is enabled
        if bot.user.id in message.mentions:
            await bot.send_message(message.channel_id, "Hello!")

    # Start the bot
    try:
        await gpt_client.setup()
        await bot.run()
    except Exception as e:
        print(f"Error starting clients: {e}")
        raise
    finally:
        # Ensure the client session is closed
        await bot.stop()


if __name__ == "__main__":
    """Main entry point"""
    try:
        # Start the bot
        logger.info("Starting Discord selfbot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
