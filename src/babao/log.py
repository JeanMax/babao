"""TODO"""

import time

def _log(header, msg):
    print(header + time.strftime("\033[37;01m [%Y/%m/%d %H:%M:%S]\033[0m\n") + msg + "\n")

def error(msg):
    _log("\033[31;01m[ERROR]", msg)

def warning(msg):
    _log("\033[33;01m[WARNING]", msg)

def debug(msg): #TODO: something like 'if getenv("DEBUG"):' or 'if getenv("LOG_LEVEL") == "DEBUG":'
    _log("\033[35;01m[DEBUG]", msg)

def log(msg):
    _log("\033[34;01m[LOG]", msg)
