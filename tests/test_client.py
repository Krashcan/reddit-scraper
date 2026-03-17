from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client import RedditClient, SubredditNotFoundError
from src.models import Post, Comment

# --- Fixture data matching Reddit's JSON shapes ---

REDDIT_TOP_JSON = {
    "data": {
        "children": [
            {
                "kind": "t3",
                "data": {
                    "id": "abc123",
                    "title": "I built a SaaS in 30 days",
                    "selftext": "Here is my journey...",
                    "url": "https://www.reddit.com/r/SideProject/comments/abc123/i_built_a_saas/",
                    "ups": 542,
                    "subreddit": "SideProject",
                    "num_comments": 87,
                },
            },
            {
                "kind": "t3",
                "data": {
                    "id": "def456",
                    "title": "How I got my first 100 users",
                    "selftext": "",
                    "url": "https://www.reddit.com/r/SideProject/comments/def456/first_100/",
                    "ups": 210,
                    "subreddit": "SideProject",
                    "num_comments": 32,
                },
            },
        ]
    }
}

REDDIT_COMMENTS_JSON = [
    {
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "id": "abc123",
                        "title": "I built a SaaS in 30 days",
                        "selftext": "Here is my journey...",
                        "url": "https://www.reddit.com/r/SideProject/comments/abc123/",
                        "ups": 542,
                        "subreddit": "SideProject",
                        "num_comments": 87,
                    },
                }
            ]
        }
    },
    {
        "data": {
            "children": [
                {
                    "kind": "t1",
                    "data": {
                        "id": "com1",
                        "body": "Great work!",
                        "ups": 34,
                        "link_id": "t3_abc123",
                    },
                },
                {
                    "kind": "t1",
                    "data": {
                        "id": "com2",
                        "body": "How did you market it?",
                        "ups": 21,
                        "link_id": "t3_abc123",
                    },
                },
            ]
        }
    },
]


# --- RedditClient initialisation ---


class TestRedditClientInit:
    def test_has_base_url(self):
        client = RedditClient()
        assert client.base_url == "https://www.reddit.com"

    def test_has_correct_user_agent(self):
        client = RedditClient()
        assert (
            client.headers["User-Agent"]
            == "RedditResearcher/1.0 (personal research tool)"
        )


# --- fetch_top_posts ---


class TestFetchTopPosts:
    @pytest.mark.asyncio
    async def test_returns_list_of_posts(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = REDDIT_TOP_JSON
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                posts = await client.fetch_top_posts(
                    "SideProject", limit=10, time_filter="month"
                )

        assert isinstance(posts, list)
        assert len(posts) == 2
        assert all(isinstance(p, Post) for p in posts)
        assert posts[0].id == "abc123"
        assert posts[1].id == "def456"

    @pytest.mark.asyncio
    async def test_calls_correct_url(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = REDDIT_TOP_JSON
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                await client.fetch_top_posts(
                    "SideProject", limit=10, time_filter="month"
                )

        mock_http_client.get.assert_called_once_with(
            "https://www.reddit.com/r/SideProject/top.json",
            params={"limit": 10, "t": "month"},
        )

    @pytest.mark.asyncio
    async def test_calls_sleep_with_request_delay(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = REDDIT_TOP_JSON
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch(
                "src.client.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                await client.fetch_top_posts(
                    "SideProject", limit=10, time_filter="month"
                )

        mock_sleep.assert_called_once_with(client.request_delay)


# --- fetch_comments ---


class TestFetchComments:
    @pytest.mark.asyncio
    async def test_returns_list_of_comments(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = REDDIT_COMMENTS_JSON
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                comments = await client.fetch_comments(
                    "SideProject", "abc123", limit=10
                )

        assert isinstance(comments, list)
        assert len(comments) == 2
        assert all(isinstance(c, Comment) for c in comments)
        assert comments[0].id == "com1"
        assert comments[1].id == "com2"

    @pytest.mark.asyncio
    async def test_calls_correct_url(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = REDDIT_COMMENTS_JSON
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                await client.fetch_comments("SideProject", "abc123", limit=10)

        mock_http_client.get.assert_called_once_with(
            "https://www.reddit.com/r/SideProject/comments/abc123.json",
            params={"limit": 10, "sort": "top"},
        )

    @pytest.mark.asyncio
    async def test_calls_sleep_with_request_delay(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = REDDIT_COMMENTS_JSON
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch(
                "src.client.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                await client.fetch_comments("SideProject", "abc123", limit=10)

        mock_sleep.assert_called_once_with(client.request_delay)


# --- Error handling ---


class TestFetchTopPostsErrors:
    @pytest.mark.asyncio
    async def test_raises_subreddit_not_found_on_404(self):
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(SubredditNotFoundError):
                    await client.fetch_top_posts(
                        "nonexistent", limit=10, time_filter="month"
                    )

    @pytest.mark.asyncio
    async def test_retries_with_backoff_on_429(self):
        mock_429 = MagicMock()
        mock_429.status_code = 429

        mock_ok = MagicMock()
        mock_ok.status_code = 200
        mock_ok.json.return_value = REDDIT_TOP_JSON
        mock_ok.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(side_effect=[mock_429, mock_429, mock_ok])
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch(
                "src.client.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                posts = await client.fetch_top_posts(
                    "SideProject", limit=10, time_filter="month"
                )

        assert len(posts) == 2
        # Backoff waits: 1s, 2s, then the final request_delay sleep
        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [1, 2, client.request_delay]

    @pytest.mark.asyncio
    async def test_raises_rate_limit_after_3_retries_on_429(self):
        mock_429 = MagicMock()
        mock_429.status_code = 429

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_429)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch(
                "src.client.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                from src.client import RateLimitError

                with pytest.raises(RateLimitError):
                    await client.fetch_top_posts(
                        "SideProject", limit=10, time_filter="month"
                    )

        # 3 backoff sleeps: 1s, 2s, 4s
        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [1, 2, 4]

    @pytest.mark.asyncio
    async def test_returns_empty_list_and_warns_on_zero_posts(self, capsys):
        empty_json = {"data": {"children": []}}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = empty_json
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        client = RedditClient()

        with patch("src.client.httpx.AsyncClient", return_value=mock_http_client):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                posts = await client.fetch_top_posts(
                    "emptysubreddit", limit=10, time_filter="month"
                )

        assert posts == []
        captured = capsys.readouterr()
        assert "emptysubreddit" in captured.out
