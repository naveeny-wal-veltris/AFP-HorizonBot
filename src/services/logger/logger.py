import logging
import os
from datetime import datetime

loggers_to_configure = ["error_logger", "info_logger"]

log_date = datetime.now().strftime("%Y-%m-%d")

def configure_loggers():
    global log_date
    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        handler_exists = any(handler.name == logger_name for handler in logger.handlers)
        if not handler_exists:
            # Create a new log file for each day
            log_filename = log_date + f"_{logger_name}.log"
            log_filepath = os.path.join("src", "services", "logger", "logs", log_filename)

            # Create a file handler
            file_handler = logging.FileHandler(log_filepath)
            file_handler.setLevel(logging.INFO)  # Set the log level for the file handler

            # Create a stream handler (logs to console)
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)

            # Create a formatter
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

            # Set the formatter for the handlers
            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)

            # Add the handlers to the logger
            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

            # handler.set_name("custom_handler")
            logger.propagate = False

def log_loggers(type, mesg):
    if type == "info":
        logger = logging.getLogger("info_logger")
        if logger.level != logging.INFO:
            logger.setLevel(logging.INFO)  # Set the log level to INFO
        logger.info(logger.name + " " + mesg)
    elif type == "error":
        logger = logging.getLogger("error_logger")
        if logger.level != logging.DEBUG:
            logger.setLevel(logging.DEBUG)  # Set the log level to ERROR
        logger.error(logger.name + " " + mesg)

def log_mesg(mesg, type="info"):
    global log_date
    if datetime.now().strftime("%Y-%m-%d") != log_date:
        log_date = datetime.now().strftime("%Y-%m-%d")
        for logger_name in loggers_to_configure:
            logging.Logger.manager.loggerDict.pop(logger_name, None)
        configure_loggers()
    logger = log_loggers(type=type, mesg=mesg)
