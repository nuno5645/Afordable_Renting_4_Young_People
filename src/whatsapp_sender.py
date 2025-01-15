import pywhatkit as kit
from datetime import datetime
import time
import logging
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppSender:
    def __init__(self):
        """Initialize the WhatsApp sender"""
        self.wait_time = 15  # seconds to wait for WhatsApp Web to load

    def send_message(self, phone_number: str, message: str, now: bool = True):
        """
        Send a WhatsApp message to a specified phone number
        
        Args:
            phone_number (str): Phone number with country code (e.g., '+351912345678' or '351912345678')
            message (str): Message to be sent
            now (bool): If True, sends message immediately, otherwise waits 1 minute
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Ensure phone number starts with +
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Use sendwhatmsg_instantly instead of sendwhatmsg
            kit.sendwhatmsg_instantly(
                phone_number, 
                message,
                wait_time=self.wait_time,  # Time to wait before clicking send button
                tab_close=True  # Automatically close tab after sending
            )
            
            logger.info(f"Message sent successfully to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {phone_number}: {str(e)}")
            return False

    def send_message_to_group(self, group_id: str, message: str, now: bool = True):
        """
        Send a WhatsApp message to a group
        
        Args:
            group_id (str): Group ID from the group invite link
            message (str): Message to be sent
            now (bool): If True, sends message immediately, otherwise waits 1 minute
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # If message contains URL, handle it specially
            if 'http' in message:
                # Split into text and URL parts
                parts = message.split('http')
                text_part = parts[0].strip()
                url_part = 'http' + parts[1].strip()
                
                # Send text part first if it exists
                if text_part:
                    kit.sendwhatmsg_to_group_instantly(
                        group_id,
                        text_part,
                        wait_time=self.wait_time,
                        tab_close=False
                    )
                    time.sleep(2)
                
                # Format URL for WhatsApp web API
                formatted_url = url_part.replace('/', '%2F').replace(':', '%3A').replace(',', '%2C')
                formatted_url = formatted_url.replace('-', '%2D').replace('_', '%5F').replace(' ', '%20')
                
                # Send URL part
                kit.sendwhatmsg_to_group_instantly(
                    group_id,
                    formatted_url,
                    wait_time=self.wait_time,
                    tab_close=True
                )
            else:
                # If no URL, send as normal
                kit.sendwhatmsg_to_group_instantly(
                    group_id,
                    message,
                    wait_time=self.wait_time,
                    tab_close=True
                )
            
            logger.info(f"Message sent successfully to group {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to group {group_id}: {str(e)}")
            return False 

if __name__ == "__main__":
    def main():
        sender = WhatsAppSender()
        
        group_id = "ByBvbZbZImiIGrL8nlpvQX"
        url = "https://www.idealista.pt/arrendar-casas/amadora/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc"
        
        # Send the message and URL separately
        group_message = f"Hello group! This is a test message.\n{url}"
        
        print("Sending message to group...")
        sender.send_message_to_group(group_id, group_message)

    main() 