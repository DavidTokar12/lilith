from __future__ import annotations

import logging
import sys

from pathlib import Path

import click


class Application:
    def __init__(self):
        self.log_level = logging.INFO
        self.logger = logging.getLogger("lilith")

    def setup_logging(self):
        logging.basicConfig(level=self.log_level, force=True)
        self.logger.setLevel(self.log_level)

    def run(self):
        exit_code = cli(obj=self, standalone_mode=False)
        return exit_code if exit_code is not None else 0


@click.group()
@click.option(
    "--log-level",
    default="INFO",
    help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
)
@click.pass_obj
def cli(app, log_level):
    """
    CLI application similar to Poetry, built using Click.
    """

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        click.echo(f"Invalid log level: {log_level}")
        raise click.BadParameter("Invalid log level")

    app.log_level = numeric_level
    app.setup_logging()


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def build(ctx, path):
    """Builds the project at the specified path."""
    app = ctx.obj
    build_path = Path(path).resolve()
    try:
        from lilith.console.commands.build import BuildCommand

        app.logger.info(f"Building project at {build_path}")
        BuildCommand(build_path=build_path, logger=app.logger).run()
        return 0

    except Exception as e:
        app.logger.error(f"An error occurred during build: {e}")
        click.echo(f"Error: {e}", err=True)
        return 1


def main():
    app = Application()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
