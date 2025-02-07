#!/usr/bin/env python3

import os
import asyncio
from dotenv import load_dotenv
from discord_selfbot import DiscordSelfBot
from discord_selfbot.models import Message, Reaction, TypingEvent, EventType
from discord_gpt import GPTClient
from discord_selfbot.logger import setup_logger

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = setup_logger()

# Initialize the Discord client with GPT integration
bot = DiscordSelfBot(
    token=os.getenv("DISCORD_TOKEN"),
    monitored_channels=[
        int(ch) for ch in os.getenv("MONITORED_CHANNELS", "").split(",") if ch
    ],
    monitored_guilds=[
        int(guild) for guild in os.getenv("MONITORED_GUILDS", "").split(",") if guild
    ],
    debug=os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG",
)

# Initialize GPT client if API key is available
gpt_client = None
if os.getenv("OPENAI_API_KEY"):
    gpt_client = GPTClient(api_key=os.getenv("OPENAI_API_KEY"))


# Message handling
@bot.on_event(EventType.MESSAGE_CREATE)
async def handle_message(message: Message):
    """Handle new messages"""
    if message.author.id == bot.user.id:
        return

    logger.info(f"Message from {message.author.username}: {message.content}")

    # Example: Auto-reply to mentions if GPT is enabled
    if bot.user.mentioned_in(message) and gpt_client:
        async with message.channel.typing():
            try:
                response = await gpt_client.get_response(message.content)
                await bot.send_message(message.channel_id, response)
            except Exception as e:
                logger.error(f"Error generating GPT response: {e}")


@bot.on_event(EventType.MESSAGE_UPDATE)
async def handle_message_edit(message: Message):
    """Handle message edits"""
    if message.author.id == bot.user.id:
        return

    logger.info(f"Message edited by {message.author.username}: {message.content}")


@bot.on_event(EventType.MESSAGE_DELETE)
async def handle_message_delete(message: Message):
    """Handle message deletions"""
    if message.author.id == bot.user.id:
        return

    logger.info(f"Message deleted in channel {message.channel_id}")


# Reaction handling
@bot.on_event(EventType.MESSAGE_REACTION_ADD)
async def handle_reaction_add(reaction: Reaction):
    """Handle new reactions"""
    if reaction.user_id == bot.user.id:
        return

    logger.info(f"Reaction added: {reaction.emoji}")

    # Example: Mirror reactions on your messages
    if reaction.message.author.id == bot.user.id:
        try:
            await bot.add_reaction(
                message_id=reaction.message_id,
                channel_id=reaction.channel_id,
                emoji=reaction.emoji,
            )
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")


@bot.on_event(EventType.MESSAGE_REACTION_REMOVE)
async def handle_reaction_remove(reaction: Reaction):
    """Handle reaction removals"""
    if reaction.user_id == bot.user.id:
        return

    logger.info(f"Reaction removed: {reaction.emoji}")


# Typing event handling
@bot.on_event(EventType.TYPING_START)
async def handle_typing(typing: TypingEvent):
    """Handle typing events"""
    if typing.user_id == bot.user.id:
        return

    logger.debug(f"User {typing.user_id} is typing in channel {typing.channel_id}")


async def scheduled_task():
    """Example of a scheduled task"""
    while True:
        try:
            # Example: Get last messages from monitored channels
            for channel_id in bot.monitored_channels:
                messages = await bot.get_last_messages(channel_id, limit=5)
                logger.info(f"Last {len(messages)} messages in channel {channel_id}")

            # Wait for 5 minutes before next check
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"Error in scheduled task: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying


def main():
    """Main entry point"""
    try:
        # Start scheduled task if there are monitored channels
        if bot.monitored_channels:
            asyncio.create_task(scheduled_task())

        # Start the bot
        logger.info("Starting Discord selfbot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
