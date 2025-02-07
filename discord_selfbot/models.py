from dataclasses import dataclass, fields
from typing import List, Optional, Dict
from enum import Enum


class EventType(Enum):
    """
    Enum representing supported Discord events.

    Available events:
        TYPING_START: When a user starts typing in a channel
        MESSAGE_CREATE: When a new message is sent
        MESSAGE_UPDATE: When a message is edited
        MESSAGE_DELETE: When a message is deleted
        MESSAGE_REACTION_ADD: When a reaction is added to a message
        MESSAGE_REACTION_REMOVE: When a reaction is removed from a message

    Each event provides specific data:
        TYPING_START -> TypingEvent
        MESSAGE_CREATE -> Message
        MESSAGE_UPDATE -> Message
        MESSAGE_DELETE -> DeletedMessage
        MESSAGE_REACTION_ADD -> Reaction
        MESSAGE_REACTION_REMOVE -> Reaction
    """

    TYPING_START = "TYPING_START"
    MESSAGE_CREATE = "MESSAGE_CREATE"
    MESSAGE_UPDATE = "MESSAGE_UPDATE"
    MESSAGE_DELETE = "MESSAGE_DELETE"
    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"


@dataclass
class UserSession:
    """
    Represents a user's session with their basic information.
    """

    verified: bool
    id: str
    username: str
    global_name: Optional[str]
    discriminator: str
    avatar: Optional[str]
    public_flags: int
    avatar_decoration_data: Optional[Dict]
    primary_guild: Optional[str]
    clan: Optional[str]
    premium: bool
    premium_type: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict) -> "UserSession":
        """
        Create a UserSession instance from a dictionary of data.
        """
        return cls(
            verified=data.get("verified", False),
            id=data.get("id"),
            username=data.get("username"),
            global_name=data.get("global_name"),
            discriminator=data.get("discriminator"),
            avatar=data.get("avatar"),
            public_flags=data.get("public_flags"),
            avatar_decoration_data=data.get("avatar_decoration_data"),
            primary_guild=data.get("primary_guild"),
            clan=data.get("clan"),
            premium=data.get("premium", False),
            premium_type=data.get("premium_type"),
        )


