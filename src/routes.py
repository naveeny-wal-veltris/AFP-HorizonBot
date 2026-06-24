from flask import Blueprint
from flask import request
from flask import jsonify
import traceback
import time
from src.services.logger.logger import configure_loggers
from src.services.logger.logger import log_mesg
from src.services.validations.validate import validate_for_chat
from src.services.validations.validate import validate_for_collect_user_details
from src.services.chat.chat import chat_response
from src.services.database.database import get_conn
from src.services.database.database import collect_user_details

routes_blueprint = Blueprint('routes', __name__)

configure_loggers()

start_time = time.time()
conn = get_conn()
log_mesg(mesg="Time Taken for Connection: "+ str(time.time()-start_time))

@routes_blueprint.route('/chat', methods=['POST'])
def chat_api():
    if request.method == "POST":
        try:
            start_time = time.time()
            user_input = request.json.get('message')
            validate_for_chat(user_input=user_input)
            log_mesg(mesg="Time Taken for validating the parameters is: " + str(time.time() - start_time))
            response = chat_response(user_input=user_input, conn=conn)
            log_mesg(mesg="Time Taken for chat api is: " + str(time.time() - start_time))
            return response

        except ValueError as e:
            fe = traceback.format_exc()
            log_mesg(mesg=str(fe), type="error")
            return jsonify({"error": str(e), "formated_error": fe}), 400
        except Exception as e:
            fe = traceback.format_exc()
            log_mesg(mesg=str(fe), type="error")
            return jsonify({"error": str(e), "formated_error": fe}), 400

@routes_blueprint.route('/collect-user-details', methods=['POST'])
def collect_user_details_api():
    if request.method == "POST":
        try:
            start_time = time.time()
            user_details = request.json
            response, status_code = validate_for_collect_user_details(data=user_details)
            log_mesg(mesg="Time Taken for validating the parameters is: " + str(time.time() - start_time))
            if response["errors"] == []:
                response = collect_user_details(conn=conn, data=user_details)
                log_mesg(mesg="Time Taken for collecting user email api is: " + str(time.time() - start_time))
                return response
            return response, status_code

        except ValueError as e:
            fe = traceback.format_exc()
            log_mesg(mesg=str(fe), type="error")
            return jsonify({"error": str(e), "formated_error": fe}), 400
        except Exception as e:
            fe = traceback.format_exc()
            log_mesg(mesg=str(fe), type="error")
            return jsonify({"error": str(e), "formated_error": fe}), 400
