"""Command-line environment validation without exposing secret values."""

from __future__ import annotations

import sys

from pydantic import ValidationError

from company_os.settings import Settings


def main() -> int:
    try:
        settings = Settings()
    except ValidationError:
        print(
            "Company OS configuration is invalid. "
            "Check variable names and formats; values are not shown."
        )
        return 2

    problems: list[str] = []
    if settings.database_url is None:
        problems.append(
            "COMPANY_OS_DATABASE_URL is required to run the full local stack."
        )

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 2

    print(
        "Company OS configuration valid "
        f"(environment={settings.environment}, database=configured, "
        f"log_level={settings.log_level})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
