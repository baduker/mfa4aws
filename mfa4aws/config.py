from getpass import getpass
from configparser import ConfigParser
from mfa4aws.util import log_error_and_exit, prompter


def initial_setup(logger, config_path):
    """Initial setup for AWS credentials."""
    console_input = prompter()
    profile_name = console_input("Profile name (default: 'default'): ") or "default"
    profile_name = f"{profile_name}-long-term"

    aws_access_key_id = getpass("aws_access_key_id: ")
    if not aws_access_key_id:
        log_error_and_exit(logger, "You must supply aws_access_key_id.")

    aws_secret_access_key = getpass("aws_secret_access_key: ")
    if not aws_secret_access_key:
        log_error_and_exit(logger, "You must supply aws_secret_access_key.")

    new_config = ConfigParser()
    new_config.add_section(profile_name)
    new_config.set(profile_name, "aws_access_key_id", aws_access_key_id)
    new_config.set(profile_name, "aws_secret_access_key", aws_secret_access_key)

    with config_path.open("w") as config_file:
        new_config.write(config_file)
