import sys


def log_error_and_exit(logger, message):
    """Log an error and exit."""
    if logger:
        logger.error(message)
    else:
        print(message, file=sys.stderr)
    sys.exit(1)


def prompter():
    """Return an input function."""
    return input
