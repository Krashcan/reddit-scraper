import os
from unittest.mock import AsyncMock, MagicMock, patch


def _make_post_json(post_id, title, subreddit):
    return {
        "kind": "t3",
        "data": {
            "id": post_id,
            "title": title,
            "selftext": f"Body of {title}",
            "url": f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/",
            "ups": 100,
            "subreddit": subreddit,
            "num_comments": 5,
        },
    }


def _make_comment_json(comment_id, post_id):
    return {
        "kind": "t1",
        "data": {
            "id": comment_id,
            "body": f"Comment {comment_id}",
            "ups": 10,
            "link_id": f"t3_{post_id}",
        },
    }


def _make_top_response(posts_json):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"data": {"children": posts_json}}
    return resp


def _make_comments_response(post_id):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [
        {"data": {"children": []}},
        {
            "data": {
                "children": [
                    _make_comment_json(f"c{post_id}_1", post_id),
                    _make_comment_json(f"c{post_id}_2", post_id),
                ]
            }
        },
    ]
    return resp


# --- Two subreddits, 3 posts each ---

SUB1_POSTS = [
    _make_post_json("p1", "Post Alpha", "SubOne"),
    _make_post_json("p2", "Post Beta", "SubOne"),
    _make_post_json("p3", "Post Gamma", "SubOne"),
]

SUB2_POSTS = [
    _make_post_json("p4", "Post Delta", "SubTwo"),
    _make_post_json("p5", "Post Epsilon", "SubTwo"),
    _make_post_json("p6", "Post Zeta", "SubTwo"),
]


class TestEndToEnd:
    async def test_full_pipeline_creates_md_with_all_posts(self, tmp_path):
        from fetch import main

        def route_get(url, params=None):
            if "SubOne/top.json" in url:
                return _make_top_response(SUB1_POSTS)
            if "SubTwo/top.json" in url:
                return _make_top_response(SUB2_POSTS)
            # Comment requests
            for pid in ["p1", "p2", "p3", "p4", "p5", "p6"]:
                if f"comments/{pid}.json" in url:
                    return _make_comments_response(pid)
            raise ValueError(f"Unexpected URL: {url}")

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=route_get)
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("src.client.httpx.AsyncClient", return_value=mock_http):
            with patch("src.client.asyncio.sleep", new_callable=AsyncMock):
                await main(
                    subreddits=["SubOne", "SubTwo"],
                    niche="integration test",
                    time_filter="month",
                    post_limit=3,
                    comments_per_post=2,
                    output_dir=str(tmp_path),
                    verbose=False,
                    dry_run=False,
                )

        files = os.listdir(tmp_path)
        assert len(files) == 1
        assert files[0].endswith(".md")

        content = (tmp_path / files[0]).read_text()

        # All 6 post titles present
        for title in [
            "Post Alpha",
            "Post Beta",
            "Post Gamma",
            "Post Delta",
            "Post Epsilon",
            "Post Zeta",
        ]:
            assert title in content

        # Both subreddit names in header
        header = content.split("##")[0]
        assert "SubOne" in header
        assert "SubTwo" in header
