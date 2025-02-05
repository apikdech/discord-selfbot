import asyncio
from collections import deque
from datetime import datetime
from typing import Dict, Deque, List, Tuple
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
COUNTING_BOT_ID = "510016054391734273"

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


# Helper function to get largest message number for a channel
def get_largest_message_number(channel_id: str) -> MessageNumber | None:
    if channel_id not in message_numbers:
        return None

    channel_messages = message_numbers[channel_id]
    return max(channel_messages, key=lambda x: x.number) if channel_messages else None


def check_reaction_message(channel_id: str, message_id: str) -> bool:
    if reaction_listen_config.get(channel_id, True) == False:
        return True
        
    if channel_id not in reaction_messages:
        return False
    
    return message_id in reaction_messages[channel_id]


last_typing_timestamp = 0
cooldowns: Dict[str, Tuple[float, float]] = {
    "1330033413524033537": (30, 60),
    "1330237721557471232": (0.1, 0.5),
}
send_number: Dict[str, bool] = {
    "1330033413524033537": False,
    "1330237721557471232": True, 
}
counter_stuck_times: Dict[str, int] = {}
send_stuck_help: Dict[str, bool] = {}
SENDING_CHANNELS = [
    "1330033413524033537", # SST
    "1330237721557471232", # Hideout
]
reaction_listen_config: Dict[str, bool] = {
    "1330033413524033537": False,
    "1330237721557471232": False,
}


async def send_number_updates(bot: DiscordSelfBot):
    now = datetime.now().astimezone()
    for channel_id in SENDING_CHANNELS:
        if send_number.get(channel_id, False) == True:
            largest_number = get_largest_message_number(channel_id)
            if largest_number and largest_number.author_id != bot.user.id:
                # Convert the timestamp string to datetime object
                last_timestamp = datetime.fromisoformat(largest_number.timestamp)
                time_diff = (now - last_timestamp).total_seconds()
                cooldown = cooldowns[channel_id][0] + random.uniform(0, cooldowns[channel_id][1] - cooldowns[channel_id][0])

                if (time_diff > cooldown) and check_reaction_message(
                    channel_id, largest_number.message_id
                ):
                    log.info("Sending number updates")
                    message_numbers[channel_id] = deque(maxlen=10)
                    await bot.trigger_typing(channel_id)
                    await bot.send_message(channel_id, str(largest_number.number + 1))
                    send_stuck_help[channel_id] = False
                    counter_stuck_times[channel_id] = 0
                else:
                    response = f"Waiting for {cooldown - time_diff} seconds to send number {largest_number.number + 1} update from {largest_number.author_id}"
                    log.info(response)

            if (
                counter_stuck_times.get(channel_id, 0) > 150
                and send_stuck_help.get(channel_id, False) == False
            ):
                await bot.send_message(channel_id, "c!server")
                counter_stuck_times[channel_id] = 0

                send_stuck_help[channel_id] = True
            else:
                if send_stuck_help.get(channel_id, False) == False:
                    counter_stuck_times[channel_id] = (
                        counter_stuck_times.get(channel_id, 0) + 1
                    )


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
            if message.content.startswith("continue") and message.content.endswith("🗣️"):
                counter_stuck_times[message.channel_id] = 0
                message_numbers[message.channel_id] = deque(maxlen=10)
                await bot.send_message(
                    message.channel_id, "c!server"
                )
                return

            if message.content.startswith("<:PauseBusiness:941975578729402408>"):
                send_number[message.channel_id] = False
                await bot.send_message(
                    message.channel_id, "<:PauseBusiness:941975578729402408>"
                )
                return

            if message.content.startswith("<:sadcatplease:898223330073673798>"):
                send_number[message.channel_id] = True
                await bot.send_message(
                    message.channel_id, "<:sadcatplease:898223330073673798>"
                )
                return

            if message.content.startswith("cooldown"):
                splitted_message = message.content.split()
                cooldown_min, cooldown_max = splitted_message[1], splitted_message[2]
                cooldown_min = float(cooldown_min)
                cooldown_max = float(cooldown_max)
                cooldowns[message.channel_id] = (cooldown_min, cooldown_max)
                await bot.send_message(
                    message.channel_id,
                    f"Updated the cooldown to be [{cooldown_min}, {cooldown_max}]",
                )
                return
            
            if message.content.startswith("listen reaction"):
                reaction_listen_config[message.channel_id] = True
                await bot.send_message(
                    message.channel_id, ":speaking_head: I'll listen to reactions now"
                )
                return
            
            if message.content.startswith("stop listen reaction"):
                reaction_listen_config[message.channel_id] = False
                await bot.send_message(
                    message.channel_id, ":speaking_head: I'll stop listening to reactions now"
                )
                return
            
        if message.author.id == COUNTING_BOT_ID:
            if (
                len(message.embeds) == 0
                or message.referenced_message.content != "c!server"
                or message.referenced_message.author.id != bot.user.id
            ):
                return

            embed = message.embeds[0]

            # Parse the description to get current number and last counter
            if embed.description:
                try:
                    # Extract current number - matches "Current Number: **X,XXX**"
                    current_number = embed.description.split("\n")[0]
                    current_number = current_number.split("**")[1].replace(",", "")
                    current_number = int(current_number)

                    # Extract last counter - matches "Last counted by: <@USER_ID>"
                    last_counter = embed.description.split("\n")[3]
                    last_counter_id = last_counter.split("<@")[1].split(">")[0]

                    log.info(
                        f"Current number: {current_number}, Last counter: {last_counter_id}"
                    )

                    if last_counter_id == bot.user.id:
                        return

                    send_stuck_help[message.channel_id] = False
                    send_number[message.channel_id] = True
                    message_numbers[message.channel_id] = deque(maxlen=10)
                    await bot.send_message(
                        message.channel_id,
                        str(current_number + 1),
                    )
                except (IndexError, ValueError) as e:
                    log.error(f"Error parsing embed description: {e}")
                    log.debug(f"Embed description: {embed.description}")

            return

        if len(message.content.split()) == 0:
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
            chunked_responses = bot.chunk_message(response, 1950)
            for chunk in chunked_responses:
                await bot.reply_to_message(
                    message.id, message.channel_id, f":speaking_head: {chunk}"
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
        seconds=0.25,
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
