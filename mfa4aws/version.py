import sys
from datetime import datetime

import click

from mfa4aws import __version__, __name__ as __main__

RELEASE_DATE = datetime.now().strftime("%Y-%m-%d")
ASCII_LOGO = f"""
Manage your AWS MFA credentials with ease.

███    ███ ███████  █████  ██   ██  █████  ██     ██ ███████
████  ████ ██      ██   ██ ██   ██ ██   ██ ██     ██ ██
██ ████ ██ █████   ███████ ███████ ███████ ██  █  ██ ███████
██  ██  ██ ██      ██   ██      ██ ██   ██ ██ ███ ██      ██
██      ██ ██      ██   ██      ██ ██   ██  ███ ███  ███████
v{__version__} ({RELEASE_DATE}) by baduker
"""

def show_version():
    python_version = [
        str(sys.version_info.major),
        str(sys.version_info.minor),
        str(sys.version_info.micro),
    ]
    python_version = ".".join(python_version)
    platform_info = sys.platform.capitalize()
    click.echo(ASCII_LOGO)
    click.echo(
        f"Running {__main__} on {platform_info} with Python {python_version}"
    )
