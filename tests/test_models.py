from dataclasses import fields

from src.models import Comment, Post

# --- Fixtures ---

REDDIT_POST_JSON = {
    "kind": "t3",
    "data": {
        "id": "abc123",
        "title": "I built a SaaS in 30 days",
        "selftext": "Here is my journey building a marketing tool...",
        "url": "https://www.reddit.com/r/SideProject/comments/abc123/i_built_a_saas/",
        "ups": 542,
        "subreddit": "SideProject",
        "num_comments": 87,
    },
}

REDDIT_COMMENT_JSON = {
    "kind": "t1",
    "data": {
        "id": "xyz789",
        "body": "This is really inspiring, great work!",
        "ups": 34,
        "link_id": "t3_abc123",
    },
}


# --- Post dataclass field tests ---


class TestPostFields:
    def test_post_has_id_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "id" in field_names

    def test_post_has_title_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "title" in field_names

    def test_post_has_body_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "body" in field_names

    def test_post_has_url_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "url" in field_names

    def test_post_has_upvotes_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "upvotes" in field_names

    def test_post_has_subreddit_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "subreddit" in field_names

    def test_post_has_num_comments_field(self):
        field_names = {f.name for f in fields(Post)}
        assert "num_comments" in field_names


# --- Comment dataclass field tests ---


class TestCommentFields:
    def test_comment_has_id_field(self):
        field_names = {f.name for f in fields(Comment)}
        assert "id" in field_names

    def test_comment_has_body_field(self):
        field_names = {f.name for f in fields(Comment)}
        assert "body" in field_names

    def test_comment_has_upvotes_field(self):
        field_names = {f.name for f in fields(Comment)}
        assert "upvotes" in field_names

    def test_comment_has_post_id_field(self):
        field_names = {f.name for f in fields(Comment)}
        assert "post_id" in field_names


# --- Post.from_reddit_json tests ---


class TestPostFromRedditJson:
    def test_parses_id(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert post.id == "abc123"

    def test_parses_title(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert post.title == "I built a SaaS in 30 days"

    def test_parses_body(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert post.body == "Here is my journey building a marketing tool..."

    def test_parses_url(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert (
            post.url
            == "https://www.reddit.com/r/SideProject/comments/abc123/i_built_a_saas/"
        )

    def test_parses_upvotes(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert post.upvotes == 542

    def test_parses_subreddit(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert post.subreddit == "SideProject"

    def test_parses_num_comments(self):
        post = Post.from_reddit_json(REDDIT_POST_JSON)
        assert post.num_comments == 87


# --- Comment.from_reddit_json tests ---


class TestCommentFromRedditJson:
    def test_parses_id(self):
        comment = Comment.from_reddit_json(REDDIT_COMMENT_JSON)
        assert comment.id == "xyz789"

    def test_parses_body(self):
        comment = Comment.from_reddit_json(REDDIT_COMMENT_JSON)
        assert comment.body == "This is really inspiring, great work!"

    def test_parses_upvotes(self):
        comment = Comment.from_reddit_json(REDDIT_COMMENT_JSON)
        assert comment.upvotes == 34

    def test_parses_post_id(self):
        comment = Comment.from_reddit_json(REDDIT_COMMENT_JSON)
        assert comment.post_id == "abc123"


# --- Edge cases for Post.from_reddit_json ---


class TestPostFromRedditJsonEdgeCases:
    def test_empty_selftext_sets_body_to_empty(self):
        data = {
            "kind": "t3",
            "data": {**REDDIT_POST_JSON["data"], "selftext": ""},
        }
        post = Post.from_reddit_json(data)
        assert post.body == ""

    def test_removed_selftext_sets_body_to_empty(self):
        data = {
            "kind": "t3",
            "data": {**REDDIT_POST_JSON["data"], "selftext": "[removed]"},
        }
        post = Post.from_reddit_json(data)
        assert post.body == ""

    def test_absent_selftext_defaults_body_to_empty(self):
        post_data = {
            k: v for k, v in REDDIT_POST_JSON["data"].items() if k != "selftext"
        }
        data = {"kind": "t3", "data": post_data}
        post = Post.from_reddit_json(data)
        assert post.body == ""
