# Reddit Research Scraper

Fetches top posts and comments from Reddit subreddits and saves them as markdown files for research and analysis.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

## Usage

Basic usage with multiple subreddits:

```bash
python fetch.py --subreddits indiehackers SideProject webdev --niche "marketing for engineers"
```

All CLI options:

```bash
python fetch.py \
  --subreddits SideProject webdev \
  --niche "marketing for engineers" \
  --time-filter month \
  --post-limit 50 \
  --comments-per-post 10 \
  --output dumps/ \
  --verbose
```

Dry run (fetch posts only, skip comments, no file written):

```bash
python fetch.py --subreddits SideProject --dry-run
```

## Options

| Flag                | Description                          | Default   |
|---------------------|--------------------------------------|-----------|
| `--subreddits`      | One or more subreddit names          | required  |
| `--niche`           | Label for output file and header     | `general` |
| `--time-filter`     | `hour\|day\|week\|month\|year\|all`  | `month`   |
| `--post-limit`      | Posts per subreddit (max 100)        | `50`      |
| `--comments-per-post` | Top comments per post              | `10`      |
| `--output`          | Output directory                     | `dumps/`  |
| `--verbose`         | Print each post title as fetched     | off       |
| `--dry-run`         | Fetch posts only, print counts       | off       |

## Sample Output

Output files are saved to `dumps/YYYY-MM-DD_{niche_slug}.md`:

```markdown
# Reddit Research Dump

**Niche:** marketing for engineers
**Date:** 2026-03-17
**Subreddits:** SideProject, webdev
**Total posts:** 12

## r/SideProject

### I built a SaaS in 30 days (542 upvotes)

Here is my journey building a marketing tool...

- **34** Great work!
- **21** How did you market it?

## r/webdev

### Best frameworks for landing pages (310 upvotes)

- **45** Try Astro, it's great for static sites
```

## Note

The output markdown is designed to be pasted directly into a Claude chat for analysis and research insights.

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```
