from __future__ import annotations

import logging
import sys
import traceback

from pathlib import Path

import click


logger = logging.getLogger("lilith")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("Lilith - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Application:

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

    logger.setLevel(numeric_level)


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path to the project root directory.",
)
@click.option(
    "--reset", is_flag=True, default=False, help="Reset the build before starting."
)
@click.pass_context
def build(ctx, path, reset):
    """Builds the project at the specified path."""

    build_path = Path(path).resolve()
    try:
        from lilith.console.commands.build import BuildCommand

        logger.info(f"Building project at {build_path}")
        BuildCommand(build_path=build_path, reset=reset).run()
        return 0

    except Exception as e:
        logger.error(f"An error occurred during build: {e}")
        logger.info(traceback.format_exc())
        return 1


def main():
    app = Application()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
