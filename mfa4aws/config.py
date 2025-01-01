import logging
import sys
from configparser import ConfigParser
from getpass import getpass

from mfa4aws.util import prompter

logger = logging.getLogger(__name__)

def initial_setup(config_path):
    """Initial setup for AWS credentials."""
    console_input = prompter()
    profile_name = console_input("Profile name (default: 'default'): ") or "default"
    profile_name = f"{profile_name}-long-term"

    aws_access_key_id = getpass("aws_access_key_id: ")
    if not aws_access_key_id:
        logger.exception("You must supply aws_access_key_id.")
        sys.exit(1)

    aws_secret_access_key = getpass("aws_secret_access_key: ")
    if not aws_secret_access_key:
        logger.exception("You must supply aws_secret_access_key.")
        sys.exit(1)

    new_config = ConfigParser()
    new_config.add_section(profile_name)
    new_config.set(profile_name, "aws_access_key_id", aws_access_key_id)
    new_config.set(profile_name, "aws_secret_access_key", aws_secret_access_key)

    with config_path.open("w") as config_file:
        new_config.write(config_file)
