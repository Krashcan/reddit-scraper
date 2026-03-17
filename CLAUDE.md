# Project Instructions

<!-- Update this file with project-specific details so Claude understands your codebase. -->

<!-- Tech stack and frameworks used -->
<!--
- Python 3.11+
- httpx (async HTTP — not requests)
- python-dotenv for env var loading
- argparse for CLI
- pytest + pytest-asyncio + pytest-mock for testing
- black + ruff for formatting and linting
-->

<!-- How to build, test, and run the project -->
<!--
Install dependencies:
  pip install -r requirements.txt
  pip install -r requirements-dev.txt

Run the fetcher:
  python fetch.py --subreddits indiehackers SideProject webdev --niche "marketing for engineers"

All CLI options:
  --subreddits         One or more subreddit names (required)
  --niche              Label for the output file and report header (default: "general")
  --time-filter        hour|day|week|month|year|all (default: month)
  --post-limit         Posts per subreddit, max 100 (default: 50)
  --comments-per-post  Top comments per post (default: 10)
  --output             Output directory (default: dumps/)
  --verbose            Print each post title as it is fetched
  --dry-run            Fetch posts only, skip comments, print counts, no file written

Run tests:
  pytest

Lint and format:
  black . && ruff check .

Environment variables (copy .env.example to .env):
  REQUEST_DELAY_SECONDS=1.0
  DEFAULT_POST_LIMIT=50
  DEFAULT_COMMENTS_PER_POST=10
  DEFAULT_TIME_FILTER=month
-->

<!-- Code style and conventions -->
<!--
- Strict TDD: write the failing test first, then implement (red → green → refactor)
- No implementation code without a test that calls it first
- Mock all external HTTP calls in tests — no real network calls in the test suite
- Tests must be fast: full suite under 5 seconds
- Async functions use asyncio, entrypoint uses asyncio.run()
- Dataclasses for models (Post, Comment)
- Custom exceptions: SubredditNotFoundError, RateLimitError
- Enforce 1 request/second rate limit via asyncio.sleep between Reddit API calls
- Exponential backoff on 429: wait 1s, 2s, 4s before giving up
- Minimum test coverage: 80%
-->

<!-- Project structure overview -->
<!--
reddit-fetcher/
├── CLAUDE.md
├── BUILD_PROMPTS.md
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── fetch.py                 # CLI entrypoint
├── src/
│   ├── __init__.py
│   ├── client.py            # Reddit JSON API client
│   ├── models.py            # Post and Comment dataclasses
│   └── formatter.py         # Formats fetched data into markdown
└── tests/
    ├── __init__.py
    ├── test_client.py
    ├── test_models.py
    ├── test_formatter.py
    └── test_integration.py
-->

<!-- Any project-specific rules or constraints -->
<!--
Reddit API details:
  Base URL: https://www.reddit.com
  Posts:    /r/{subreddit}/top.json?limit={n}&t={time_filter}
  Comments: /r/{subreddit}/comments/{post_id}.json?limit={n}&sort=top
  User-Agent: RedditResearcher/1.0 (personal research tool)
  No auth required for public subreddits

Output file:
  Location: dumps/YYYY-MM-DD_{niche_slug}.md
  Niche slug: lowercase, spaces to underscores, special chars removed
  Format: markdown readable by humans and pasteable into Claude chat for analysis

Error handling:
  404 → skip subreddit, print warning, continue
  429 → exponential backoff, max 3 retries
  Empty subreddit → skip and warn
  All subreddits fail → exit with error, do not write empty file

Do NOT:
  - Make any AI or LLM API calls — this tool fetches data only
  - Use requests library — use httpx
  - Add a web server or database
  - Hardcode any values that belong in .env
  - Skip writing tests before implementation
  - Fetch more than 100 posts per subreddit
-->
