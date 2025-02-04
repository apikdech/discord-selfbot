import asyncio
from collections import deque
from datetime import datetime
from typing import Dict, Deque, List
from dotenv import load_dotenv
from discord_gpt.client import DiscordGPTClient
from discord_selfbot import (
    DiscordSelfBot,
    Message,
    DeletedMessage,
    Reaction,
    TypingEvent,
    EventType,
    Logger,
)
from common import *
from os import getenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random

BLACKLISTED_IDS = ["xxxdodgemasterxxx"]

message_numbers: Dict[str, Deque[MessageNumber]] = {}
reaction_messages: Dict[str, Deque[str]] = {}
# Create a logger instance
log = Logger(debug=True)


# Helper function to add new message number
def add_message_number(
    channel_id: str, message_id: str, number: int, timestamp: str, author_id: str
):
    if channel_id not in message_numbers:
        message_numbers[channel_id] = deque(maxlen=10)

    message_numbers[channel_id].append(
        MessageNumber(
            message_id=message_id,
            number=number,
            timestamp=timestamp,
            author_id=author_id,
        )
    )


# Helper function to get last message number for a channel
def get_last_message_number(channel_id: str) -> MessageNumber | None:
    if channel_id not in message_numbers:
        return None

    channel_messages = message_numbers[channel_id]
    return channel_messages[-1] if channel_messages else None


def check_reaction_message(channel_id: str, message_id: str) -> bool:
    if channel_id not in reaction_messages:
        return False

    return message_id in reaction_messages[channel_id]


last_typing_timestamp = 0
cooldown_min = 0.1
cooldown_max = 0.5
send_number = True


