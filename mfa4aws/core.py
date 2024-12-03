import datetime
from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, ParamValidationError

from mfa4aws.util import log_error_and_exit, prompter, validate_token, format_duration, calculate_time_left

AWS_CREDS_PATH = Path.home() / ".aws" / "credentials"


def get_config(aws_creds_path: Path) -> ConfigParser:
    """Load AWS credentials configuration."""
    config = ConfigParser()
    try:
        config.read(aws_creds_path)
    # Let's catch more specific exceptions
    except FileNotFoundError as error:
        log_error_and_exit(None, f"Error reading credentials file: {str(error)}")
    except (NoOptionError, NoSectionError) as error:
        log_error_and_exit(None, f"Error parsing credentials file: {str(error)}")
    return config


def get_profiles() -> list:
    return boto3.session.Session().available_profiles


def validate(
    assume_role: str,
    config: ConfigParser,
    device: str,
    duration: int,
    force: bool,
    logger: object,
    long_term_suffix: str,
    profile: str,
    region: str,
    role_session_name: str,
    short_term_suffix: str,
    token: str,
):
    """Validate AWS credentials and refresh if necessary."""
    long_term_name = f"{profile}-{long_term_suffix}" if long_term_suffix else profile
    short_term_name = f"{profile}-{short_term_suffix}" if short_term_suffix else profile

    if not config.has_section(long_term_name):
        log_error_and_exit(logger, f"Long-term credentials section [{long_term_name}] is missing.")

    key_id = config.get(long_term_name, "aws_access_key_id")
    access_key = config.get(long_term_name, "aws_secret_access_key")

    if not device:
        device = config.get(long_term_name, "aws_mfa_device", fallback=None)
        if not device:
            log_error_and_exit(logger, "MFA device not provided.")

    if assume_role:
        role_arn = assume_role
    else:
        role_arn = config.get(long_term_name, "assume_role", fallback=None)

    # Check for existing valid short-term credentials
    if config.has_section(short_term_name):
        exp_str = config.get(short_term_name, "expiration", fallback=None)
        if exp_str:
            expiration = datetime.datetime.strptime(exp_str, "%Y-%m-%d %H:%M:%S")
            if expiration > datetime.datetime.utcnow() and not force:
                logger.info(f"Credentials are still valid for {calculate_time_left(expiration)} until {expiration}.")
                return

    # Generate new credentials
    get_credentials(
        short_term_name,
        key_id,
        access_key,
        device,
        duration,
        role_arn,
        role_session_name,
        token,
        config,
        region,
        logger,
    )


# core.py

def get_credentials(
    short_term_name: str,
    key_id: str,
    access_key: str,
    device: str,
    duration: int,
    assume_role: str,
    role_session_name: str,
    token: str,
    config: ConfigParser,
    region: str,
    logger,
):
    """Retrieve temporary credentials from AWS STS."""
    if not token:
        token = prompter()(f"Enter MFA token for device {device}: ")
        validate_token(token)

    logger.info("Starting AWS MFA authentication...")
    client = boto3.client(
        "sts",
        aws_access_key_id=key_id,
        aws_secret_access_key=access_key,
        region_name=region,  # Use the region parameter here
    )

    logger.info(f"Fetching temporary credentials for - Profile:  {short_term_name}, Duration: {duration} seconds {format_duration(duration)}")
    response = None
    try:
        if assume_role:
            response = client.assume_role(
                RoleArn=assume_role,
                RoleSessionName=role_session_name or "mfa-session",
                DurationSeconds=duration,
                SerialNumber=device,
                TokenCode=token,
            )
        else:
            response = client.get_session_token(
                DurationSeconds=duration,
                SerialNumber=device,
                TokenCode=token,
            )
    except (ClientError, ParamValidationError) as error:
        log_error_and_exit(logger, f"Error retrieving credentials: {str(error)}")

    credentials = response["Credentials"]
    config[short_term_name] = {
        "aws_access_key_id": credentials["AccessKeyId"],
        "aws_secret_access_key": credentials["SecretAccessKey"],
        "aws_session_token": credentials["SessionToken"],
        "expiration": credentials["Expiration"].strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(AWS_CREDS_PATH, "w") as configfile:
        config.write(configfile)

    logger.info(f"Success! Temporary credentials saved and will expire in {duration} seconds ({format_duration(duration)}) at: {credentials['Expiration']}..")
