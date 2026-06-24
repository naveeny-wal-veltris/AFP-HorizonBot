from flask import Flask, request, jsonify
import boto3
import uuid
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Load environment variables from the .env file
load_dotenv()

# Access the values
botId = os.getenv('botId')
botAliasId = os.getenv('botAliasId')
localeId = os.getenv('localeId')
track_userinput_response = os.getenv('track_userinput_response')

# Initialize the Lex client
client = boto3.client('lexv2-runtime', region_name='us-east-1')

def chat_response(user_input, conn):
    # Generate a unique session ID
    session_id = str(uuid.uuid4())

    try:
        # Send the user input to the Lex bot
        response = client.recognize_text(
            botId = botId,  
            botAliasId = botAliasId,  
            localeId = localeId,  
            sessionId = session_id,  
            text = user_input  
        )

        message = ""
        response_cards = []
        read_more_url = ""
        go_back_button = None

        # Process the response from Lex
        for msg in response.get('messages', []):
            if msg['contentType'] == 'PlainText':
                message += msg['content'] + " "
            elif msg['contentType'] == 'ImageResponseCard':
                # Check if this card has the "Go Back" title
                if msg['imageResponseCard'].get('title') != 'Go Back':
                    # Append other response cards
                    image_response_card = {
                        'title': msg['imageResponseCard'].get('title', ''),
                        'imageUrl': msg['imageResponseCard'].get('imageUrl', ''),
                        'buttons': msg['imageResponseCard'].get('buttons', [])
                    }
                    response_cards.append(image_response_card)
                else:
                    # Extract the "Go Back" button but do not add the card
                    go_back_button = msg['imageResponseCard']['buttons'][0]
            elif msg['contentType'] == 'CustomPayload':
                # Extract the 'readMore' URL if it exists
                custom_payload = msg.get('content', {})
                custom_payload = json.loads(custom_payload)
                if custom_payload != "" and custom_payload.get('readMore', '') == '':
                    if track_userinput_response == "True":
                        # Insert question and response JSON into the PostgreSQL table
                        insert_chatbot_qa(conn=conn, user_input=user_input, response_json=custom_payload)
                    return custom_payload
                else:
                    read_more_url = custom_payload.get('readMore', '')

        # Ensure the 'readMore' URL is added to the response card
        if response_cards:
            response_cards[-1]['readMore'] = read_more_url

        # Add the "Go Back" button to the first response card
        if go_back_button:
            response_cards[0]['buttons'].append(go_back_button)

        # Prepare the final response JSON
        response_json = {
            'message': message.strip(),
            'responseCards': response_cards,
            'sessionAttributes': response.get('sessionAttributes', {}),
            'nextApiUrl': '',
            "errors": []
        }

        if track_userinput_response == "True":
            # Insert question and response JSON into the PostgreSQL table
            insert_chatbot_qa(conn=conn, user_input=user_input, response_json=response_json)

        # Return the processed response JSON
        return jsonify(response_json)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def insert_chatbot_qa(conn, user_input, response_json):
    try:
        cursor = conn.cursor()
        # Get the current time in UTC
        utc_time = datetime.now(timezone.utc)
        # # Convert UTC time to Central Time Zone (America/Chicago)
        # central_timezone = ZoneInfo('America/Chicago')
        # central_time = utc_time.astimezone(central_timezone)
        # # Format the datetime to exclude microseconds and timezone
        # formatted_time = central_time.strftime('%Y-%m-%d %H:%M:%S')
        # stm = f"""
        # INSERT INTO chatbot_qa (user_input, response_json, created_at)
        # VALUES ('{user_input}', '{json.dumps(response_json)}', '{formatted_time}');
        # """
        escaped_user_input = user_input.replace("'", "''")
        escaped_response_json = json.dumps(response_json, ensure_ascii=False).replace("'", "''")
        stm = f"""
            INSERT INTO chatbot_qa (user_input, response_json, created_at)
            VALUES ('{escaped_user_input}', '{escaped_response_json}', '{utc_time}');
        """
        cursor.execute(stm)
        conn.commit()
    except Exception as db_error:
        conn.rollback()
        print(f"Database Error: {db_error}")
