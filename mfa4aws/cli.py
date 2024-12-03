import logging
import sys

import click

from mfa4aws.config import initial_setup
from mfa4aws.core import validate, get_config, AWS_CREDS_PATH, get_profiles
from mfa4aws.version import show_version

logger = logging.getLogger(__name__)

class LevelFormatter(logging.Formatter):
    """Custom formatter that allows per-level formatting."""
    def __init__(self, fmt=None, datefmt=None, style='%', log_level_formats=None):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.level_formats = level_formats or {}
        self.default_format = fmt

    def format(self, record):
        fmt = self.level_formats.get(record.levelno, self.default_format)
        if self._style._fmt != fmt:
            self._style._fmt = fmt
            # Re-create the style object
            self._style = logging.PercentStyle(fmt)
        return super().format(record)

# Define log formats
simple_format = "%(message)s"
detailed_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Map log levels to formats
level_formats = {
    logging.DEBUG: detailed_format,    # DEBUG messages use detailed format
    logging.INFO: simple_format,       # INFO messages use simple format
    logging.WARNING: detailed_format,  # Other levels use detailed format
    logging.ERROR: detailed_format,
    logging.CRITICAL: detailed_format,
}

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--version", is_flag=True, help="Show logo and version information, then exit.")
@click.option("--log-level", default="INFO", help="Set log level (DEBUG, INFO, WARNING, ERROR).")
@click.pass_context
def cli(ctx, version, log_level):
    """mfa4aws: A CLI Tool for AWS MFA Authentication."""

    # Configure logging
    level = getattr(logging, log_level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = LevelFormatter(fmt=simple_format, log_level_formats=level_formats)
    handler.setFormatter(formatter)

    # Get the root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(handler)

    if version:
        show_version()
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo("No command provided. Use --help for usage information.")
        ctx.exit()

@cli.command()
@click.option("--assume-role", default=None, type=str, help="ARN of the role to assume.")
@click.option("--device", type=str, help="MFA device ARN.")
@click.option("--duration", default=43200, type=int, help="Session duration in seconds (default: 12 hours).")
@click.option("--force", is_flag=True, help="Force credential refresh even if valid.")
@click.option("--long-term-suffix", default="long-term", type=str, help="Long-term credential profile suffix.")
@click.option("--profile", default="default", type=str, help="AWS profile name.")
@click.option("--region", default=None, type=str, help="Use a specific region for the STS client.")
@click.option("--role-session-name", default=None, help="Session name when assuming a role.")
@click.option("--short-term-suffix", default=None, help="Short-term credential profile suffix.")
@click.option("--token", type=str, help="MFA token provided directly.")
@click.pass_context
def auth(
    ctx,
    assume_role,
    device,
    duration,
    force,
    long_term_suffix,
    profile,
    region,
    role_session_name,
    short_term_suffix,
    token,
):
    """Authenticate with AWS MFA and retrieve temporary credentials."""
    # Ensure credentials file exists
    logger.debug(f"Checking for credentials file at {AWS_CREDS_PATH}.")
    if not AWS_CREDS_PATH.exists():
        logger.error(f"Credentials file not found at {AWS_CREDS_PATH}.")
        if click.confirm("Would you like to create it?", default=True):
            AWS_CREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
            AWS_CREDS_PATH.touch()
            initial_setup(AWS_CREDS_PATH)
        else:
            logger.debug("User chose not to create credentials file.")
            click.echo("Exiting.")
            return

    config = get_config(AWS_CREDS_PATH)

    validate(
        assume_role,
        config,
        device,
        duration,
        force,
        long_term_suffix,
        profile,
        region,
        role_session_name,
        short_term_suffix,
        token,
    )

@cli.command()
def list_profiles():
    config = get_config(AWS_CREDS_PATH)
    profiles = config.sections()

    if not profiles:
        click.echo("No profiles found in the credentials file.")
        return

    click.echo(f"Available AWS profiles in {AWS_CREDS_PATH}:")
    for index, profile in enumerate(profiles, start=1):
        click.echo(f"{index}. {profile}")

    for profile in get_profiles():
        click.echo(profile)

if __name__ == "__main__":
    cli()
