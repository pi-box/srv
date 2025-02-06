import os
from pyrogram import Client

def main():
    # Define the session file name
    SESSION_FILE = "telegram"

    try:
        # Check if the session file exists & correct
        client = Client(SESSION_FILE)
        client.start()
        print("Authentication successful! Session file exists.")
    
    except Exception as e:
        print("Session file not found or invalid. Setting up a new session...")
        
        # Get API credentials from the user
        api_id = int(input("Enter your Telegram API ID: "))  # Ensure integer input
        api_hash = input("Enter your Telegram API Hash: ").strip()
        
        # Initialize the Telegram client
        client = Client(SESSION_FILE, api_id=api_id, api_hash=api_hash)
        client.start()
        print("Authentication successful! Session file created.")

if __name__ == "__main__":
    main()
