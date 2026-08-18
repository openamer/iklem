"""Allow `python -m iklem` to run the CLI."""

from iklem.cli import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
