#!/usr/bin/env python
# coding: utf-8

import logging
from src.messenger.ntfy_sender import NtfySender
from config.settings import NTFY_TOPIC
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_notification():
    """Test sending a notification via ntfy.sh"""
    try:
        logger.info("Initializing ntfy.sh sender...")
        sender = NtfySender(topic=NTFY_TOPIC, logger=logger)
        
        # Test notification
        logger.info(f"Sending test notification to topic: {NTFY_TOPIC}")
        result = sender.send_notification(
            message="This is a test notification from the house scraper",
            title="House Scraper Test",
            priority="default",
            tags=["house", "test"]
        )
        
        if result:
            logger.info("Test notification sent successfully!")
        else:
            logger.error("Failed to send test notification")
            
        # Test affordable house notification with improved format
        logger.info("Sending affordable house test notification with improved format and clickable URL")
        
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Property URL
        property_url = "https://example.com/test-house"
        
        # Create a well-formatted message with clickable URL
        message = (
            f"💰 *800€* - Affordable House!\n\n"
            f"🏠 *Beautiful Apartment*\n"
            f"📍 Lisbon, Arroios\n"
            f"🛏️ 2 bedroom(s)\n"
            f"📐 75m²\n"
            f"🏢 Floor: 3\n\n"
            f"📝 Modern apartment with balcony, fully furnished, close to metro station and amenities...\n\n"
            f"🔎 *Source:* Test Scraper\n"
            f"⏱️ Found: {current_time}\n\n"
            f"🔗 *View Property:*\n"
            f"{property_url}"
        )
        
        # Create view action button
        view_action = f"view, View Property, {property_url}"
        
        result = sender.send_notification(
            message=message,
            title="€800 | Beautiful Apartment",
            priority="high",
            tags=["house", "money", "bell"],
            click=property_url,  # Make the entire notification clickable
            actions=[view_action]  # Add a view button
        )
        
        if result:
            logger.info("Affordable house notification with clickable URL sent successfully!")
        else:
            logger.error("Failed to send affordable house notification")
            
    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_notification() 