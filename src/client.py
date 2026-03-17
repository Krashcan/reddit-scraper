from __future__ import annotations

import asyncio
import os

import httpx

from src.models import Comment, Post


class SubredditNotFoundError(Exception):
    pass


class RateLimitError(Exception):
    pass


class RedditClient:
    def __init__(self) -> None:
        self.base_url = "https://www.reddit.com"
        self.headers = {
            "User-Agent": "RedditResearcher/1.0 (personal research tool)"
        }
        self.request_delay = float(os.getenv("REQUEST_DELAY_SECONDS", "1.0"))

    async def fetch_top_posts(
        self, subreddit: str, limit: int, time_filter: str
    ) -> list[Post]:
        url = f"{self.base_url}/r/{subreddit}/top.json"
        params = {"limit": limit, "t": time_filter}

        response = await self._get_with_retry(url, params)

        children = response.json()["data"]["children"]
        if not children:
            print(f"Warning: no posts found in r/{subreddit}")
            return []

        await asyncio.sleep(self.request_delay)
        return [Post.from_reddit_json(child) for child in children]

    async def fetch_comments(
        self, subreddit: str, post_id: str, limit: int
    ) -> list[Comment]:
        url = f"{self.base_url}/r/{subreddit}/comments/{post_id}.json"
        params = {"limit": limit, "sort": "top"}

        async with httpx.AsyncClient(headers=self.headers) as http:
            response = await http.get(url, params=params)

        comment_children = response.json()[1]["data"]["children"]
        comments = [
            Comment.from_reddit_json(child)
            for child in comment_children
            if child.get("kind") == "t1"
        ]

        await asyncio.sleep(self.request_delay)
        return comments

    async def _get_with_retry(
        self, url: str, params: dict
    ) -> httpx.Response:
        max_retries = 3
        for attempt in range(max_retries):
            async with httpx.AsyncClient(headers=self.headers) as http:
                response = await http.get(url, params=params)

            if response.status_code == 404:
                raise SubredditNotFoundError(
                    f"Subreddit not found: {url}"
                )

            if response.status_code == 429:
                wait = 2**attempt
                await asyncio.sleep(wait)
                continue

            return response

        raise RateLimitError(
            f"Rate limited after {max_retries} retries: {url}"
        )
