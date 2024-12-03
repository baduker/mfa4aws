import sys
import datetime


def log_error_and_exit(logger, message) -> None:
    """Log an error and exit."""
    if logger:
        logger.error(message)
    else:
        print(message, file=sys.stderr)
    sys.exit(1)


def prompter():
    """Return an input function."""
    return input


def format_duration(seconds: int, long_format: bool = False) -> str:
    """Format seconds into a human-readable duration."""
    if long_format:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    # Just show the hours and minutes
    hours, minutes = divmod(seconds, 3600)
    return f"{hours}h {minutes}m"


def calculate_time_left(expiration: datetime) -> str:
    """Calculate the time left until expiration."""
    now = datetime.datetime.now()
    time_left = expiration - now
    return format_duration(int(time_left.total_seconds()), long_format=True)


def validate_token(token: str) -> None:
    """Validate the MFA token."""
    # Token must be 6 digits and can't be empty
    if token.isdigit() or len(token) != 6:
        log_error_and_exit(None, "Invalid MFA token. Must be 6 digits.")