async def send_number_updates(bot: DiscordSelfBot):
    if send_number == False:
        return

    now = datetime.now().astimezone()
    for channel_id in message_numbers.keys():
        last_number = get_last_message_number(channel_id)
        if last_number:
            if last_number.author_id == bot.user.id:
                return
            # Convert the timestamp string to datetime object
            last_timestamp = datetime.fromisoformat(last_number.timestamp)
            time_diff = (now - last_timestamp).total_seconds()
            # cooldown = 2 + random.uniform(1, 5)
            cooldown = cooldown_min + random.uniform(0, cooldown_max - cooldown_min)
            if (
                time_diff > cooldown
            ) and check_reaction_message(channel_id, last_number.message_id):
                log.info("Sending number updates")
                await bot.trigger_typing(channel_id)
                await bot.send_message(channel_id, str(last_number.number + 1))
                add_message_number(
                    channel_id,
                    last_number.message_id,
                    last_number.number + 1,
                    now.isoformat(),
                    bot.user.id,
                )
            else:
                response = f"Waiting for {cooldown - time_diff} seconds to send number {last_number.number + 1} update from {last_number.author_id}"
                log.info(response)
                # await bot.reply_to_message(last_number.message_id, channel_id, response)


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from environment variables
    DISCORD_TOKEN = getenv("DISCORD_TOKEN")
    OPENAI_API_KEY = getenv("OPENAI_API_KEY")
    MONITORED_CHANNELS = [
        int(ch) for ch in getenv("MONITORED_CHANNELS", "").split(",") if ch
    ]
    MONITORED_GUILDS = [
        int(ch) for ch in getenv("MONITORED_GUILDS", "").split(",") if ch
    ]
    OWNER_ID = getenv("OWNER_ID")

    if not DISCORD_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Please set DISCORD_TOKEN and OPENAI_API_KEY in .env file")

    # Initialize the GPT client
    client = DiscordGPTClient(openai_api_key=OPENAI_API_KEY)
    await client.start()

    # Initialize the bot
    bot = DiscordSelfBot(
        token=DISCORD_TOKEN,
        monitored_channels=MONITORED_CHANNELS,
        monitored_guilds=MONITORED_GUILDS,
        debug=False,
    )

    # Set up event handlers
    @bot.on_event(EventType.MESSAGE_CREATE)
    async def handle_message(message: Message):
        log.info(f"New message: {message}")
        if message.author.id == bot.user.id:
            return

        if message.content == ".":
            global last_typing_timestamp
            last_typing_timestamp = int(message.timestamp) + 10
            return

        if message.author.id == OWNER_ID:
            if message.content.startswith("continue"):
                number = message.content.split()[1]
                number = evaluate_number(number)
                if number >= 1:
                    await bot.send_message(message.channel_id, str(number))
                return
                
            global send_number
            
            if message.content == "<:PauseBusiness:941975578729402408>":
                send_number = False
                await bot.send_message(message.channel_id, "<:PauseBusiness:941975578729402408>")
                return

            if message.content == "<:sadcatplease:898223330073673798>":
                send_number = True
                await bot.send_message(message.channel_id, "<:sadcatplease:898223330073673798>")
                return

            if message.content.startswith("cooldown"):
                global cooldown_min, cooldown_max

                cooldown_min = message.content.split()[1]
                cooldown_max = message.content.split()[2]
                cooldown_min = float(cooldown_min)
                cooldown_max = float(cooldown_max)
                await bot.send_message(message.channel_id, f"Updated the cooldown to be [{cooldown_min}, {cooldown_max}]")
                return

        first_word = message.content.split()[0]

        number = evaluate_number(first_word)

        if number >= 1:
            add_message_number(
                message.channel_id,
                message.id,
                number,
                message.timestamp,
                message.author.id,
            )
            return
        elif number == 0:
            return

        if message.author.username in BLACKLISTED_IDS:
            return

        if bot.user.id in [mention.id for mention in message.mentions]:
            log.info(f"Mentioned {bot.user.id} in message: {message}")
            response = await client.generate_gpt_response(
                message.channel_id, message.content
            )
            await bot.trigger_typing(message.channel_id)
            await bot.reply_to_message(
                message.id, message.channel_id, f":speaking_head: {response}"
            )

        await client.add_message_history(
            message.channel_id, message.id, message.author.id, message.content
        )

    @bot.on_event(EventType.MESSAGE_UPDATE)
    async def handle_message_update(message: Message):
        log.info(f"Updated message: {message}")
        log.debug(f"New content: {message.content}")
        if message.referenced_message:
            log.debug(f"Original message: {message.referenced_message.content}")

    @bot.on_event(EventType.MESSAGE_DELETE)
    async def handle_message_delete(message: DeletedMessage):
        log.info(f"Deleted message: {message}")

    @bot.on_event(EventType.MESSAGE_REACTION_ADD)
    async def handle_reaction_add(reaction: Reaction):
        log.info(f"Reaction added: {reaction}")
        if (
            reaction.emoji.name == "❌"
            and reaction.member.user.id == "510016054391734273"
        ):
            await bot.send_message(reaction.channel_id, "1")
            # flush message numbers for the channel
            message_numbers[reaction.channel_id] = deque(maxlen=10)
            add_message_number(
                reaction.channel_id,
                reaction.message_id,
                1,
                reaction.timestamp,
                bot.user.id,
            )
        elif (
            reaction.emoji.name == "✅"
            or reaction.emoji.name == "☑️"
            or reaction.emoji.name == "💯"
        ) and reaction.member.user.id == "510016054391734273":
            if reaction.channel_id not in reaction_messages:
                reaction_messages[reaction.channel_id] = deque(maxlen=10)
            reaction_messages[reaction.channel_id].append(reaction.message_id)

    @bot.on_event(EventType.MESSAGE_REACTION_REMOVE)
    async def handle_reaction_remove(reaction: Reaction):
        log.info(f"Reaction removed: {reaction}")

    @bot.on_event(EventType.TYPING_START)
    async def handle_typing(typing: TypingEvent):
        log.info(f"Typing started: {typing}")
        global last_typing_timestamp
        last_typing_timestamp = typing.timestamp

    # Initialize and start the scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_number_updates,
        trigger="interval",
        seconds=1,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=None,
        args=[bot],
    )
    scheduler.start()

    # Start the bot
    log.info("Starting bot...")
    await bot.start()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
