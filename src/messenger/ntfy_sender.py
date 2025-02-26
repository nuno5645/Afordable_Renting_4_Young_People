import subprocess
import logging

class NtfySender:
    """
    A class to send notifications via ntfy.sh
    """
    def __init__(self, topic="Casas", logger=None):
        """
        Initialize the ntfy.sh sender
        
        Args:
            topic (str): The ntfy.sh topic to send notifications to
            logger: Optional logger instance
        """
        self.topic = topic
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info(f"[NTFY] Initialized ntfy.sh sender with topic: {topic}")
        
    def send_notification(self, message, title=None, priority=None, tags=None, click=None, actions=None):
        """
        Send a notification to ntfy.sh
        
        Args:
            message (str): The message to send
            title (str, optional): The title of the notification
            priority (str, optional): Priority level (min, low, default, high, urgent)
            tags (list, optional): List of emoji tags to include
            click (str, optional): URL to open when notification is clicked
            actions (list, optional): List of action buttons to add to notification
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        try:
            # Build the curl command
            cmd = ["curl", "-d", message]
            
            # Add optional headers if provided
            if title:
                cmd.extend(["-H", f"Title: {title}"])
            if priority:
                cmd.extend(["-H", f"Priority: {priority}"])
            if tags:
                tags_str = ",".join(tags)
                cmd.extend(["-H", f"Tags: {tags_str}"])
            if click:
                cmd.extend(["-H", f"Click: {click}"])
            if actions:
                for action in actions:
                    cmd.extend(["-H", f"Actions: {action}"])
                
            # Add the ntfy.sh URL with topic
            cmd.append(f"ntfy.sh/{self.topic}")
            
            # Execute the command
            self.logger.debug(f"[NTFY] Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"[NTFY] Notification sent successfully to {self.topic}")
                return True
            else:
                self.logger.error(f"[NTFY] Failed to send notification: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"[NTFY] Error sending notification: {str(e)}", exc_info=True)
            return False

# Simple test function
def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    sender = NtfySender(logger=logger)
    sender.send_notification(
        message="Test notification from house scraper",
        title="House Scraper Test",
        priority="default",
        tags=["house", "bell"],
        click="https://example.com/test-house",
        actions=["view, View Property, https://example.com/test-house"]
    )

if __name__ == "__main__":
    main() 