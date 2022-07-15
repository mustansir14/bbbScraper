import requests

def send_message(message, bot_token, chat_ids):

    responses = []
    for chat_id in chat_ids: 
        responses.append(requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": chat_id, "text":message}))
    return responses

