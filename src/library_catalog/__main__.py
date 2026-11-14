"""Точка входа."""

import sys

import pytest


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    return pytest.main(["tests", *args])


if __name__ == "__main__":
    sys.exit(main())
