import datetime
import logging
import sys

logger = logging.getLogger(__name__)

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
    logger.debug(f"Validating MFA token: {token}")
    if token.isdigit() or len(token) != 6:
        logger.error("Invalid MFA token. Must be 6 digits.")
        sys.exit(1)
