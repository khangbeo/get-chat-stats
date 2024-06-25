import os
import requests
import logging
from dotenv import load_dotenv, find_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from a .env file
load_dotenv()

dotenv_path = find_dotenv()
if not dotenv_path:
    logging.error(".env file not found")
else:
    logging.info(f"Loading .env file from {dotenv_path}")
    load_dotenv(dotenv_path)

# Configuration
username = os.getenv("USER")
token = os.getenv("TOKEN")
base_url = "https://api.streamelements.com/kappa/v2"
chat_stats_url = f"{base_url}/chatstats/{username}/stats"
channel_stats_url = f"{base_url}/stats/{username}"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {str(token)}",
}

req = requests

def get_chat_stats(url):
    try:
        res = req.get(url, headers=headers)
        res.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return res.json()
    except req.exceptions.RequestException as e:
        logging.error(f"Error fetching chat stats: {e}")
        return None

def filter_user(user, excluded_users):
    return user["name"] not in excluded_users

def load_excluded_users(file_path):
    try:
        with open(file_path, 'r') as file:
            excluded_users = [line.strip() for line in file.readlines()]
        return excluded_users
    except FileNotFoundError:
        logging.error(f"Excluded users file not found: {file_path}")
        return []

def get_top_chatters(chatters, excluded_users):
    valid_chatters = [user for user in chatters if filter_user(user, excluded_users)]
    if valid_chatters:
        first_chatter = valid_chatters[0]
        name, amount = first_chatter['name'], first_chatter['amount']
        return name, amount
    return None, None

def main():
    excluded_users_file = 'excluded_users.txt'
    excluded_users = load_excluded_users(excluded_users_file)
    chat_stats = get_chat_stats(chat_stats_url)

    if chat_stats:
        logging.info(f"Chat stats response: {chat_stats}")
        
        if 'chatters' in chat_stats:
            name, amount = get_top_chatters(chat_stats['chatters'], excluded_users)
            if name and amount:
                label = f"Most interactive: {name}"
                with open('top_chatter.txt', 'w') as file:
                    file.write(label)
        else:
            logging.error("Key 'chatters' not found in the response")
    else:
        logging.error("Failed to fetch chat stats")

if __name__ == '__main__':
    main()
