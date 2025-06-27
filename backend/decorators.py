"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from functools import wraps
from typing import List, Optional
from configs.logging_config import logger
from configs import config


def require_env_vars(*env_vars: str):
    """Decorator to check if required environment variables are set.

    Args:
        *env_vars: Variable number of environment variable names to check.

    Returns:
        The decorated function if all environment variables are set.

    Raises:
        EnvironmentError: If any of the required environment variables are not set.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            missing_vars = []
            for var in env_vars:
                if not getattr(config, var, None):
                    missing_vars.append(var)
                    logger.error(f"{var} is not set in the environment variables.")

            if missing_vars:
                raise EnvironmentError(
                    f"The following environment variables must be set to run {func.__name__}: {', '.join(missing_vars)}"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
