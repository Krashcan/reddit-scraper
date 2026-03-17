from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Post:
    id: str
    title: str
    body: str
    url: str
    upvotes: int
    subreddit: str
    num_comments: int

    @classmethod
    def from_reddit_json(cls, json_obj: dict) -> Post:
        data = json_obj["data"]
        selftext = data.get("selftext", "")
        if selftext == "[removed]":
            selftext = ""
        return cls(
            id=data["id"],
            title=data["title"],
            body=selftext,
            url=data["url"],
            upvotes=data["ups"],
            subreddit=data["subreddit"],
            num_comments=data["num_comments"],
        )


@dataclass
class Comment:
    id: str
    body: str
    upvotes: int
    post_id: str

    @classmethod
    def from_reddit_json(cls, json_obj: dict) -> Comment:
        data = json_obj["data"]
        link_id = data["link_id"]
        # link_id is "t3_<post_id>", strip the prefix
        post_id = link_id.split("_", 1)[1]
        return cls(
            id=data["id"],
            body=data["body"],
            upvotes=data["ups"],
            post_id=post_id,
        )
