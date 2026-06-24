from src.services.logger.logger import log_mesg
import re
from email_validator import validate_email, EmailNotValidError
import phonenumbers

def validate_for_chat(user_input):
    if user_input is not None:
        if isinstance(user_input, str):
            if user_input.strip() == "":
                log_mesg(mesg="user_input is an empty string", type="error")
                raise ValueError("user_input can't be an empty string")
        else:
            log_mesg(mesg="user_input is not of type String", type="error")
            raise ValueError("user_input should be a string")
    else:
        log_mesg(mesg="user_input Field is Missing", type="error")
        raise ValueError("user_input Field is Missing")
    
def validate_for_collect_user_details(data):
    """
    Function to validate user details including email, full name, and phone number.
    Returns a dictionary with validation status and error messages.
    """
    response = {
        "message": "",
        "nextApiUrl": "/collect-user-details",
        "responseCards": [],
        "sessionAttributes": {},
        "errors": []  # Using a list to store all error messages
    }
    
    try:
        # Email validation
        if "email" not in data.keys():
            log_mesg("Email Field is Missing", type="error")
            response["errors"].append({"field": "email", "message": "Email Field is Missing. Reenter your email"})
        elif data["email"] is None or data["email"] == "":
            log_mesg("Value for Email Field is Missing", type="error")
            response["errors"].append({"field": "email", "message": "Value for Email Field is Missing. Reenter your email"})
        elif isinstance(data["email"], str):
            if len(data["email"]) == 0:
                log_mesg("Email Field is empty", type="error")
                response["errors"].append({"field": "email", "message": "Email can't be empty. Reenter your email"})
            try:
                email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(\.[a-zA-Z]{2,})?$"
                if not re.match(email_regex, data["email"]):
                    response["errors"].append({"field": "email", "message": "Email invalid. Please validate that you have typed a correct email address"})
            except Exception as e:
                log_mesg(mesg=f"Unexpected Error: {e}", type="error")
                response["errors"].append({"field": "email", "message": "Unexpected error while validating email."})
        else:
            log_mesg("Email is not str type", type="error")
            response["errors"].append({"field": "email", "message": "Email invalid. Please validate that you have typed a correct email address"})
    except Exception as e:
        log_mesg(mesg=f"Unexpected Error: {e}", type="error")
        response["errors"].append({"field": "email", "message": "Unexpected error while validating email."})  # Added

    try:
        # Full Name validation
        if "full_name" not in data.keys():
            log_mesg("Full Name Field is Missing", type="error")
            response["errors"].append({"field": "full_name", "message": "Full Name Field is Missing. Reenter your full name"})
        elif data["full_name"] is None or data["full_name"] == "":
            log_mesg("Value for Full Name Field is Missing", type="error")
            response["errors"].append({"field": "full_name", "message": "Value for Full Name Field is Missing. Reenter your full name"})
        elif isinstance(data["full_name"], str):
            if len(data["full_name"]) == 0:
                log_mesg("Full Name Field is empty", type="error")
                response["errors"].append({"field": "full_name", "message": "Full Name can't be empty. Reenter your full name"})
            if len(data["full_name"]) > 200:
                log_mesg("Full Name exceeds maximum length", type="error")
                response["errors"].append({"field": "full_name", "message": "Only 200 maximum characters allowed"})
            if not re.match(r"^(?=.*[a-zA-Z])[a-zA-Z0-9\s´'\-,\.\(\)!Åë&]+$", data["full_name"]):
                log_mesg("Invalid Full Name Format", type="error")
                response["errors"].append({"field": "full_name", "message": "Please provide your legal full name and ensure that there are no special characters"})
        else:
            log_mesg("Full Name is not str type", type="error")
            response["errors"].append({"field": "full_name", "message": "Please provide your legal full name and ensure that there are no special characters"})
    except Exception as e:
        log_mesg(mesg=f"Unexpected Error: {e}", type="error")
        response["errors"].append({"field": "full_name", "message": "Unexpected error while validating full name."})  # Added

    try:
        # Phone Number validation
        if "phone_no" not in data.keys():
            log_mesg("Phone Number Field is Missing", type="error")
            response["errors"].append({"field": "phone_no", "message": "Phone Number Field is Missing. Reenter your phone number"})
        elif data["phone_no"] is None or data["phone_no"] == "":
            log_mesg("Value for Phone Number Field is Missing", type="error")
            response["errors"].append({"field": "phone_no", "message": "Value for Phone Number Field is Missing. Reenter your phone number"})
        elif isinstance(data["phone_no"], str):
            if len(data["phone_no"]) == 0:
                log_mesg("Phone Number Field is empty", type="error")
                response["errors"].append({"field": "phone_no", "message": "Phone Number can't be empty. Reenter your phone number"})
            try:
                parsed_number = phonenumbers.parse(data["phone_no"])
                region_code = phonenumbers.region_code_for_number(parsed_number)
                if not region_code:
                    log_mesg("Missing or Invalid Country Code in Phone Number", type="error")
                    response["errors"].append({"field": "phone_no", "message": "Invalid phone number. Please ensure that you mention the country code and number together (for example: +1-1234567890)"})
                if not phonenumbers.is_valid_number(parsed_number):
                    if not any(error["field"] == "phone_no" for error in response["errors"]):
                        log_mesg("Invalid Phone Number", type="error")
                        response["errors"].append({"field": "phone_no", "message": "Invalid phone number. Please ensure that you mention the country code and number together (for example: +1-1234567890)"})
            except phonenumbers.NumberParseException as e:
                log_mesg(mesg=f"Phone Number Parsing Error: {e}", type="error")
                response["errors"].append({"field": "phone_no", "message": "Invalid phone number. Please ensure that you mention the country code and number together (for example: +1-1234567890)"})
        else:
            log_mesg("Phone Number is not str type", type="error")
            response["errors"].append({"field": "phone_no", "message": "Invalid phone number. Please ensure that you mention the country code and number together (for example: +1-1234567890)"})
    except Exception as e:
        log_mesg(mesg=f"Unexpected Error: {e}", type="error")
        response["errors"].append({"field": "phone_no", "message": "Unexpected error while validating phone number."})  # Already added

    if response["errors"]:
        return response, 400
    else:
        return response, 200