@dataclass
class Author:
    """
    Represents a Discord user/author with their basic information.

    Attributes:
        username (str): The user's username
        id (str): The user's unique ID
        global_name (Optional[str]): The user's global display name
        discriminator (str): The user's discriminator (4 digits after #)
        avatar (Optional[str]): The user's avatar hash
        flags (Optional[int]): The user's flags (badges, etc.)
        public_flags (int): The user's public flags (badges, etc.)
        avatar_decoration_data (Optional[Dict]): Data about avatar decorations
        primary_guild (Optional[str]): The user's primary guild ID
        clan (Optional[str]): The user's clan information
        bot (Optional[bool]): Whether the user is a bot
        display_name (Optional[str]): The user's display name
    """

    username: str
    id: str
    global_name: Optional[str]
    discriminator: str
    avatar: Optional[str]
    public_flags: int
    avatar_decoration_data: Optional[Dict]
    primary_guild: Optional[str]
    clan: Optional[str]
    flags: Optional[int] = None
    bot: Optional[bool] = False
    display_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Author":
        """Create an Author instance from a dictionary, ignoring unknown fields."""
        valid_fields = {field.name for field in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class Member:
    """
    Represents a Discord guild member with their roles and settings.

    Attributes:
        user (Optional[Author]): The user object for this member
        roles (List[str]): List of role IDs the member has
        premium_since (Optional[str]): When the member started boosting the server
        pending (bool): Whether the member is pending verification
        nick (Optional[str]): The member's nickname in the guild
        mute (bool): Whether the member is server muted
        joined_at (str): When the member joined the guild
        flags (int): The member's flags
        deaf (bool): Whether the member is server deafened
        communication_disabled_until (Optional[str]): Timeout expiration timestamp
        banner (Optional[str]): The member's banner hash
        avatar (Optional[str]): The member's guild-specific avatar hash
    """

    user: Optional[Author]
    roles: List[str]
    premium_since: Optional[str]
    pending: bool
    nick: Optional[str]
    mute: bool
    joined_at: str
    flags: int
    deaf: bool
    communication_disabled_until: Optional[str]
    banner: Optional[str]
    avatar: Optional[str]


@dataclass
class MessageReference:
    """
    Represents a reference to another message (used for replies).

    Attributes:
        message_id (str): The ID of the referenced message
        channel_id (str): The channel ID where the referenced message is
        guild_id (Optional[str]): The guild ID where the referenced message is
        type (Optional[int]): The type of reference
    """

    message_id: str
    channel_id: str
    guild_id: Optional[str]
    type: Optional[int] = 0


@dataclass
class Sticker:
    """
    Represents a Discord sticker.

    Attributes:
        name (str): The name of the sticker
        id (str): The unique ID of the sticker
        format_type (int): The format type of the sticker
    """

    name: str
    id: str
    format_type: int


@dataclass
class EmbedProvider:
    """
    Represents a provider in a Discord embed.

    Attributes:
        name (Optional[str]): The name of the provider
        url (Optional[str]): The URL of the provider
    """

    name: Optional[str] = None
    url: Optional[str] = None


@dataclass
class EmbedThumbnail:
    """
    Represents a thumbnail in a Discord embed.

    Attributes:
        url (str): The source URL of the thumbnail
        proxy_url (Optional[str]): The proxied URL of the thumbnail
        height (Optional[int]): The height of the thumbnail
        width (Optional[int]): The width of the thumbnail
        placeholder (Optional[str]): The placeholder data
        placeholder_version (Optional[int]): The placeholder version
        flags (Optional[int]): The thumbnail flags
    """

    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    placeholder: Optional[str] = None
    placeholder_version: Optional[int] = None
    flags: Optional[int] = None


@dataclass
class Embed:
    """
    Represents a Discord embed.

    Attributes:
        url (Optional[str]): The URL of the embed
        type (Optional[str]): The type of embed
        title (Optional[str]): The title of the embed
        description (Optional[str]): The description of the embed
        provider (Optional[EmbedProvider]): The provider information
        thumbnail (Optional[EmbedThumbnail]): The thumbnail information
        color (Optional[int]): The color code of the embed
    """

    url: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[EmbedProvider] = None
    thumbnail: Optional[EmbedThumbnail] = None
    color: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Embed":
        """
        Create an Embed instance from a dictionary of data.

        Args:
            data (Dict): The raw embed data from Discord

        Returns:
            Embed: A new Embed instance
        """
        provider = None
        if "provider" in data:
            provider = EmbedProvider(**data["provider"])

        thumbnail = None
        if "thumbnail" in data:
            thumbnail = EmbedThumbnail(**data["thumbnail"])

        return cls(
            url=data.get("url"),
            type=data.get("type"),
            title=data.get("title"),
            description=data.get("description"),
            provider=provider,
            thumbnail=thumbnail,
            color=data.get("color"),
        )


@dataclass
class Attachment:
    """
    Represents a file attached to a Discord message.

    Attributes:
        url (str): The source URL of the file
        size (int): The size of the file in bytes
        proxy_url (str): The proxied URL of the file
        id (str): The attachment's unique ID
        filename (str): The name of the file
        content_type (Optional[str]): The MIME type of the file
        content_scan_version (Optional[int]): The content scan version
    """

    url: str
    size: int
    proxy_url: str
    id: str
    filename: str
    content_type: Optional[str] = None
    content_scan_version: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Attachment":
        """
        Create an Attachment instance from a dictionary of data.

        Args:
            data (Dict): The raw attachment data from Discord

        Returns:
            Attachment: A new Attachment instance
        """
        return cls(
            url=data["url"],
            size=data["size"],
            proxy_url=data["proxy_url"],
            id=data["id"],
            filename=data["filename"],
            content_type=data.get("content_type"),
            content_scan_version=data.get("content_scan_version"),
        )


@dataclass
class Message:
    """
    Represents a Discord message with all its content and metadata.

    Attributes:
        id (str): The message's unique ID
        type (int): The type of message
        content (str): The message's content
        channel_id (str): The channel where the message was sent
        author (Optional[Author]): The user who sent the message
        timestamp (str): When the message was sent
        edited_timestamp (Optional[str]): When the message was last edited
        tts (bool): Whether this is a TTS message
        mention_everyone (bool): Whether the message mentions @everyone/@here
        mentions (List[Author]): Users mentioned in the message
        mention_roles (List[str]): Roles mentioned in the message
        attachments (List[Attachment]): Files attached to the message
        embeds (List[Embed]): Embeds in the message
        pinned (bool): Whether the message is pinned
        flags (int): Message flags
        components (List[Dict]): Message components (buttons, etc.)
        guild_id (Optional[str]): The guild where the message was sent
        member (Optional[Member]): The member who sent the message
        referenced_message (Optional[Message]): The message being replied to
        message_reference (Optional[MessageReference]): Reference data
        sticker_items (Optional[List[Sticker]]): Stickers in the message
        position (Optional[int]): Message position
        channel_type (Optional[int]): Type of the channel
        message_snapshots (Optional[List[Message]]): Snapshots of forwarded messages
    """

    id: Optional[str]
    type: int
    content: str
    channel_id: str
    timestamp: str
    edited_timestamp: Optional[str]
    tts: bool
    mention_everyone: bool
    mentions: List[Author]
    mention_roles: List[str]
    attachments: List[Attachment]
    embeds: List[Embed]
    pinned: bool
    flags: int
    components: List[Dict]
    author: Optional[Author] = None
    guild_id: Optional[str] = None
    member: Optional[Member] = None
    referenced_message: Optional["Message"] = None
    message_reference: Optional[MessageReference] = None
    sticker_items: Optional[List[Sticker]] = None
    position: Optional[int] = None
    channel_type: Optional[int] = None
    message_snapshots: Optional[List["Message"]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Create a Message instance from a dictionary of data."""
        # Parse author if exists
        author = None
        if "author" in data:
            author = Author.from_dict(data["author"])

        # Parse mentions into Author objects
        mentions = []
        if "mentions" in data:
            for mention in data["mentions"]:
                # Remove member field from mention data before creating Author
                mention_data = {k: v for k, v in mention.items() if k != "member"}
                mentions.append(Author.from_dict(mention_data))

        # Parse attachments into Attachment objects
        attachments = []
        if "attachments" in data:
            attachments = [
                Attachment.from_dict(attachment) for attachment in data["attachments"]
            ]

        # Parse embeds into Embed objects
        embeds = []
        if "embeds" in data:
            embeds = [Embed.from_dict(embed) for embed in data["embeds"]]

        # Parse member if exists
        member = None
        if "member" in data:
            member_data = data["member"].copy()
            member_data["user"] = author  # Use the author as the member's user
            member = Member(**member_data)

        # Parse message reference if exists
        message_reference = None
        if "message_reference" in data:
            message_reference = MessageReference(**data["message_reference"])

        # Parse referenced message if exists
        referenced_message = None
        if "referenced_message" in data and data["referenced_message"]:
            referenced_message = cls.from_dict(data["referenced_message"])

        # Parse stickers if exist
        sticker_items = None
        if "sticker_items" in data:
            sticker_items = [Sticker(**sticker) for sticker in data["sticker_items"]]

        # Parse message snapshots if exist
        message_snapshots = None
        if "message_snapshots" in data:
            # Extract the actual message data from the snapshot structure
            snapshots = []
            for snapshot in data["message_snapshots"]:
                if isinstance(snapshot, dict) and "message" in snapshot:
                    # The message data is nested inside a 'message' key
                    snapshots.append(Message.from_dict(snapshot["message"]))
                else:
                    # Direct message data
                    snapshots.append(Message.from_dict(snapshot))
            message_snapshots = snapshots if snapshots else None

        # Create message instance
        return cls(
            id=data.get("id"),
            type=data.get("type", 0),
            content=data.get("content", ""),
            channel_id=data.get("channel_id", ""),
            timestamp=data.get("timestamp", ""),
            edited_timestamp=data.get("edited_timestamp"),
            tts=data.get("tts", False),
            mention_everyone=data.get("mention_everyone", False),
            mentions=mentions,
            mention_roles=data.get("mention_roles", []),
            attachments=attachments,
            embeds=embeds,
            pinned=data.get("pinned", False),
            flags=data.get("flags", 0),
            components=data.get("components", []),
            author=author,
            guild_id=data.get("guild_id"),
            member=member,
            referenced_message=referenced_message,
            message_reference=message_reference,
            sticker_items=sticker_items,
            position=data.get("position"),
            channel_type=data.get("channel_type"),
            message_snapshots=message_snapshots,
        )

    def is_reply(self) -> bool:
        """Check if the message is a reply to another message"""
        return self.message_reference is not None

    def has_stickers(self) -> bool:
        """Check if the message contains stickers"""
        return bool(self.sticker_items)

    def is_edited(self) -> bool:
        """Check if the message has been edited"""
        return self.edited_timestamp is not None

    def is_forwarded(self) -> bool:
        """Check if the message is a forwarded message"""
        return bool(self.message_snapshots)

    def __str__(self) -> str:
        """String representation of the message"""
        base = f"Message(id={self.id}, author={self.author.username if self.author else 'Unknown'}, content='{self.content}')"
        if self.is_edited():
            base += " (edited)"
        if self.is_reply():
            base += " (reply)"
        if self.has_stickers():
            base += f" ({len(self.sticker_items)} stickers)"
        if self.is_forwarded():
            base += f" (forwarded messages:\n"
            for snapshot in self.message_snapshots:
                base += f"  - {snapshot.author.username if snapshot.author else 'Unknown'}: {snapshot.content}\n"
            base += ")"
        return base


@dataclass
class DeletedMessage:
    """
    Represents a deleted Discord message with minimal information.

    Attributes:
        id (str): The deleted message's ID
        channel_id (str): The channel where the message was
        guild_id (Optional[str]): The guild where the message was
    """

    id: str
    channel_id: str
    guild_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "DeletedMessage":
        """
        Create a DeletedMessage instance from a dictionary of data.

        Args:
            data (Dict): The raw deleted message data from Discord

        Returns:
            DeletedMessage: A new DeletedMessage instance
        """
        return cls(
            id=data["id"], channel_id=data["channel_id"], guild_id=data.get("guild_id")
        )

    def __str__(self) -> str:
        """
        Get a string representation of the deleted message.

        Returns:
            str: A string showing the message ID and channel
        """
        return f"DeletedMessage(id={self.id}, channel_id={self.channel_id})"


@dataclass
class Emoji:
    """
    Represents a Discord emoji.

    Attributes:
        name (str): The name of the emoji
        id (Optional[str]): The unique ID of the emoji (None for Unicode emojis)
    """

    name: str
    id: Optional[str]


@dataclass
class Reaction:
    """
    Represents a reaction to a Discord message.

    Attributes:
        user_id (str): The ID of the user who reacted
        type (int): The type of reaction
        message_id (str): The ID of the message reacted to
        emoji (Emoji): The emoji used in the reaction
        channel_id (str): The channel where the reaction occurred
        burst (bool): Whether this was a burst reaction
        guild_id (str): The guild where the reaction occurred
        message_author_id (Optional[str]): The ID of the message author
        member (Optional[Member]): The member who reacted
    """

    user_id: str
    type: int
    message_id: str
    emoji: Emoji
    channel_id: str
    burst: bool
    guild_id: str
    message_author_id: Optional[str] = None
    member: Optional[Member] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Reaction":
        """
        Create a Reaction instance from a dictionary of data.

        Args:
            data (Dict): The raw reaction data from Discord

        Returns:
            Reaction: A new Reaction instance
        """
        emoji = Emoji(**data["emoji"])

        member = None
        if "member" in data:
            user = Author(**data["member"]["user"])
            member_data = data["member"].copy()
            member_data["user"] = user
            member = Member(**member_data)

        return cls(
            user_id=data["user_id"],
            type=data["type"],
            message_id=data["message_id"],
            emoji=emoji,
            channel_id=data["channel_id"],
            burst=data["burst"],
            guild_id=data["guild_id"],
            message_author_id=data.get("message_author_id"),
            member=member,
        )

    def __str__(self) -> str:
        """
        Get a string representation of the reaction.

        Returns:
            str: A string showing the emoji, message, and user info
        """
        base = f"Reaction(emoji={self.emoji.name}, message_id={self.message_id}, user_id={self.user_id})"
        if self.member:
            base += f" by {self.member.user.username}"
        return base


@dataclass
class TypingEvent:
    """
    Represents a typing indicator event in Discord.

    Attributes:
        user_id (str): The ID of the user who is typing
        timestamp (int): When the typing started
        channel_id (str): The channel where the user is typing
        guild_id (str): The guild where the typing occurred
        member (Optional[Member]): The member who is typing
    """

    user_id: str
    timestamp: int
    channel_id: str
    guild_id: str
    member: Optional[Member] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "TypingEvent":
        """
        Create a TypingEvent instance from a dictionary of data.

        Args:
            data (Dict): The raw typing event data from Discord

        Returns:
            TypingEvent: A new TypingEvent instance
        """
        member = None
        if "member" in data:
            user = Author(**data["member"]["user"])
            member_data = data["member"].copy()
            member_data["user"] = user
            member = Member(**member_data)

        return cls(
            user_id=data["user_id"],
            timestamp=data["timestamp"],
            channel_id=data["channel_id"],
            guild_id=data["guild_id"],
            member=member,
        )

    def __str__(self) -> str:
        """
        Get a string representation of the typing event.

        Returns:
            str: A string showing who is typing and where
        """
        base = f"TypingEvent(user_id={self.user_id}, channel={self.channel_id})"
        if self.member:
            base += f" by {self.member.user.username}"
            if self.member.nick:
                base += f" ({self.member.nick})"
        return base
