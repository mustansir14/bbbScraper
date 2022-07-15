import requests

token = "5424120477:AAGmh_Pv8f80zlBW_S1TKB93DyMWTnG8udA"

def send_message(message):

    chat_ids = [1047563173, 1292951296]
    responses = []
    for chat_id in chat_ids: 
        responses.append(requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text":message}))
    return responses


if __name__ == "__main__":

    print(send_message("Hi"))