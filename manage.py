from __init__ import *
# Any tuple return value in any of these modules is the shutdown signal which
# will cause the assistant to speak the output first value and stop running.

# By standard, there should be one argument to every function,
# even if it is useless.

def app_close(void = None):
    return "Shutting down. See you later!", "This is the shut down signal"

