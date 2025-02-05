import websockets
import aiohttp
import asyncio
import json
from typing import List, Optional, Dict, Any, Callable, Union
from .models import (
    UserSession,
    Message,
    DeletedMessage,
    Reaction,
    TypingEvent,
    EventType,
)
from .logger import Logger


class DiscordSelfBot:
    """
    A Discord self-bot client that can monitor and interact with Discord events.

    This client connects to Discord's WebSocket gateway and handles various events
    like messages, reactions, typing indicators, etc. It can be configured to monitor
    specific channels and guilds.

    Supported Events:
        - TYPING_START: Triggered when a user starts typing
          Handler receives: TypingEvent
        - MESSAGE_CREATE: Triggered when a new message is sent
          Handler receives: Message
        - MESSAGE_UPDATE: Triggered when a message is edited
          Handler receives: Message
        - MESSAGE_DELETE: Triggered when a message is deleted
          Handler receives: DeletedMessage
        - MESSAGE_REACTION_ADD: Triggered when a reaction is added
          Handler receives: Reaction
        - MESSAGE_REACTION_REMOVE: Triggered when a reaction is removed
          Handler receives: Reaction

    Attributes:
        GATEWAY_URL (str): The Discord WebSocket gateway URL
        API_URL (str): The Discord REST API base URL
        token (str): The user's Discord token
        monitored_channels (List[int]): List of channel IDs to monitor
        monitored_guilds (List[int]): List of guild IDs to monitor
        debug (bool): Whether to enable debug logging
        ws (Optional[websockets.WebSocketClientProtocol]): The WebSocket connection
        session (Optional[aiohttp.ClientSession]): The HTTP session for API requests
        sequence (Optional[int]): The last sequence number received
        heartbeat_interval (Optional[int]): The interval for sending heartbeats
        session_id (Optional[str]): The current session ID
        user_id (Optional[str]): The authenticated user's ID
        event_handlers (Dict[str, List[Callable]]): Registered event handlers
        log (Logger): The logger instance
        task_semaphore (asyncio.Semaphore): Semaphore for limiting concurrent event handlers
        active_tasks (set[asyncio.Task]): Set of active event handler tasks
    """

    GATEWAY_URL = "wss://gateway.discord.gg/?v=9&encoding=json"
    API_URL = "https://discord.com/api/v9"

    def __init__(
        self,
        token: str,
        monitored_channels: List[int] = None,
        monitored_guilds: List[int] = None,
        debug: bool = False,
        max_concurrent_tasks: int = 50,
    ):
        """
        Initialize the Discord self-bot.

        Args:
            token (str): The user's Discord token
            monitored_channels (List[int], optional): List of channel IDs to monitor
            monitored_guilds (List[int], optional): List of guild IDs to monitor
            debug (bool, optional): Whether to enable debug logging
            max_concurrent_tasks (int, optional): Maximum number of concurrent event handlers. Defaults to 10.
        """
        self.token = token
        self.monitored_channels = monitored_channels or []
        self.monitored_guilds = monitored_guilds or []
        self.debug = debug
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.sequence = None
        self.heartbeat_interval = None
        self.session_id = None
        self.user: UserSession
        self.log = Logger(debug=debug)
        self.task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.active_tasks: set[asyncio.Task] = set()

        self.event_handlers = {event.value: [] for event in EventType}

    def on_event(self, event_name: Union[EventType, str]):
        """
        Decorator for registering event handlers.

        Args:
            event_name (Union[EventType, str]): The event to handle. Can be either an EventType enum
                                              or a string matching one of the supported events.

        Returns:
            Callable: The decorator function

        Supported Events:
            - TYPING_START: Triggered when a user starts typing
              Handler receives: TypingEvent
            - MESSAGE_CREATE: Triggered when a new message is sent
              Handler receives: Message
            - MESSAGE_UPDATE: Triggered when a message is edited
              Handler receives: Message
            - MESSAGE_DELETE: Triggered when a message is deleted
              Handler receives: DeletedMessage
            - MESSAGE_REACTION_ADD: Triggered when a reaction is added
              Handler receives: Reaction
            - MESSAGE_REACTION_REMOVE: Triggered when a reaction is removed
              Handler receives: Reaction

        Example:
            Using enum (recommended):
                @bot.on_event(EventType.MESSAGE_CREATE)
                async def handle_message(message: Message):
                    print(f"New message: {message.content}")

            Using string:
                @bot.on_event('MESSAGE_CREATE')
                async def handle_message(message: Message):
                    print(f"New message: {message.content}")
        """
        # Convert string to enum if needed
        if isinstance(event_name, str):
            try:
                event_name = EventType(event_name)
            except ValueError:
                raise ValueError(
                    f"Unsupported event: {event_name}. Use one of: {', '.join(e.value for e in EventType)}"
                )

        def decorator(func: Callable):
            self.event_handlers[event_name.value].append(func)
            return func

        return decorator

    async def _send_json(self, data: Dict):
        """
        Send JSON data through the WebSocket connection.

        Args:
            data (Dict): The data to send
        """
        await self.ws.send(json.dumps(data))

    async def _heartbeat(self):
        """
        Send heartbeat messages to keep the WebSocket connection alive.
        This runs in a loop at the interval specified by Discord.
        """
        while True:
            await self._send_json({"op": 1, "d": self.sequence})
            await asyncio.sleep(self.heartbeat_interval / 1000)

    async def _identify(self):
        """
        Send the identify payload to establish the WebSocket connection.
        This includes the token and intents required for the bot to function.
        """
        await self._send_json(
            {
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": "windows",
                        "$browser": "chrome",
                        "$device": "chrome",
                    },
                    "presence": {
                        "status": "online",
                        "since": 0,
                        "activities": [],
                        "afk": False,
                    },
                    "intents": 1 << 0
                    | 1 << 9
                    | 1 << 10
                    | 1 << 11
                    | 1 << 12
                    | 1 << 13
                    | 1 << 14
                    | 1 << 15
                    | 1 << 24
                    | 1 << 25,
                },
            }
        )

    async def _handle_event(self, event_type: str, data: Dict):
        """
        Handle incoming Discord events and route them to appropriate handlers.
        Each handler runs concurrently in its own task, with a limit on concurrent executions.

        Args:
            event_type (str): The type of event (e.g., MESSAGE_CREATE)
            data (Dict): The event data from Discord
        """
        try:
            # Different events have channel_id in different places
            channel_id = None
            if "channel_id" in data:
                channel_id = data["channel_id"]
            elif "message" in data and "channel_id" in data["message"]:
                channel_id = data["message"]["channel_id"]

            # If no monitored channels or the event's channel is monitored
            if not self.monitored_channels or (
                channel_id and int(channel_id) in self.monitored_channels
            ):
                try:
                    # Parse events into appropriate objects
                    if event_type == EventType.MESSAGE_DELETE.value:
                        parsed_data = DeletedMessage.from_dict(data)
                    elif event_type in [
                        EventType.MESSAGE_CREATE.value,
                        EventType.MESSAGE_UPDATE.value,
                    ]:
                        parsed_data = Message.from_dict(data)
                    elif event_type in [
                        EventType.MESSAGE_REACTION_ADD.value,
                        EventType.MESSAGE_REACTION_REMOVE.value,
                    ]:
                        parsed_data = Reaction.from_dict(data)
                    elif event_type == EventType.TYPING_START.value:
                        parsed_data = TypingEvent.from_dict(data)
                    else:
                        parsed_data = data

                    # Create and track tasks for each handler
                    for handler in self.event_handlers.get(event_type, []):
                        task = asyncio.create_task(
                            self._run_handler(handler, event_type, parsed_data, data)
                        )
                        self.active_tasks.add(task)
                        task.add_done_callback(
                            self.active_tasks.discard
                        )  # Remove task when done

                    if self.debug:
                        self.log.debug(
                            f"Active tasks: {len(self.active_tasks)}/{self.task_semaphore._value}"
                        )

                except KeyError as e:
                    self.log.error(
                        f"Error parsing event data for {event_type}: Missing key {e}"
                    )
                    self.log.debug(f"Raw event data: {data}")
                except Exception as e:
                    self.log.error(f"Error parsing event data for {event_type}: {e}")
                    self.log.debug(f"Raw event data: {data}")
        except Exception as e:
            self.log.error(f"Error handling event {event_type}: {e}")
            self.log.debug(f"Raw event data: {data}")

    async def _run_handler(
        self, handler: Callable, event_type: str, parsed_data: Any, raw_data: Dict
    ) -> None:
        """
        Run an event handler in a safe context with concurrency limits.

        Args:
            handler (Callable): The event handler to run
            event_type (str): The type of event
            parsed_data (Any): The parsed event data
            raw_data (Dict): The raw event data for debugging
        """
        try:
            async with self.task_semaphore:  # Limit concurrent tasks
                await handler(parsed_data)
        except Exception as e:
            self.log.error(f"Error in event handler for {event_type}: {e}")
            self.log.debug(f"Event data: {raw_data}")

    async def _api_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[Dict]:
        """
        Make an HTTP request to the Discord API.

        Args:
            method (str): The HTTP method to use
            endpoint (str): The API endpoint to call
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[Dict]: The JSON response, or None for 204 No Content
        """
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        async with self.session.request(
            method, f"{self.API_URL}{endpoint}", headers=headers, **kwargs
        ) as resp:
            # Handle 204 No Content responses
            if resp.status == 204:
                return None

            # For other responses, try to parse JSON
            try:
                return await resp.json()
            except aiohttp.ContentTypeError as e:
                self.log.warn(
                    f"Warning: Unexpected response content type: {resp.content_type}"
                )
                return None

    async def send_message(
        self, channel_id: int, content: str, reference_message_id: Optional[int] = None
    ):
        """
        Send a message to a Discord channel. If the content is longer than 2000 characters,
        it will be split into multiple messages.

        Args:
            channel_id (int): The ID of the channel to send to
            content (str): The message content
            reference_message_id (Optional[int]): The ID of the message to reply to. Only applies to first message if split.
        """
        chunks = self.chunk_message(content)

        # Send all chunks
        for i, chunk in enumerate(chunks):
            payload = {"content": chunk}
            # Only include reference for first message
            if i == 0 and reference_message_id:
                payload["message_reference"] = {
                    "message_id": str(reference_message_id),
                    "channel_id": str(channel_id),
                }

            await self._api_request(
                "POST", f"/channels/{channel_id}/messages", json=payload
            )

    async def reply_to_message(self, message_id: int, channel_id: int, content: str):
        """
        Reply to a specific message.

        Args:
            message_id (int): The ID of the message to reply to
            channel_id (int): The channel ID where the message is
            content (str): The reply content
        """
        await self.send_message(channel_id, content, reference_message_id=message_id)

    async def get_last_messages(
        self, channel_id: int, limit: int = 50
    ) -> List[Message]:
        """
        Fetch the last messages from a channel.

        Args:
            channel_id (int): The ID of the channel to fetch messages from
            limit (int, optional): Number of messages to fetch. Defaults to 50. Max is 100.

        Returns:
            List[Message]: List of Message objects, ordered from newest to oldest

        Raises:
            ValueError: If limit is not between 1 and 100
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")

        response = await self._api_request(
            "GET", f"/channels/{channel_id}/messages", params={"limit": limit}
        )

        if response:
            return [Message.from_dict(msg) for msg in response]
        return []

    async def add_reaction(self, message_id: int, channel_id: int, emoji: str):
        """
        Add a reaction to a message.

        Args:
            message_id (int): The ID of the message to react to
            channel_id (int): The channel ID where the message is
            emoji (str): The emoji to react with
        """
        encoded_emoji = emoji.encode("utf-8").hex()
        await self._api_request(
            "PUT",
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me",
        )

    async def remove_reaction(self, message_id: int, channel_id: int, emoji: str):
        """
        Remove a reaction from a message.

        Args:
            message_id (int): The ID of the message to remove reaction from
            channel_id (int): The channel ID where the message is
            emoji (str): The emoji to remove
        """
        encoded_emoji = emoji.encode("utf-8").hex()
        await self._api_request(
            "DELETE",
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me",
        )

    async def trigger_typing(self, channel_id: int):
        """
        Trigger a typing indicator in a channel.

        Args:
            channel_id (int): The ID of the channel to show typing in
        """
        await self._api_request("POST", f"/channels/{channel_id}/typing")

    async def update_message(self, channel_id: int, message_id: int, content: str):
        """
        Update the content of a message.

        Args:
            channel_id (int): The channel ID where the message is
            message_id (int): The ID of the message to update
            content (str): The new message content
        """
        payload = {"content": content}

        await self._api_request(
            "PATCH", f"/channels/{channel_id}/messages/{message_id}", json=payload
        )

    async def delete_message(self, channel_id: int, message_id: int):
        """
        Delete a message.

        Args:
            channel_id (int): The channel ID where the message is
            message_id (int): The ID of the message to delete
        """
        await self._api_request(
            "DELETE", f"/channels/{channel_id}/messages/{message_id}"
        )

    async def _subscribe_to_typing(self, guild_id: int):
        """
        Subscribe to typing indicators for a guild.

        Args:
            guild_id (int): The ID of the guild to subscribe to
        """
        # First send op 36
        await self._send_json({"op": 36, "d": {"guild_id": str(guild_id)}})

        # Then send op 37 with subscriptions
        await self._send_json(
            {
                "op": 37,
                "d": {
                    "subscriptions": {
                        str(guild_id): {
                            "typing": True,
                            "activities": True,
                            "threads": True,
                        }
                    }
                },
            }
        )

    async def start(self):
        """
        Start the bot and establish connection to Discord.
        This method handles the main event loop and reconnection logic.
        """
        # Configure connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,  # Maximum number of concurrent connections
            limit_per_host=20,  # Maximum number of concurrent connections to the same host
            force_close=False,  # Keep connections alive
            enable_cleanup_closed=True,  # Clean up closed connections
            ttl_dns_cache=300,  # DNS cache TTL in seconds (5 minutes)
        )
        
        self.session = aiohttp.ClientSession(connector=connector)

        while True:
            try:
                self.log.info("Attempting to connect to Discord WebSocket...")
                async with websockets.connect(self.GATEWAY_URL) as ws:
                    self.ws = ws
                    self.log.info("Successfully connected to Discord WebSocket!")

                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)

                        op = data.get("op")

                        if self.debug:
                            self.log.debug("Received event:", data)

                        skipped_events = [
                            None,
                            "PRESENCE_UPDATE",
                            "USER_UPDATE",
                            "VOICE_STATE_UPDATE",
                            "VOICE_SERVER_UPDATE",
                            "RESUMED",
                            "RECONNECT",
                            "INVALID_SESSION",
                            "HELLO",
                            "HEARTBEAT_ACK",
                        ]

                        if op == 10:  # Hello
                            self.log.info(
                                "Received HELLO from Discord. Setting up heartbeat..."
                            )
                            self.heartbeat_interval = data["d"]["heartbeat_interval"]
                            asyncio.create_task(self._heartbeat())
                            await self._identify()
                            self.log.info("Sent identification payload to Discord.")

                        elif op == 0:  # Dispatch
                            self.sequence = data["s"]
                            event_type = data["t"]

                            if event_type == "READY":
                                self.session_id = data["d"]["session_id"]
                                self.user = UserSession.from_dict(data["d"]["user"])
                                self.log.info(
                                    f"Bot is ready! Logged in as User ID: {self.user.id} ({self.user.username}) - {self.user.global_name}"
                                )

                                # Subscribe to typing indicators for monitored guilds
                                for guild_id in self.monitored_guilds:
                                    self.log.info(
                                        f"Subscribing to typing indicators for guild: {guild_id}"
                                    )
                                    await self._subscribe_to_typing(guild_id)

                            elif event_type in skipped_events:
                                if self.debug:
                                    self.log.debug(f"Skipping event: {event_type}")
                                continue
                            else:
                                await self._handle_event(event_type, data["d"])

            except (
                websockets.exceptions.ConnectionClosed,
                websockets.exceptions.ConnectionClosedError,
            ) as e:
                self.log.warn(
                    "WebSocket connection closed, caused by: "
                    + str(e)
                    + ". Attempting to reconnect in 5 seconds..."
                )
                await asyncio.sleep(5)
                continue

            except Exception as e:
                self.log.error(f"Error: {e}")
                self.log.warn("Attempting to reconnect in 5 seconds...")
                await asyncio.sleep(5)
                continue

    def run(self):
        """
        Run the bot synchronously.
        This is the main entry point for starting the bot.
        """
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            self.log.info("Bot shutdown requested...")
            # Cancel all running tasks
            for task in self.active_tasks:
                task.cancel()
            if self.session:
                asyncio.run(self.session.close())
            self.log.info("Bot shutdown complete.")

    def chunk_message(self, content: str, chunk_size: int = 2000) -> list[str]:
        """
        Split a message into chunks of specified size, preserving newlines where possible.

        Args:
            content (str): The message content to split
            chunk_size (int): Maximum size of each chunk. Defaults to 2000 (Discord's limit)

        Returns:
            list[str]: List of message chunks, each no larger than chunk_size
        """
        chunks = []
        current_chunk = ""

        # First try to split on newlines
        lines = content.split("\n")
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= chunk_size:  # +1 for newline
                if current_chunk:
                    current_chunk += "\n"
                current_chunk += line
            else:
                # If current line itself is > chunk_size, split it
                if len(line) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = ""
                    # Split long line into chunks
                    for i in range(0, len(line), chunk_size):
                        chunks.append(line[i : i + chunk_size])
                else:
                    # Current line would make chunk too big, save current chunk and start new
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = line

        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        # If no chunks were created (original message ≤ chunk_size), use original content
        if not chunks:
            chunks = [content]

        return chunks
