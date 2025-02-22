import os
import json
import sysconfig
from pyrogram import Client

"""
Setup Script for Pi-Box

This script initializes and configures the Pi-Box system by authenticating with the Telegram API
and retrieving necessary configuration data.

Features:
- Loads or creates a configuration file (`telegram.config`).
- Authenticates the Telegram client.
- Retrieves and stores the Telegram group ID for media synchronization.

Usage:
Run this script to configure the Telegram integration before running the Pi-Box server.
"""

def get_group_id(client, group_link):
    """
    Retrieves the group ID from a given Telegram group link.
    If the chat is a preview, attempts to join the chat before retrieving the ID.
    
    Args:
        client (Client): The initialized Telegram client.
        group_link (str): The Telegram group invite link.
    
    Returns:
        int: The group ID if successful, None otherwise.
    """
    try:
        chat = client.get_chat(group_link)
        if "ChatPreview" in str(type(chat)):
            chat = client.join_chat(group_link)
        return chat.id
    except Exception as e:
        print(f"Error retrieving group ID: {e}")
        return None

def main():
    """
    Main function to authenticate with Telegram, retrieve the group ID, and store configuration data.
    """
    SESSION_FILE = "telegram"
    CLI_DIR = "" if os.name == 'nt' else sysconfig.get_path("scripts")
    CONFIG_FILE = os.path.join(CLI_DIR, "telegram.config")
    
    config_data = {}
    
    # Check if the config file exists and load it if available
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config_data = json.load(file)
    
    try:
        # Initialize client using existing session
        client = Client(SESSION_FILE)
        client.start()
        print("Authentication successful! Session file exists.")
    except Exception as e:
        print("Session file not found or invalid. Setting up a new session...")
        
        # Get API credentials from user if not in config
        api_id = config_data.get("api_id") or int(input("Enter your Telegram API ID: "))
        api_hash = config_data.get("api_hash") or input("Enter your Telegram API Hash: ").strip()
        
        # Initialize the Telegram client
        client = Client(SESSION_FILE, api_id=api_id, api_hash=api_hash)
        client.start()
        print("Authentication successful! Session file created.")
    
    # Ask for group link if not already stored
    if "group_id" not in config_data:
        group_link = input("Enter your Telegram group link (e.g., t.me/+your_group_link_here): ").strip()
        group_id = get_group_id(client, group_link)
        
        if group_id:
            config_data.update({"group_link": group_link, "group_id": group_id})
            print(f"Group ID retrieved: {group_id}")
        else:
            print("Failed to retrieve group ID.")
    
    # Save config data to file
    with open(CONFIG_FILE, "w") as file:
        json.dump(config_data, file, indent=4)
    
    print("Configuration saved successfully.")
    
if __name__ == "__main__":
    main()
