import json
import time
import os
import random
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
google_api_key = os.getenv('GOOGLE_API_KEY')

last_message_id = None
bot_user_id = None

# List of inappropriate words
inappropriate_words = ["inappropriate word 1", "inappropriate word 2", "nonsense"]

def log_message(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def is_appropriate(response_text):
    """
    Checks if the response contains inappropriate words.
    """
    for word in inappropriate_words:
        if word in response_text:
            return False
    return True

def is_high_quality(response_text):
    """
    Checks if the response is of good quality.
    """
    # Check response length
    if len(response_text) < 10:  # If the response is less than 10 characters
        return False
    # Check for unrelated keywords
    unrelated_keywords = ["I don't know", "I don't understand", "nonsense"]
    for keyword in unrelated_keywords:
        if keyword in response_text:
            return False
    return True

def trim_response(response_text, max_length=200):
    """
    Trims the response to a specified maximum length.
    """
    if len(response_text) > max_length:
        return response_text[:max_length] + "..."  # Shorten the response and add "..."
    return response_text

def generate_reply(prompt, google_api_key, use_google_ai=True):
    """
    Generates a reply to the user's message using Google Gemini AI or random responses.
    """
    if use_google_ai:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/YOUR_FINE_TUNED_MODEL:generateContent?key={google_api_key}'
        headers = {'Content-Type': 'application/json'}

        # Enhance the prompt
        enhanced_prompt = f"""
        You are a friendly and helpful Discord bot. Please provide a short and concise response to the following message (maximum 200 characters):
        {prompt}

        If the message is unclear or inappropriate, respond with: "I'm sorry, I can't help with that."
        """

        data = {'contents': [{'parts': [{'text': enhanced_prompt}]}]}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            response_text = response_data['candidates'][0]['content']['parts'][0]['text']

            # Check if the response is appropriate and of good quality
            if is_appropriate(response_text) and is_high_quality(response_text):
                # Limit the response length
                response_text = trim_response(response_text, max_length=200)
                response_data['candidates'][0]['content']['parts'][0]['text'] = response_text
                return response_data
            else:
                log_message("Inappropriate or low-quality response detected. It will not be sent.")
                return {"candidates": [{"content": {"parts": [{"text": "Sorry, I can't answer this question."}]}}]}
        except requests.exceptions.RequestException as e:
            log_message(f"Request failed: {e}")
            return {"candidates": [{"content": {"parts": [{"text": "Error processing the request. Please try again."}]}}]}
    else:
        # If not using Google Gemini AI, select a random response from pesan.txt
        random_message = get_random_message()
        random_message = trim_response(random_message, max_length=200)  # Limit the response length
        return {"candidates": [{"content": {"parts": [{"text": random_message}]}}]}

def get_random_message():
    """
    Selects a random message from the pesan.txt file.
    """
    try:
        with open('pesan.txt', 'r') as file:
            lines = file.readlines()
            if lines:
                return random.choice(lines).strip()
            else:
                log_message("File pesan.txt is empty.")
                return "No messages available."
    except FileNotFoundError:
        log_message("File pesan.txt not found.")
        return "File pesan.txt not found."

def send_message(channel_id, message_text, reply_to=None):
    """
    Sends a message to the Discord channel.
    """
    headers = {
        'Authorization': f'{discord_token}',
        'Content-Type': 'application/json'
    }

    payload = {'content': message_text}
    if reply_to:
        payload['message_reference'] = {'message_id': reply_to}

    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", json=payload, headers=headers)
        response.raise_for_status()

        if response.status_code == 201:
            log_message(f"Sent message: {message_text}")
        else:
            log_message(f"Failed to send message: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message(f"Request error: {e}")

def auto_reply(channel_id, read_delay, reply_delay, use_google_ai):
    """
    Auto-reply mode for new messages in the Discord channel.
    """
    global last_message_id, bot_user_id

    headers = {'Authorization': f'{discord_token}'}

    try:
        bot_info_response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        bot_info_response.raise_for_status()
        bot_user_id = bot_info_response.json().get('id')
    except requests.exceptions.RequestException as e:
        log_message(f"Failed to retrieve bot information: {e}")
        return

    while True:
        try:
            response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                messages = response.json()
                if len(messages) > 0:
                    most_recent_message = messages[0]
                    message_id = most_recent_message.get('id')
                    author_id = most_recent_message.get('author', {}).get('id')
                    message_type = most_recent_message.get('type', '')

                    if (last_message_id is None or int(message_id) > int(last_message_id)) and author_id != bot_user_id and message_type != 8:
                        user_message = most_recent_message.get('content', '')
                        log_message(f"Received message: {user_message}")

                        result = generate_reply(user_message, google_api_key, use_google_ai)
                        response_text = result['candidates'][0]['content']['parts'][0]['text'] if result else "Sorry, I can't reply to this message."

                        log_message(f"Waiting for {reply_delay} seconds before replying...")
                        time.sleep(reply_delay)
                        send_message(channel_id, response_text, reply_to=message_id)
                        last_message_id = message_id

            log_message(f"Waiting for {read_delay} seconds before checking for new messages...")
            time.sleep(read_delay)
        except requests.exceptions.RequestException as e:
            log_message(f"Request error: {e}")
            time.sleep(read_delay)

def auto_send_messages(channel_id, send_interval):
    """
    Auto-send mode for random messages in the Discord channel.
    """
    while True:
        message_text = get_random_message()
        message_text = trim_response(message_text, max_length=200)  # Limit the message length
        send_message(channel_id, message_text)
        log_message(f"Waiting {send_interval} seconds before sending the next message...")
        time.sleep(send_interval)

if __name__ == "__main__":
    use_reply = input("Do you want to use the reply feature? (y/n): ").lower() == 'y'
    
    channel_id = input("Enter the channel ID: ")
    
    if use_reply:
        use_google_ai = input("Do you want to use Google Gemini AI? (y/n): ").lower() == 'y'
        read_delay = int(input("Set the delay for reading new messages (in seconds): "))
        reply_delay = int(input("Set the delay for replying to messages (in seconds): "))

        log_message("Reply mode activated...")
        auto_reply(channel_id, read_delay, reply_delay, use_google_ai)
    else:
        send_interval = int(input("Set the interval for sending messages (in seconds): "))

        log_message("Random message sending mode activated...")
        auto_send_messages(channel_id, send_interval)
