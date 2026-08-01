#!/usr/bin/env python
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def load_development_environment(env_file: Path | None = None) -> None:
    load_dotenv(env_file or Path(__file__).with_name(".env"), override=False)


def main() -> None:
    load_development_environment()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "advanced_hello_world.settings.development")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
