from openai import AsyncOpenAI
from .db.database import MessageDatabase


class DiscordGPTClient:
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.model = model
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.db = MessageDatabase()

    async def setup(self) -> None:
        await self.db.init_db()

    async def generate_gpt_response(self, channel_id: int, prompt: str) -> str:
        # Get channel history
        history = await self.db.get_channel_history(channel_id)

        # Format conversation history for GPT
        messages = [
            {
                "role": "system",
                "content": "You are a superior human. Keep responses short and simple. Do not behave like a bot. ",
            }
        ]

        # Add message history as context
        for msg in reversed(history[-100:]):  # Use last 100 messages as context
            messages.append(
                {"role": "user", "content": f"{msg['author_id']}: {msg['content']}"}
            )

        # Add the current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    async def add_message_history(
        self, channel_id: int, message_id: int, author_id: int, content: str
    ):
        await self.db.add_message(
            channel_id=channel_id,
            message_id=message_id,
            author_id=author_id,
            content=content,
        )

    async def start(self):
        await self.setup()
