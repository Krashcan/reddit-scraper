"""
Live end-to-end tests that hit the real Reddit API.

These are excluded from normal test runs (CI, pre-commit, `pytest`).
Run them manually to verify the API integration still works:

    pytest -m e2e -v
"""

import pytest

from src.client import RedditClient, SubredditNotFoundError
from src.models import Comment, Post


pytestmark = pytest.mark.e2e


class TestLiveFetchTopPosts:
    async def test_returns_posts_from_python_subreddit(self):
        client = RedditClient()
        posts = await client.fetch_top_posts("python", limit=5, time_filter="month")

        assert len(posts) > 0
        assert len(posts) <= 5
        assert all(isinstance(p, Post) for p in posts)

    async def test_post_fields_are_populated(self):
        client = RedditClient()
        posts = await client.fetch_top_posts("python", limit=1, time_filter="month")

        post = posts[0]
        assert post.id
        assert post.title
        assert post.url
        assert post.subreddit.lower() == "python"
        assert isinstance(post.upvotes, int)
        assert isinstance(post.num_comments, int)

    async def test_raises_on_nonexistent_subreddit(self):
        client = RedditClient()
        with pytest.raises(SubredditNotFoundError):
            await client.fetch_top_posts(
                "thissubredditdoesnotexist9999zz", limit=1, time_filter="month"
            )


class TestLiveFetchComments:
    async def test_returns_comments_for_a_real_post(self):
        client = RedditClient()
        posts = await client.fetch_top_posts("python", limit=1, time_filter="month")
        assert len(posts) > 0

        post = posts[0]
        comments = await client.fetch_comments("python", post.id, limit=5)

        assert isinstance(comments, list)
        assert all(isinstance(c, Comment) for c in comments)

    async def test_comment_fields_are_populated(self):
        client = RedditClient()
        posts = await client.fetch_top_posts("python", limit=1, time_filter="month")
        post = posts[0]

        comments = await client.fetch_comments("python", post.id, limit=3)
        if not comments:
            pytest.skip("Post has no comments")

        comment = comments[0]
        assert comment.id
        assert comment.body
        assert comment.post_id == post.id
        assert isinstance(comment.upvotes, int)
