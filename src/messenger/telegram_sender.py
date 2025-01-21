from telegram import Bot
import asyncio

bot_token = '7862422966:AAEvYHJNgZOhlPmFsOmB2Ylkt8yaskjKfwU'
# Your Telegram chat ID with the bot
chat_id = '6276215332'

class TelegramSender:
    def __init__(self):
        """Initialize the Telegram sender"""
        print("Initializing Telegram bot...")
        # Initialize the bot
        self.bot = Bot(token=bot_token)
        print("Telegram bot initialized successfully")

    async def send_message(self, chat_id: str, message: str):
        """
        Send a Telegram message to a specified chat ID
        
        Args:
            chat_id (str): Telegram chat ID to send message to
            message (str): Message to be sent
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            print(f"Attempting to send message to chat {chat_id}...")
            await self.bot.send_message(chat_id=chat_id, text=message)
            print(f"Message sent successfully to chat {chat_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send message to chat {chat_id}: {str(e)}")
            return False

async def main():
    sender = TelegramSender()
    test_message = "Hello! This is a test message from the Telegram bot."
    print("Sending test message...")
    await sender.send_message(chat_id, test_message)

if __name__ == "__main__":
    asyncio.run(main())