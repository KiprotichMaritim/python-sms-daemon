# A Python Daemon to Send SMSs to AfricasTalking SMS Gateway
# Author: Kiprotich, maritim <github.com/KiprotichMaritim> <linkedin..com/KiprotichMaritim>
# Repo: https://github.com/KiprotichMaritim/python-sms-daemon

import mysql.connector
import africastalking
import time
import logging
import logging.handlers

# Database configuration
host = 'localhost'
username = 'DB_USERNAME'
password = 'DB_PASSWORD'
database = 'DB_NAME'
sms_table = 'sms_queue'

# Initialize AT SDK
at_username = "sandbox"    # use 'sandbox' for development in the test environment
at_api_key = "AT_API_KEY"      # use your sandbox app API key for development in the test environment
africastalking.initialize(at_username, at_api_key)
# Initialize SMS service
at_sms = africastalking.SMS

# Setup application logging 
logging.basicConfig(filename='sms_queue.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# SMS processor
def sms_process():
    # Create database connection
    db_connection = mysql.connector.connect(host = host, user = username , password = password, database = database)
    db_connection_cursor = db_connection.cursor()
    try: 
        # Find Unprocessed SMS (Status 0)
        db_connection_cursor.execute("select id, phone_number, message from sms_queue where status = %s", (0,))
        list_of_sms = db_connection_cursor.fetchall()

        if list_of_sms:
            for sms in list_of_sms:
                sms_id = sms[0]
                # We assume the phone number is correct and well formatted e.g +254722000000
                phone_number = sms[1]
                message = sms[2]
                logging.info("SEND SMS")

                # Send to API
                at_response = at_sms.send(message, [phone_number])
                # You can do checks here and any required error handling based on AT response
                logging.info(at_response)

                # Mark the SMS as sent
                update_sql = "UPDATE sms_queue set status = 1 where id = %s"
                db_connection_cursor.execute(update_sql, (sms_id,))
                db_connection.commit()

                logging.info("SMS sent")

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        db_connection_cursor.close()
        db_connection.close()    

#Daemon functionality
def run():
    while True:
        sms_process()
        time.sleep(10) # Runs every ten seconds

if(__name__ == "__main__"):
    run()
