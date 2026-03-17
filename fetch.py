from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import date

from dotenv import load_dotenv

from src.client import RedditClient, SubredditNotFoundError
from src.formatter import Formatter
from src.models import Post


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Fetch top Reddit posts and comments for research"
    )
    parser.add_argument(
        "--subreddits",
        nargs="+",
        required=True,
        help="One or more subreddit names",
    )
    parser.add_argument(
        "--niche",
        default="general",
        help="Label for the output file and report header (default: general)",
    )
    parser.add_argument(
        "--time-filter",
        default=os.getenv("DEFAULT_TIME_FILTER", "month"),
        choices=["hour", "day", "week", "month", "year", "all"],
        help="Time filter for top posts (default: month)",
    )
    parser.add_argument(
        "--post-limit",
        type=int,
        default=int(os.getenv("DEFAULT_POST_LIMIT", "50")),
        help="Posts per subreddit, max 100 (default: 50)",
    )
    parser.add_argument(
        "--comments-per-post",
        type=int,
        default=int(os.getenv("DEFAULT_COMMENTS_PER_POST", "10")),
        help="Top comments per post (default: 10)",
    )
    parser.add_argument(
        "--output",
        default="dumps/",
        help="Output directory (default: dumps/)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each post title as it is fetched",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch posts only, skip comments, print counts, no file written",
    )

    args = parser.parse_args(argv)

    if args.post_limit > 100:
        parser.error("--post-limit cannot exceed 100")

    return args


async def main(
    subreddits: list[str],
    niche: str,
    time_filter: str,
    post_limit: int,
    comments_per_post: int,
    output_dir: str,
    verbose: bool,
    dry_run: bool,
) -> None:
    client = RedditClient()
    formatter = Formatter()

    subreddit_data: dict[str, list[Post]] = {}
    all_comments: dict[str, list] = {}

    for subreddit in subreddits:
        try:
            posts = await client.fetch_top_posts(
                subreddit, limit=post_limit, time_filter=time_filter
            )
        except SubredditNotFoundError:
            print(f"Warning: r/{subreddit} not found, skipping")
            continue

        if not posts:
            continue

        if verbose:
            for post in posts:
                print(post.title)

        subreddit_data[subreddit] = posts

        if dry_run:
            print(f"r/{subreddit}: {len(posts)} posts")
            continue

        for post in posts:
            comments = await client.fetch_comments(
                subreddit, post.id, limit=comments_per_post
            )
            all_comments[post.id] = comments

    if not subreddit_data:
        print("Error: all subreddits failed — no data fetched", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        return

    total_posts = sum(len(posts) for posts in subreddit_data.values())
    meta = {
        "niche": niche,
        "date": date.today().isoformat(),
        "subreddits": list(subreddit_data.keys()),
        "post_count": total_posts,
    }

    markdown = formatter.to_markdown(subreddit_data, all_comments, meta)
    filepath = formatter.save(markdown, output_dir, niche)
    print(filepath)


def cli() -> None:
    args = parse_args()
    asyncio.run(
        main(
            subreddits=args.subreddits,
            niche=args.niche,
            time_filter=args.time_filter,
            post_limit=args.post_limit,
            comments_per_post=args.comments_per_post,
            output_dir=args.output,
            verbose=args.verbose,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    cli()
