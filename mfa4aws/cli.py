import logging

import click

from mfa4aws.config import initial_setup
from mfa4aws.core import validate, get_config, AWS_CREDS_PATH, get_profiles
from mfa4aws.version import show_version

logger = logging.getLogger("mfa4aws")

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show logo and version information, then exit.")
@click.option("--log-level", default="INFO", help="Set log level (DEBUG, INFO, WARNING, ERROR).")
@click.pass_context
def cli(ctx, version, log_level):
    """MFA4AWS: A CLI Tool for AWS MFA Authentication."""
    if version:
        show_version()
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo("No command provided. Use --help for usage information.")
        ctx.exit()

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s - %(message)s")
    logger.setLevel(level)


@cli.command()
@click.option("--assume-role",default=None, type=str, help="ARN of the role to assume.")
@click.option("--device", type=str, help="MFA device ARN.")
@click.option("--duration", default=43200, type=int, help="Session duration in seconds (default: 12 hours).")
@click.option("--force", is_flag=True, type=bool, help="Force credential refresh even if valid.")
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

@click.command()
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

cli.add_command(list_profiles)

if __name__ == "__main__":
    cli()
