import datetime
import logging
import sys

from tabulate import tabulate

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

def format_config_output(profiles):
    """Format the AWS configuration and credentials for display using tabulate."""
    rows = []

    for prof_name, prof_data in profiles.items():
        # Profile
        rows.append([
            "profile",
            prof_name,
            "None",
            "None",
        ])

        # Access Key
        access_key = prof_data.get('access_key')
        access_key_display = redact_value(access_key) if access_key else "<not set>"
        source_access_key = prof_data['source'].get('access_key') or "None"
        rows.append([
            "access_key",
            access_key_display,
            source_access_key,
            source_access_key
        ])

        # Secret Key
        secret_key = prof_data.get('secret_key')
        secret_key_display = redact_value(secret_key) if secret_key else "<not set>"
        source_secret_key = prof_data['source'].get('secret_key') or "None"
        rows.append([
            "secret_key",
            secret_key_display,
            source_secret_key,
            source_secret_key
        ])

        # Region
        region = prof_data.get('region') or "<not set>"
        source_region = prof_data['source'].get('region') or "None"
        rows.append([
            "region",
            region,
            source_region,
            source_region
        ])

    table = tabulate(
        rows,
        headers=["Name", "Value", "Type", "Location"],
        tablefmt="plain"
    )
    return table

def redact_value(value: str) -> str:
    """
    Redact all but the first and last 4 characters of a value
    and ensure the result is at most 20 characters long.
    """
    if not value:
        return value

    # Ensure value is a string
    value = str(value)
    length = len(value)

    # Truncate the value to a maximum of 20 characters
    if length > 20:
        value = value[:20]
        length = 20

    if length <= 8:
        # Not enough characters to redact; return value as is
        return value
    else:
        # Redact all but the first and last 4 characters
        num_redact = length - 8  # Number of characters to redact

        # Ensure num_redact is non-negative
        if num_redact < 0:
            num_redact = 0

        redacted_middle = '*' * num_redact
        redacted_value = value[:4] + redacted_middle + value[-4:]
        return redacted_value

