import click
import logging
import sys
from datetime import datetime

from mfa4aws import __version__
from mfa4aws.config import initial_setup
from mfa4aws.core import validate, get_config, AWS_CREDS_PATH

logger = logging.getLogger("mfa4aws")

RELEASE_DATE = datetime.now().strftime("%Y-%m-%d")
ASCII_LOGO = f"""
Manage your AWS MFA credentials with ease.

███    ███ ███████  █████  ██   ██  █████  ██     ██ ███████
████  ████ ██      ██   ██ ██   ██ ██   ██ ██     ██ ██
██ ████ ██ █████   ███████ ███████ ███████ ██  █  ██ ███████
██  ██  ██ ██      ██   ██      ██ ██   ██ ██ ███ ██      ██
██      ██ ██      ██   ██      ██ ██   ██  ███ ███  ███████
                                     v{__version__} ({RELEASE_DATE})
"""


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show logo and version information, then exit.")
@click.option("--log-level", default="INFO", help="Set log level (DEBUG, INFO, WARNING, ERROR).")
@click.pass_context
def cli(ctx, version, log_level):
    """MFA4AWS: A CLI Tool for AWS MFA Authentication."""
    if version:
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_info = sys.platform.capitalize()
        click.echo(ASCII_LOGO)
        click.echo(f"Running {__name__} on {platform_info} with Python {python_version}")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo("No command provided. Use --help for usage information.")
        ctx.exit()

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s - %(message)s")
    logger.setLevel(level)


@cli.command()
@click.option("--assume-role",type=str,help="ARN of the role to assume.")
@click.option("--device", type=str, help="MFA device ARN.")
@click.option("--duration", default=43200, type=int, help="Session duration in seconds (default: 12 hours).")
@click.option("--force", is_flag=True, type=bool, help="Force credential refresh even if valid.")
@click.option("--long-term-suffix", default="long-term", type=str, help="Long-term credential profile suffix.")
@click.option("--profile", default="default", type=str, help="AWS profile name.")
@click.option("--region", default=None, type=str, help="Use a specific region for the STS client.")
@click.option("--role-session-name", default=None, help="Session name when assuming a role.")
@click.option("--short-term-suffix", default=None, help="Short-term credential profile suffix.")
@click.option("--token", type=int, help="MFA token provided directly.")
def auth(
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
    logger.info("Starting AWS MFA authentication...")

    # Ensure credentials file exists
    if not AWS_CREDS_PATH.exists():
        logger.error(f"Credentials file not found at {AWS_CREDS_PATH}.")
        if click.confirm("Would you like to create it?", default=True):
            AWS_CREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
            AWS_CREDS_PATH.touch()
            initial_setup(logger, AWS_CREDS_PATH)
        else:
            click.echo("Exiting.")
            return

    config = get_config(AWS_CREDS_PATH)

    validate(
        assume_role,
        config,
        device,
        duration,
        force,
        logger,
        long_term_suffix,
        profile,
        region,
        role_session_name,
        short_term_suffix,
        token,
    )


if __name__ == "__main__":
    cli()
