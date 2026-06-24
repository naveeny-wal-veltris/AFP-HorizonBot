import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from src.services.logger.logger import log_mesg
from flask import jsonify
import os
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Load environment variables from the .env file
load_dotenv()

def get_conn():
    """
    Establishes and returns a connection to a PostgreSQL database hosted on AWS.
    """
    try:
        # Access the values from environment variables
        host = os.getenv('host')
        username = os.getenv('username')
        password = os.getenv('password')
        db_name = os.getenv('db_name')
        db_port = os.getenv('db_port', 5432)  # Default PostgreSQL port

        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=host,
            user=username,
            password=password,
            dbname=db_name,
            port=db_port
        )
        return connection

    except Exception as e:
        log_mesg(mesg=str(e), type="error")
        return e
    
def collect_user_details(conn, data):
    try:
        email = data["email"]
        full_name = data["full_name"]
        phone_no = data["phone_no"]
        cursor = conn.cursor()

        # Get the current time in UTC
        utc_time = datetime.now(timezone.utc)

        # Fetch the lead source ID for "Website"
        lead_source_query = "SELECT id FROM lead_sources WHERE source = 'Chatbot';"
        cursor.execute(lead_source_query)
        lead_source_id = cursor.fetchone()
        if not lead_source_id:
            raise ValueError("Lead source 'Chatbot' not found in the lead_sources table")
        lead_source_id = lead_source_id[0]

        # Insert data into the leads table with the lead_source_id
        start_time = time.time()
        status = "New"
        lead_type = "External"
        created_by = 1
        escaped_full_name = full_name.replace("'", "''")
        stm = f"""
            INSERT INTO leads (email, full_name, phone_no, created_at, updated_at, lead_source_id, status, lead_type, created_by)
            VALUES ('{email}', '{escaped_full_name}', '{phone_no}', '{utc_time}', '{utc_time}', {lead_source_id}, '{status}', '{lead_type}', {created_by})
            RETURNING id;
            """
        cursor.execute(stm)
        last_inserted_id = cursor.fetchone()[0]
        conn.commit()

        log_mesg(mesg="Time taken to insert into leads table: " + str(time.time() - start_time))
        log_mesg(mesg="Data added to the leads table")

        # Additional logic: Check for duplicate records
        check_query = f"""
            SELECT COUNT(*) FROM leads
            WHERE email = '{email}' and phone_no = '{phone_no}';
        """
        cursor.execute(check_query)
        count = cursor.fetchone()[0]

        # Get the current time in UTC
        utc_time = datetime.now(timezone.utc)

        # If count > 1, update `deleted_by` and `deleted_at`
        if count > 1:
            update_query = f"""
                UPDATE leads
                SET deleted_by = 1, deleted_at = '{utc_time}'
                WHERE id = {last_inserted_id};
            """
            cursor.execute(update_query)
            conn.commit()

        # Prepare response
        data = jsonify({
            "message": "Thank you for providing your information. Our team will use these details to assist you further if necessary.",
            "nextApiUrl": "",
            "responseCards": [
                {
                    "buttons": [
                        {"text": "AFP Services", "value": "AFP Services"},
                        {"text": "Why AFP?", "value": "Why AFP?"},
                        {"text": "What Does AFP Do?", "value": "What Does AFP Do?"},
                        {"text": "AFP Contact Details", "value": "Contact details"}
                    ],
                    "imageUrl": "",
                    "readMore": "",
                    "title": "Type in your query, or choose from any of the quick links below"
                }
            ],
            "sessionAttributes": {},
            "errors":[]
        })
        return data
    except Exception as e:
        log_mesg(mesg=str(e), type="error")
        conn.rollback()  # Rollback in case of error
        return {"error": str(e)}

