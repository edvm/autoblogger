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

import argparse

from apps.blogger import get_blogger_app
from configs.logging_config import logger
from core.state import WorkflowState

"""Command-line interface for the Autoblogger application.

This module provides a CLI to generate blog posts based on a user-provided topic.
It utilizes the `argparse` module to handle command-line arguments.

Example:
    To generate a blog post about "Artificial Intelligence":
        $ uv run python cli.py "Artificial Intelligence"

    To see help:
        $ uv run python cli.py --help
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autoblogger CLI")
    parser.add_argument("topic", nargs="?", help="The topic for the blog post.")

    # Search configuration arguments
    parser.add_argument(
        "--search-depth",
        choices=["basic", "advanced"],
        default="basic",
        help="Depth of search (default: basic)",
    )
    parser.add_argument(
        "--search-topic",
        choices=["general", "news", "finance"],
        default="general",
        help="Search topic category (default: general)",
    )
    parser.add_argument(
        "--time-range",
        choices=["day", "week", "month", "year"],
        default="month",
        help="Time range for results (default: month)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days when time range is custom (default: 7)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of results to return (default: 5)",
    )
    parser.add_argument(
        "--include-domains", nargs="*", help="Domains to include in search"
    )
    parser.add_argument(
        "--exclude-domains", nargs="*", help="Domains to exclude from search"
    )
    parser.add_argument(
        "--include-answer",
        action="store_true",
        help="Include direct answers in search results",
    )
    parser.add_argument(
        "--include-raw-content",
        action="store_true",
        help="Include raw content in search results",
    )
    parser.add_argument(
        "--include-images", action="store_true", help="Include images in search results"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Request timeout in seconds (default: 60)",
    )

    args = parser.parse_args()

    if args.topic:
        initial_state: WorkflowState = WorkflowState(initial_topic=args.topic)
        blogger_app = get_blogger_app(
            search_depth=args.search_depth,
            topic=args.search_topic,
            time_range=args.time_range,
            days=args.days,
            max_results=args.max_results,
            include_domains=args.include_domains,
            exclude_domains=args.exclude_domains,
            include_answer=args.include_answer,
            include_raw_content=args.include_raw_content,
            include_images=args.include_images,
            timeout=args.timeout,
        )
        final_state: WorkflowState = blogger_app.generate_blog_post(initial_state)
        print(final_state.final_content)
        exit(0)
    else:
        parser.print_usage()
        logger.error("No topic provided.")
        print("\n")
        logger.info("Please provide a topic to generate a blog post.")
        logger.info("Example usage: uv run python cli.py 'Your Blog Topic Here'")
        logger.info("If you need help, run: uv run python cli.py --help")
        exit(1)
