from __future__ import annotations

import sys

from pathlib import Path

from dotenv import load_dotenv


def load_environment():
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

if __name__ == "__main__":
    load_environment()

    from lilith.console.application import main
    sys.exit(main())
